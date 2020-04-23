from springFrame import *
from Player import *
from random import random
import numpy as np
import math

class Holder:
    __slots__ = ('Units','n_all','reserve','temperature')
    def __init__(self, Units: list):
        self.Units = Units
        self.n_all = len(self.Units)
        self.reserve = math.floor(self.n_all/3)
        self.temperature = 1.0
    def round(self, printing=False):
        print("___rounding___")
        queue = self.Units
        # for _ in queue:
        #     print(_)
        Res = {}
        for i in range(len(queue)):
            for j in range(i+1, len(queue)):
                Res[(i,j)] = Res[(j,i)] = 0
                for k in range(1):
                    Res[(i,j)] += self.__match(queue[i], queue[j], f"{i:0>2} - {j:0>2}, {k:0>1}")
                    Res[(j,i)] += self.__match(queue[j], queue[i], f"{j:0>2} - {i:0>2}, {k:0>1}")
        return Res

    @staticmethod
    def __match(botA: Player, botB: Player, Ids=None):
        # print("___matching___")
        # print(botA)
        # print(botB)
        botA.side = 1
        botB.side = 2
        frm = Frame()
        botA.frame = botB.frame = frm
        winningSide = None
        if not Ids:
            winningSide = REPL([botA, botB], frm,
                            record=False, printing=printing)
        else:
            winningSide = REPL([botA, botB], frm, record=True,
                            addr="MatchInfoCache/"+Ids+".pkl", printing=printing)
        return winningSide

    def grade(self, MatchRes):
        print("___grading___")
        Score = [0] * self.n_all
        for sides, result in MatchRes.items():
            A, B = sides
            if result == 1:
                Score[A] += 10
                Score[B] -= 7
            elif result == 2:
                Score[B] += 10
                Score[A] -= 7
        return Score
    def filter(self, Score, reserve=None):
        print("___filtering___")
        if not reserve:
            reserve = self.reserve
        com = sorted([(self.Units[i], Score[i]) for i in range(self.n_all)], key=lambda x: (x[1]), reverse=True)[:reserve]
        return [x[0] for x in com]
    def evolve(self, curUnits: list, Score=None):
        print(f"___evolving___, temperature = {self.temperature}")
        newUnits = deepcopy(curUnits)
        for _ in range(1):
            for cu in curUnits:
                cu: Rigid
                for i in range(len(cu.biasGradeBefore)):
                    cu.biasGradeBefore[i] += (random()*2-1)*self.temperature
                for i in range(len(cu.biasGradeNext)):
                    cu.biasGradeNext[i] += (random()*2-1)*self.temperature
            newUnits.extend(curUnits)
        while len(newUnits) < self.n_all:
            newU = Rigid()
            for i in range(len(newU.biasGradeBefore)):
                newU.biasGradeBefore[i] += (random()*2-1)*self.temperature*5
            for i in range(len(newU.biasGradeNext)):
                newU.biasGradeNext[i] += (random()*2-1)*self.temperature*5
            newUnits.append(newU)
        newUnits = newUnits[:self.n_all]

        # TODO: refresh self.temperature
        if Score:
            var = np.var(Score)**0.5/10
            print("variance**0.5:", var)
            var = var**0.5
            temp = self.temperature + (var-2)
            self.temperature = temp if temp > 0 else 2.0
        
        return newUnits

    def loop(self, id):
        Res = self.round()
        Score = self.grade(Res)
        print(Score)
        curUnits = self.filter(Score)
        print("best:", curUnits[0])
        self.Units = self.evolve(curUnits, Score)
        for i in range(self.n_all):
            print(" - - :", self.Units[i])
        print(len(self.Units))
        with open(f"MatchInfoCache/Units_{id:0>3}.pkl", 'wb') as f:
            pickle.dump(self.Units, f)


if __name__ == "__main__":
    # for i in range(10):
    #     for j in range(10):
    #         print(f"{i:0>2},{j}")
    hd = Holder([Rigid() for _ in range(15)])
    # hd.round()
    # print(hd.grade())
    for _ in range(200):
        hd.loop(_)
