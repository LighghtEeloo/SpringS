from springFrame import *


class Moment:
    def __init__(self, view, parent=None, step=None, frame=None, grading=None):
        self.parent = parent
        self.won = None
        self.grade = None
        self.view = view
        self.step = step
        self.frame: Frame = frame
        self.grading: function = grading
        self.nextMoments = []
        self.visited = None
    def __eq__(self, other):
        return self.frame==other.frame
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
        return f"\nMoment: lx{self.visited}, {id(self)}\n  - step: {self.step} <{chr(self.view+64)}>\n  - grade: {self.grade}\n{self.frame}"
    def dilate(self, rad=None):
        opp = self.view % 2 + 1
        if self.frame is None:
            # print("?-*-?")
            # exit(14)
            return ValueError
        frm: Frame = self.frame
        # If the node has won, there's no need for further dilatation
        if frm.win() != 0:
            self.grade = 1860 if frm.win() == self.view else -1860
            return []
        row, col = frm.size[0], frm.size[1]
        steps = [(i, j) for i in range(row) for j in range(col) if frm[i][j].side != self.view]
        for step in steps:
            _ = Moment(opp, self, step, deepcopy(frm), self.grading)
            _.frame.drop(*step, opp)
            if _.frame.win() != 0:
                self.visited = -1
            self.nextMoments.append(_)
        self.visited = len(self.nextMoments) if self.visited != -1 else -1
        if not rad is None:
            # TODO: use rad!
            self.nextMoments.sort(key=lambda x: (-self.grading(x.frame, opp)))
            self.nextMoments = self.nextMoments[:rad] # python automatically takes care of the upper bound
        self.frame = None
        return self.nextMoments
    def assess(self):
        if self.frame is None and len(self.nextMoments) > 0:
            bucket = []
            for node in self.nextMoments:
                if node.grade is None:
                    node.assess()
                bucket.append(node.grade)
            # print(self)
            # print(bucket)
            self.grade = -max(bucket)
        elif not self.frame is None:
            self.won = self.frame.win()
            if self.won == 0:
                self.grade = self.grading(self.frame, self.view)
            elif self.won == self.view:
                self.grade = 1860
            elif self.won != self.view:
                self.grade = -1860
            if self.grade is None:
                pt = self
                while not pt is None:
                    print(pt)
                    pt = pt.parent
                exit(13)
        elif len(self.nextMoments) == 0:
            # self.grade = 0
            if self.grade is None:
                pt = self
                while not pt is None:
                    print(pt)
                    print("!-*-!")
                    # print(pt.nextMoments)
                    pt = pt.parent
                exit(13)
        return self.grade

class Player:
    def __init__(self, side=0, frame=None):
        if not frame is None:
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
    # 己方后手评分
    relationGrade = [
        [-500, 24,11, 2],  # 己方已满
        [-20,-200, 5, 1],  # 己方差一
        [ -9, -20,-2, 0]  # 己方差二
    ]
    # 对手已满，差一，差二，差三
    biasGradeBefore = [
        45, 20, 17, 15
    ]
    # 已满至差三的分数
    biasGradeNext = [
        45, 20, 17, 15
    ]
    # 已满至差三的分数
    def __init__(self, side=0, frame=None):
        super().__init__(side=side, frame=frame)
        self.numNext = 0
        self.maxDepth = 1
        self.radius = None # None for no restriction

    def next(self):
        rad = self.radius
        self.numNext += 1
        opp = self.side % 2 + 1
        root = Moment(opp, frame=deepcopy(self.frame), grading=self.Judge)
        dilatation = [root]
        for depth in range(self.maxDepth):
            print("depth:", depth)
            tmp = []
            for node in dilatation:
                a = node.dilate(rad=rad)
                tmp.extend(a)
            dilatation = tmp.copy()
        root.assess()
        # print(root.nextMoments)
        root.nextMoments.sort(key=lambda x: (-x.grade))
        return root.nextMoments[0].step

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
                try:
                    return cls.relationGrade[potA.limit - potA.height - 1][potB.limit - potB.height - 1] // 2
                except IndexError:
                    print(f"PotA: {potA}\nPotB: {potB}") # too much for a block
                    print(f"indices: {[potA.limit - potA.height - 1, potB.limit - potB.height - 1]}")
            return 0
        row, col = frm.size
        grade = 0
        _ = []
        for i in range(row):
            for j in range(col):
                x, y = i + 1, j
                if x < row:
                    _.append(gradeHelper(
                        frm.board[i][j], frm.board[x][y], view))
                x, y = i, j + 1
                if y < col:
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
    def biasJudge(cls, frm, view, biasGrade=None) -> int:
        if biasGrade is None:
            biasGrade = cls.biasGradeBefore
        size = frm.size
        grade = 0
        for i in range(size[0]):
            for j in range(size[1]):
                pot = frm.board[i][j]
                if pot.side == view:
                    grade += biasGrade[pot.limit - pot.height - 1]
        return grade
    
    @classmethod
    def Judge(cls, frm=None, view=1, biasGradeBefore=None, biasGradeNext=None) -> int:
        # if frm is None:
        #     frm = self.frame
        if biasGradeBefore is None: 
            biasGradeBefore = cls.biasGradeBefore
        if biasGradeNext is None: 
            biasGradeNext = cls.biasGradeNext
        oppview = view % 2 + 1
        grade = (
            # + cls.relationalJudge(frm, view) 
            + cls.biasJudge(frm, view, biasGradeBefore)
            # - cls.relationalJudge(frm, oppview) 
            - cls.biasJudge(frm, oppview, biasGradeNext)
        )
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
        # frm.drop(0,0,1)
        # frm.drop(0,4,2)
        # frm.drop(3,0,1)
        # frm.drop(3,4,2)
        # frm.drop(0,2,1)
        # frm.drop(3,2,2)
        # frm.drop(0,2,1)
        # frm.drop(3,2,2)
        # frm.drop(1,2,1)
        # frm.drop(2,2,2)
        # frm.drop(1,2,1)
        # frm.drop(2,2,2)
        # frm.drop(1,2,1)
        # frm.drop(2,2,2)
        # rd = Rigid(1, frm)
        # rd.next()
        pass

    '''Human vs Rigid:'''
    # REPL((Rigid(1,frm), Human(2,frm)),frm)

    '''Rigid vs Rigid:'''
    REPL((Rigid(1, frm), Rigid(2, frm)), frm)


    # rd = Rigid(1,frm)
    # frm.drop(*rd.next(),1)

    # print(Rigid.relationalJudge(frm,2))
    # print(Rigid.biasJudge(frm,2))
    # print(Rigid.Judge(frm,2))
