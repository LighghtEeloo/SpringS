from springFrame import *

'''
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
                        self.nextMoments.append(Moment((i, j), opp, frm))
                        self.nextMoments[-1].grade = grading(
                            frm=self.nextMoments[-1].frame, view=opp)
                        if printing:
                            print("step graded:", self.nextMoments[-1].grade)
                    else:
                        self.nextMoments.append(
                            Moment((i, j), opp, frm, frm.win()))
        self.nextMoments.sort(key=lambda x: (x.grade), reverse=1)
        if candidate != 0:
            self.nextMoments = self.nextMoments[:candidate]
        if printing:
            for moment in self.nextMoments:
                print(f"next grade: {moment.grade}")
                moment.frame.output()
    def erase(self):
        self.frame = None
'''

class Moment:
    def __init__(self, view, parent=None, step=None, frame=None, grading=None, rad=None):
        self.parent = parent
        self.won = None
        self.grade = None
        self.view = view
        self.step = step
        self.frame: Frame = frame
        self.grading: function = grading
        self.rad = rad
        self.nextMoments = []
    def __eq__(self, other):
        return super().__eq__(other)
    def __hash__(self):
        if self.frame is None:
            return super().__hash__()
        else:
            return self.frame.__hash__()
    def __getitem__(self, position):
        if position < len(self.nextMoments):
            return self.nextMoments[position]
        return None
    def __repr__(self):
        return f"\nMoment: \n  - step: {self.step} <{chr(self.view+64)}>\n  - grade: {self.grade}\n"
    def dilate(self):
        opp = self.view % 2 + 1
        if self.frame is None:
            return ValueError
        frm: Frame = self.frame
        row, col = frm.size[0], frm.size[1]
        steps = [(i, j) for i in range(row) for j in range(col) if frm[i][j].side != self.view]
        for step in steps:
            _ = Moment(opp, self, step, deepcopy(frm), self.grading)
            _.frame.drop(*step, opp)
            _.frame.output()
            self.nextMoments.append(_)
        self.frame = None
        return self.nextMoments
    def assess(self):
        if self.frame is None and len(self.nextMoments) > 0:
            bucket = []
            for node in self.nextMoments:
                if node.grade is None:
                    node.assess()
                bucket.append(node.grade)
            return -max(bucket)
        else:
            self.won = self.frame.win()
            if self.won == 0:
                self.grade = self.grading(self.frame, self.view)
            else:
                self.grade = 1860
            return self.grade
        return ValueError

