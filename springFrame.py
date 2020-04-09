import os,sys
import pickle
from copy import deepcopy

printing = False


class Pot:
    def __init__(self, side, height, limit):
        self.side = side
        self.height = height
        self.limit = limit
    def __repr__(self):
        return f"({self.height}|{chr(self.side+64)})"
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
    def sync(self, board=None):
        if board != None:
            self.board = board[:]
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
    def loop(self):
        side = 1
        cnt = 1
        for _ in range(3):
            for i in range(4):
                for j in range(5):
                    print(f"--- {cnt} ---")
                    print(f"trying: ({i},{j}) side: {chr(side+64)}")
                    if self.drop(i,j, side) == -1:
                        continue
                    print(f"({i},{j})")
                    cnt += 1
                    if cnt == 42:
                        break
                    self.output()
                    if self.win():
                        print("win!")
                        break
                    side = side % 2 + 1
                    print()


class Moment:
    def __init__(self, step, view, frame, won=0):
        self.won = won
        if won == 0:
            self.step = step
            self.view = view
            self.frame = frame
            self.grade = None
            self.nextMoments = []
        else:
            self.step = step
            self.view = view
            self.frame = frame
            self.grade = (-1)*(abs(view-won)-1)*31*60
    # TODO: pruning by candidate
    def nextStep(self, grading, candidate=0):
        self.nextMoments = []
        opp = self.view % 2 + 1
        for i in range(self.frame.size[0]):
            for j in range(self.frame.size[1]):
                frm = deepcopy(self.frame)
                if frm.drop(i, j, opp) != -1:
                    if frm.win() == 0:
                        self.nextMoments.append(Moment((i,j),opp,frm))
                        self.nextMoments[-1].grade = grading(frm=self.nextMoments[-1].frame, view=opp)
                        if printing:
                            print("step graded:", self.nextMoments[-1].grade)
                    else:
                        self.nextMoments.append(Moment((i, j), opp, frm, frm.win()))
        self.nextMoments.sort(key=lambda x: (x.grade), reverse=1)
        if candidate != 0:
            self.nextMoments = self.nextMoments[:candidate]
        if printing:
            for moment in self.nextMoments:
                print(f"next grade: {moment.grade}")
                moment.frame.output()
                        

def REPL(players, publicFrm, record=True, addr=None):
    side = 1
    cnt = 1
    seq = []
    while True:
        print(f"--- {cnt} ---")
        print(f"Asking: side {chr(side+64)}")
        i, j = players[side-1].next()
        print(f"trying: ({i},{j}) side: {chr(side+64)}")
        if publicFrm.drop(i, j, side) == -1:
            continue
        print(f"({i},{j})")
        cnt += 1
        seq.append((i,j))
        if cnt == 42:
            break
        publicFrm.output()
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


class Player:
    def __init__(self, side=0, frame=None):
        if frame != None:
            self.frame = frame # connected!
        else:
            self.frame = Frame()
        self.side = side
    def next(self):
        return NotImplemented

class Human(Player):
    def __init__(self, side=0, frame=None):
        super().__init__(side=side, frame=frame)
    def next(self):
        size = self.frame.size
        frm = deepcopy(self.frame)
        # print("asking...")
        while True:
            try:
                inlst = input("x, y: ").strip('[]').split(',')
                intup = tuple([int(x) for x in inlst])
            except ValueError as e:
                pass
            else:
                if len(intup) == 2 and intup[0] >= 0 and intup[0] < size[0] and intup[1] >= 0 and intup[1] < size[1]:
                    if frm.drop(intup[0],intup[1], side=self.side) != -1:
                        break
            print("Again?")
        print(intup)
        return intup

class Reader(Player):
    def __init__(self, frame=None, seq=None, addr=None, read=True):
        super().__init__(frame=frame)
        if read:
            self.read(addr)
        else:
            self.seq = seq
        self.idx = 0
    def read(self, addr):
        with open(addr, 'rb') as f:
            self.seq = pickle.load(f)
    def next(self):
        if self.idx >= len(self.seq):
            return IndexError
        idx = self.idx
        self.idx += 1
        return self.seq[idx]

