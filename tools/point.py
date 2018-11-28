class QuadPoint:
    index = 0
    x = 0
    y = 0
    leftindex = 0
    rightindex = 0
    pointtype = 0
    pointgeoindex = 0
    xposflag = 0
    xnegflag = 0
    yposflag = 0
    ynegflag = 0
    nx = 0
    ny = 0
    depth = 0
    quaddir = 0
    topcordx = 0
    topcordy = 0
    bottomcordx = 0
    bottomcordy = 0
    numbernbhs = 0
    neighbours = []

    def __init__(self, index, x, y, leftindex, rightindex, pointtype, pointgeoindex, xposflag, xnegflag, yposflag, ynegflag, nx, ny, depth, quaddir, topcordx, topcordy, bottomcordx, bottomcordy, numbernbhs, neighbours):  
        self.index = index  
        self.x = x
        self.y = y
        self.leftindex = leftindex
        self.rightindex = rightindex
        self.pointtype = pointtype
        self.pointgeoindex = pointgeoindex
        self.xposflag = xposflag
        self.xnegflag = xnegflag
        self.yposflag = yposflag
        self.ynegflag = ynegflag
        self.nx = nx
        self.ny = ny
        self.depth = depth
        self.quaddir = quaddir
        self.topcordx = topcordx
        self.topcordy = topcordy
        self.bottomcordx = bottomcordx
        self.bottomcordy = bottomcordy
        self.numbernbhs = numbernbhs
        self.neighbours = neighbours

    def getIndex(self):
        return self.index
    
    def X(self):
        return self.x
    
    def Y(self):
        return self.y

    def getLeftIndex(self):
        return self.leftindex

    def setLeftIndex(self, value):
        self.leftindex = value

    def getRightIndex(self):
        return self.rightindex

    def setRightIndex(self, value):
        self.rightindex = value

    def pointType(self):
        return self.pointtype

    def pointGeometry(self):
        return self.pointgeoindex

    def getXPosFlag(self):
        return self.xposflag

    def setXPosFlag(self, value):
        self.xposflag = value

    def getXNegFlag(self):
        return self.xnegflag

    def setXNegFlag(self, value):
        self.xnegflag = value

    def getYPosFlag(self):
        return self.yposflag

    def setYPosFlag(self, value):
        self.yposflag = value

    def getYNegFlag(self):
        return self.ynegflag

    def setYNegFlag(self, value):
        self.ynegflag = value

    def getNx(self):
        return self.nx

    def setNx(self, value):
        self.nx = value

    def getNy(self):
        return self.ny

    def setNy(self, value):
        self.ny = value

    def getDepth(self):
        return self.depth

    def getQuadDirection(self):
        return self.quaddir

    def getTopCordX(self):
        return self.topcordx

    def getTopCordY(self):
        return self.topcordy

    def getBottomCordX(self):
        return self.bottomcordx

    def getBottomCordY(self):
        return self.bottomcordy

    def getNeighboursCount(self):
        return self.numbernbhs

    def getNeighbours(self):
        return self.neighbours

    def setNeighbours(self, value):
        self.nbhs = value
        self.numbernbhs = len(value)