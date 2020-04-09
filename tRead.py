import pickle
from springFrame import *
def show():
    with open("rec.pkl",'rb') as f:
        for step in pickle.load(f):
            print(step)

def change():
    seq = []
    with open("rec.pkl",'rb') as f:
        seq = pickle.load(f)
        seq[-1] = (0,1)
    with open("rec.pkl",'wb') as f:
        seq = pickle.dump(seq, f)

def readAll():
    def readMoment(moment: Moment, depth: int=None):
        print(f"next_step: {moment.step} -- {depth}")
        print(f"next_grade: {moment.grade}")
        moment.frame.output()
        if moment.won != 0:
            print(f"{chr(moment.won+64)} won!\n")
            return
        for nextMoment in moment.nextMoments:
            readMoment(nextMoment, depth+1)
    with open("allSteps.pkl",'rb') as f:
        firstSteps: list = pickle.load(f)
    for moment in firstSteps:
        readMoment(moment, 1)



if __name__=="__main__":
    # show()
    readAll()