class Rigid(Player):
    def __init__(self, side=0, frame=None):
        super().__init__(side=side, frame=frame)
        self.relationGrade = [
            [50,24,11, 5], # 己方已满
            [-4,11, 5, 2], # 己方差一
            [-9,-4, 2, 0]  # 己方差二
        ]
        self.biasGrade = [
            18, 8, 3, 1
        ]
        self.numNext = 0
        self.maxDepth = 9
        self.candidateBias = 2

    def next(self, simple=False):
        self.numNext += 1
        candidate = self.candidateBias
        # candidate = self.candidateBias + self.numNext // 2
        firstSteps = []
        opp = self.side % 2 + 1
        # print("!-*-!")
        # self.frame.output()
        for i in range(self.frame.size[0]):
            for j in range(self.frame.size[1]):
                # print(f"trying: ({i},{j})")
                frm = deepcopy(self.frame)
                if frm.drop(i, j, self.side) != -1:
                    if frm.win() == 0:
                        firstSteps.append(Moment((i,j),self.side,frm))
                        firstSteps[-1].grade = self.Judge(frm=firstSteps[-1].frame, view=self.side)
                        # print("graded:", firstSteps[-1].grade)
                    else:
                        firstSteps.append(Moment((i, j), self.side, frm, frm.win()))
        firstSteps.sort(key=lambda x: (x.grade), reverse=1)
        if not simple:
            self.steper(opp, firstSteps, self.maxDepth-1, candidate)
            with open("allSteps.pkl",'wb') as f:
                pickle.dump(firstSteps,f)
            if printing:
                print("-------- Finished! --------")
            return firstSteps[0].step
        else:
            for moment in firstSteps:
                print(f" -> {moment.step} => {moment.grade}")
            return firstSteps[0].step
    def steper(self, view, Moments: list, depth=0, candidate=1):
        if depth == 0:
            return
        if printing: 
            print(f"depth: {depth}")
        opp = self.side % 2 + 1
        c = candidate
        candidate = len(Moments) if candidate > len(Moments) else candidate
        while candidate >=2 and candidate < len(Moments) and Moments[candidate-1].grade == Moments[candidate-2].grade:
            candidate += 1
        Moments = Moments[:candidate]
        for moment in Moments:
            if moment.won == 0:
                moment.nextStep(self.Judge, c)
                self.steper(opp, moment.nextMoments, depth-1, self.candidateBias)
    def relationalJudge(self, frm, view) -> int:
        def gradeHelper(potA, potB, view):
            if potA.side == view and potB.side != view:
                return self.relationGrade[potA.limit - potA.height - 1][potB.limit - potB.height - 1]
            return 0
        size = frm.size
        grade = 0
        _ = []
        for i in range(size[0]):
            for j in range(size[1]):
                x, y = i + 1, j
                if x < size[0]:
                    _.append(gradeHelper(frm.board[i][j], frm.board[x][y], view))
                    # grade += self.gradeHelper(frm.board[i][j], frm.board[x][y], view)
                x, y = i, j + 1
                if y < size[1]:
                    _.append(gradeHelper(frm.board[i][j], frm.board[x][y], view))
                    # grade += self.gradeHelper(frm.board[i][j], frm.board[x][y], view)
                x, y = i - 1, j
                if x >= 0:
                    _.append(gradeHelper(frm.board[i][j], frm.board[x][y], view))
                    # grade += self.gradeHelper(frm.board[i][j], frm.board[x][y], view)
                x, y = i, j - 1
                if y >= 0:
                    _.append(gradeHelper(frm.board[i][j], frm.board[x][y], view))
                    # grade += self.gradeHelper(frm.board[i][j], frm.board[x][y], view)
        grade = sum(_)
        # print(f"relational: {_}")
        return grade
    def biasJudge(self, frm, view) -> int:
        size = frm.size
        grade = 0
        for i in range(size[0]):
            for j in range(size[1]):
                pot = frm.board[i][j]
                if pot.side == view:
                    grade += self.biasGrade[pot.limit - pot.height - 1]
        return grade
    def Judge(self, frm=None, view=1) -> int:
        # if frm == None:
        #     frm = self.frame
        oppview = view % 2 + 1
        grade = self.relationalJudge(frm, view) + self.biasJudge(frm, view) - \
            self.relationalJudge(frm, oppview) - self.biasJudge(frm, oppview)
        return grade


