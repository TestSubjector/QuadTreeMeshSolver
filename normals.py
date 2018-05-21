class Normals:

    def __init__(self, hashtable, globaldata, index, cord):
        self.hashtable = hashtable
        self.globaldata = globaldata
        self.index = index
        self.cord = cord
    
    def normal_clockwise(self, wallpoint):
        nx = 0
        ny = 0
        cordx = float(self.cord.split(",")[0])
        cordy = float(self.cord.split(",")[1])
        val = self.hashtable.index(self.cord)
        pointdata = self.globaldata[val - 1]
        if(wallpoint):
            leftpoint = self.hashtable[pointdata[3]]
            rightpoint = self.hashtable[pointdata[4]]
        else:
            leftpoint = pointdata[3]
            rightpoint = pointdata[4]
