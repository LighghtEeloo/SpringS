from springFrame import *
from Player import *

class Holder:
    def __init__(self, Units: list):
        self.Units = Units
        self.MatchRes = {}
        self.Score = [0]*len(Units)
    def round(self, printing=False):
        def match(botA: Player, botB: Player, Ids=None):
            botA.side = 1
            botB.side = 2
            frm = Frame()
            botA.frame = botB.frame = frm
            winningSide = None
            if not Ids:
                winningSide = REPL([botA,botB], frm, record=False, printing=printing)
            else:
                winningSide = REPL([botA, botB], frm, record=True,
                                   addr="MatchInfoCache/"+Ids+".pkl", printing=printing)
            return winningSide
        
        queue = self.Units
        Res = {}
        for i in range(len(queue)):
            for j in range(i+1, len(queue)):
                Res[(i,j)] = Res[(j,i)] = 0
                for k in range(1):
                    Res[(i,j)] += match(queue[i], queue[j], f"{i:0>2} - {j:0>2}, {k:0>1}")
                    Res[(j,i)] += match(queue[j], queue[i], f"{j:0>2} - {i:0>2}, {k:0>1}")
        self.MatchRes = Res
    def grade(self):
        for sides, result in self.MatchRes.items():
            A, B = sides
            if result == 1:
                self.Score[A] += 10
                self.Score[B] -= 7
            elif result == 2:
                self.Score[B] += 10
                self.Score[A] -= 7
        return self.Score
    def filter(self, reserve):
        com = [(self.Units[i], self.Score[i]) for i in range(len(self.Units))].sorted(key=lambda x: (x[1]), reversed=True)[:reserve]
        return com
    def evolve(self):
        pass


if __name__ == "__main__":
    # for i in range(10):
    #     for j in range(10):
    #         print(f"{i:0>2},{j}")
    hd = Holder([Rigid() for _ in range(20)])
    hd.round()
    print(hd.grade())