def relationalJudge(frm, view) -> int:
    size = frm.size
    grade = 0
    relationGrade = [
        [50, 24, 11, 5],  # 己方已满
        [-4, 11, 5, 2],  # 己方差一
        [-9, -4, 2, 0]  # 己方差二
    ]
    for i in range(size[0]):
        for j in range(size[1]):
            x, y = i + 1, j
            if x < size[0]:
                potA = frm.board[i][j]
                potB = frm.board[x][y]
                if potA.side == view\
                    and (potB.side != view):
                    grade += relationGrade[potA.limit - potA.height - 1][potB.limit - potB.height - 1]
            x, y = i, j + 1
            if y < size[1]:
                potA = frm.board[i][j]
                potB = frm.board[x][y]
                if potA.side == view\
                    and (potB.side != view):
                    grade += relationGrade[potA.limit - potA.height - 1][potB.limit - potB.height - 1]
            x, y = i - 1, j
            if x >= 0:
                potA = frm.board[i][j]
                potB = frm.board[x][y]
                if potA.side == view\
                    and (potB.side != view):
                    grade += relationGrade[potA.limit - potA.height - 1][potB.limit - potB.height - 1]
            x, y = i, j - 1
            if y >= 0:
                potA = frm.board[i][j]
                potB = frm.board[x][y]
                if potA.side == view\
                    and (potB.side != view):
                    grade += relationGrade[potA.limit - potA.height - 1][potB.limit - potB.height - 1]
    # print(f"relational graded: {grade}, view: {chr(view+64)}")
    return grade
def biasJudge(frm, view) -> int:
    biasGrade = [
        18, 8, 3, 1
    ]
    size = frm.size
    grade = 0
    for i in range(size[0]):
        for j in range(size[1]):
            pot = frm.board[i][j]
            if pot.side == view:
                grade += biasGrade[pot.limit - pot.height - 1]
    return grade
def Judge(frm=None, view=1) -> int:
    # if frm == None:
    #     frm = self.frame
    oppview = view % 2 + 1
    grade = relationalJudge(frm, view) + biasJudge(frm, view) - \
        relationalJudge(frm, oppview) - biasJudge(frm, oppview)
    return grade


if __name__ == "__main__":
    os.chdir(sys.path[0])
    # frm = Frame()
    # frm.loop()

    # h1 = Human()
    # print(h1.next())
    # h2 = Human()
    # REPL((h1,h2),frm)

    # REPL((Human(1),Human(2)),Frame())

    # reader = Reader(addr="rec.pkl")
    # REPL((reader,reader),Frame())

    frm = Frame()
    # # frm.drop(0,0,1)
    # # Moment((0,0),1,frm).nextStep(Judge)
    # frm.drop(0,0,1)
    # frm.drop(0,4,2)
    # frm.drop(3,0,1)
    # frm.drop(3,4,2)
    # frm.drop(0,2,1)
    # frm.drop(3,2,2)
    # frm.drop(0,2,1)
    # frm.drop(3,2,2)
    # frm.drop(1,0,1)
    # frm.drop(2,4,2)
    # rd = Rigid(1, frm)
    # rd.next()

    # REPL((Rigid(1,frm), Human(2,frm)),frm)
    # REPL((Rigid(1,frm), Rigid(2,frm)),frm)

    rd = Rigid(1,frm)
    frm.drop(*rd.next(),1)
    frm.output()
