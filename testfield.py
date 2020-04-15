from springFrame import *
from Player import *

class Holder:
    def __init__(self, Units: list):
        self.Units = Units
        self.Scores = {}
        self.Grade = [0]*len(Units)
    def round(self):
        def match(botA: Player, botB: Player, Ids=None):
            botA.side = 1
            botB.side = 2
            frm = Frame()
            botA.frame = botB.frame = frm
            winningSide = None
            if not Ids:
                winningSide = REPL([botA,botB], frm, record=False)
            else:
                winningSide = REPL([botA, botB], frm, record=True, addr="MatchInfoCache/"+Ids+".pkl")
            return winningSide
        
        queue = self.Units
        Scores = {}
        for i in range(len(queue)):
            for j in range(i+1, len(queue)):
                Scores[(i,j)] = Scores[(j,i)] = 0
                for k in range(1):
                    Scores[(i,j)] += match(queue[i], queue[j], f"{i:0>2} - {j:0>2}, {k:0>1}")
                    Scores[(j,i)] += match(queue[j], queue[i], f"{j:0>2} - {i:0>2}, {k:0>1}")
        self.Scores = Scores
    def grade(self):
        for sides, result in self.Scores.items():
            A, B = sides
            if result == 1:
                self.Grade[A] += 10
                self.Grade[B] -= 7
            elif result == 2:
                self.Grade[B] += 10
                self.Grade[A] -= 7
        return self.Grade


if __name__ == "__main__":
    # for i in range(10):
    #     for j in range(10):
    #         print(f"{i:0>2},{j}")
    hd = Holder([Rigid() for _ in range(10)])
    hd.round()
    print(hd.grade())
