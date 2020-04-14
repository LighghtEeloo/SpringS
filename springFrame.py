import os,sys
import pickle
from random import random
from copy import deepcopy

printing = False


class Pot:
    def __init__(self, side, height, limit):
        self.side = side
        self.height = height
        self.limit = limit
    def __repr__(self):
        return f"({self.height}|{chr(self.side+64)})"
    def __eq__(self, value):
        return self.side==value.side and self.height==value.height and self.limit==value.limit
    def dropcheck(self,side):
        return self.side == side or self.side == 0
    def drill(self, side):
        self.side = side
        self.height += 1
    def isfull(self):
        return self.height >= self.limit
    def emptize(self):
        if self.height >= self.limit:
            self.height -= self.limit
            # if self.height == 0:
            #     self.side = 0
            return self.side


class Frame:
    def __init__(self, size=(4,5)):
        super().__init__()
        self.size = size
        self.board = [[Pot(0,0,4) for j in range(size[1])] for i in range(size[0])]
        for i in range(size[0]):
            for j in range(size[1]):
                if (i == 0 or i == size[0]-1) or (j == 0 or j == size[1]-1):
                    self.board[i][j].limit -= 1
                if (i == 0 or i == size[0]-1) and (j == 0 or j == size[1]-1):
                    self.board[i][j].limit -= 1
        # self.hashBoard = [[random()*2**32//1 for j in range(size[1])] for i in range(size[0])]
    def __getitem__(self, position):
        return self.board[position]
    def __eq__(self, other):
        eqBoard = True
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.board[i][j] != other.board[i][j]:
                    eqBoard = False
                    break
        return eqBoard and self.size==other.size
    def __hash__(self):
        row, col = self.size
        return (
            + sum([5*self.board[i][j].height for i in range(row) for j in range(col) if self.board[i][j].side == 1])
            + sum([-self.board[i][j].height for i in range(row) for j in range(col) if self.board[i][j].side == 2])
            # + sum([5*self.board[i][j].height * self.hashBoard[i][j] for i in range(row) for j in range(col) if self.board[i][j].side == 1])
            # + sum([-self.board[i][j].height * self.hashBoard[i][j] for i in range(row) for j in range(col) if self.board[i][j].side == 2])
        )
        return super().__hash__()
    def __repr__(self):
        strBoard = "\n"
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                strBoard += f"{self.board[i][j]}"
                strBoard += ","
            strBoard += "\n"
        return strBoard
    def sync(self, board=None):
        if board != None:
            self.board = deepcopy(board)
            return 0
        return 1
    def drop(self, x, y, side): # 玩家落子时调用
        if not self.board[x][y].dropcheck(side):
            return -1
        self.drill(x, y, side)
        self.clear()
        return 0
    def drill(self, x, y, side, pt=False): # 落子并改变所有权
        self.board[x][y].drill(side)
        if pt:
            print(f"--- drilling: ({x},{y})")
            self.output()
        if self.board[x][y].isfull():
            if self.win() != 0:
                return
            self.board[x][y].emptize()
            self.spring(x, y, side)
    def spring(self, x, y, side): # 开 枝 散 叶
        if x-1 >= 0:
            self.drill(x-1, y, side)
        if x+1 < self.size[0]:
            self.drill(x+1, y, side)
        if y-1 >= 0:
            self.drill(x, y-1, side)
        if y+1 < self.size[1]:
            self.drill(x, y+1, side)
    def clear(self):
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.board[i][j].height == 0:
                    self.board[i][j].side = 0
    def win(self) -> int:
        res = [0]*3
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                res[self.board[i][j].side] += 1
        if res[0] < self.size[0] * self.size[1] -1 and (res[1] == 0 or res[2] == 0) and sum(res) != 1:
            return 1 if res[2]==0 else 2
        return 0
    def output(self):
        bd = self.board
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                print(f"({bd[i][j].height}|{chr(bd[i][j].side+64)}),",end="")
            print()
        print()
    # def loop(self):
    #     side = 1
    #     cnt = 1
    #     for _ in range(3):
    #         for i in range(4):
    #             for j in range(5):
    #                 print(f"--- {cnt} ---")
    #                 print(f"trying: ({i},{j}) side: {chr(side+64)}")
    #                 if self.drop(i,j, side) == -1:
    #                     continue
    #                 print(f"({i},{j})")
    #                 cnt += 1
    #                 if cnt == 42:
    #                     break
    #                 self.output()
    #                 if self.win():
    #                     print("win!")
    #                     break
    #                 side = side % 2 + 1
    #                 print()


def REPL(players, publicFrm, record=True, addr=None):
    side = 1
    cnt = 1
    seq = []
    while True:
        print(f"--- {cnt} ---")
        print(f"Asking: side {chr(side+64)}")
        i, j = players[side-1].next()
        print(f"trying: ({i},{j}) side: {chr(side+64)}", end="")
        if publicFrm.drop(i, j, side) == -1:
            continue
        # print(f"({i},{j})")
        cnt += 1
        seq.append((i,j))
        if cnt == 42:
            break
        print(publicFrm)
        # print(relationalJudge(publicFrm, 1) + biasJudge(publicFrm, 1) - relationalJudge(publicFrm, 2) - biasJudge(publicFrm, 2))
        if publicFrm.win():
            print(f"side {chr(publicFrm.win()+64)} won!")
            break
        side = side % 2 + 1
        print()
    if record:
        _ = addr if addr != None else "rec.pkl"
        with open(_, 'wb') as f:
            pickle.dump(seq, f)