class Player:
    def __init__(self, side=0, frame=None):
        if frame != None:
            self.frame = frame  # connected!
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
                    if frm.drop(intup[0], intup[1], side=self.side) != -1:
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
    relationGrade = [
        [50, 24, 11, 5],  # 己方已满
        [-400, 11, 5, 2],  # 己方差一
        [-900, -400, 2, 0]  # 己方差二
    ]
    # 对手已满，差一，差二，差三
    biasGrade = [
        18, 8, 3, 1
    ]
    # 已满至差三的分数
    def __init__(self, side=0, frame=None):
        super().__init__(side=side, frame=frame)
        self.numNext = 0
        self.maxDepth = 1
        self.candidateBias = 5

    '''
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
                        firstSteps.append(Moment((i, j), self.side, frm))
                        firstSteps[-1].grade = self.Judge(
                            frm=firstSteps[-1].frame, view=self.side)
                        # print("graded:", firstSteps[-1].grade)
                    else:
                        firstSteps.append(
                            Moment((i, j), self.side, frm, frm.win()))
        firstSteps.sort(key=lambda x: (x.grade), reverse=1)
        if not simple:
            self.steper(opp, firstSteps, self.maxDepth-1, candidate)
            with open("allSteps.pkl", 'wb') as f:
                pickle.dump(firstSteps, f)
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
        while candidate >= 2 and candidate < len(Moments) and Moments[candidate-1].grade == Moments[candidate-2].grade:
            candidate += 1
        Moments = Moments[:candidate]
        for moment in Moments:
            if moment.won == 0:
                moment.nextStep(self.Judge, c)
                self.steper(opp, moment.nextMoments,
                            depth-1, self.candidateBias)
    '''
    def next(self):
        opp = self.side % 2 + 1
        root = Moment(opp, frame=deepcopy(self.frame), grading=self.Judge)
        dilatation = [root]
        for _ in range(self.maxDepth):
            tmp = []
            for node in dilatation:
                tmp.extend(node.dilate())

    # Wrong!
    # Wrong!!
    # Wrong!!!
    @classmethod
    def relationalJudge(cls, frm, view) -> int:
        def gradeHelper(potA, potB, view):
            oppview = view % 2 + 1
            if potA.side == view and potB.side == oppview:
                return cls.relationGrade[potA.limit - potA.height - 1][potB.limit - potB.height - 1]
            if potA.side == view and potB.side == 0:
                return cls.relationGrade[potA.limit - potA.height - 1][potB.limit - potB.height - 1] // 2
            return 0
        size = frm.size
        grade = 0
        _ = []
        for i in range(size[0]):
            for j in range(size[1]):
                x, y = i + 1, j
                if x < size[0]:
                    _.append(gradeHelper(
                        frm.board[i][j], frm.board[x][y], view))
                x, y = i, j + 1
                if y < size[1]:
                    _.append(gradeHelper(
                        frm.board[i][j], frm.board[x][y], view))
                x, y = i - 1, j
                if x >= 0:
                    _.append(gradeHelper(
                        frm.board[i][j], frm.board[x][y], view))
                x, y = i, j - 1
                if y >= 0:
                    _.append(gradeHelper(
                        frm.board[i][j], frm.board[x][y], view))
        grade = sum(_)
        # print(f"relational: {_}")
        return grade
    @classmethod
    def biasJudge(cls, frm, view) -> int:
        size = frm.size
        grade = 0
        for i in range(size[0]):
            for j in range(size[1]):
                pot = frm.board[i][j]
                if pot.side == view:
                    grade += cls.biasGrade[pot.limit - pot.height - 1]
        return grade
    @classmethod
    def Judge(cls, frm=None, view=1) -> int:
        # if frm is None:
        #     frm = self.frame
        oppview = view % 2 + 1
        grade = cls.relationalJudge(frm, view) + cls.biasJudge(frm, view) - \
            cls.relationalJudge(frm, oppview) - cls.biasJudge(frm, oppview)
        return grade


if __name__ == "__main__":
    os.chdir(sys.path[0])

    frm = Frame()

    '''Human vs Human:'''
    # REPL((Human(1),Human(2)),Frame())

    '''Reader:'''
    if True:
        # reader = Reader(addr="rec.pkl")
        # REPL((reader,reader),Frame())
        pass

    '''Drop Test:'''
    if True:
        frm.drop(0,0,1)
        frm.drop(0,4,2)
        frm.drop(3,0,1)
        frm.drop(3,4,2)
        frm.drop(0,2,1)
        frm.drop(3,2,2)
        frm.drop(0,2,1)
        frm.drop(3,2,2)
        frm.drop(1,0,1)
        frm.drop(2,4,2)
        # rd = Rigid(1, frm)
        # rd.next()
        pass

    '''Human vs Rigid:'''
    # REPL((Rigid(1,frm), Human(2,frm)),frm)

    '''Rigid vs Rigid:'''
    # REPL((Rigid(1, frm), Rigid(2, frm)), frm)


    # rd = Rigid(1,frm)
    # frm.drop(*rd.next(),1)
    # frm.output()

    frm.output()
    m = Moment(2,frame=frm, grading=Rigid().Judge)
    m.dilate()
    print(m.assess())
    print(f"{m.nextMoments}")