import logging
import json
import math
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())


def loadWall(geometrydata):
    log.info("Beginning Wall Point Processing")
    wallpoint = []
    for i in range(len(geometrydata)):
        xcord = float(geometrydata[i].split()[0])
        ycord = float(geometrydata[i].split()[1])
        wallpoint.append(str(xcord) + "," + str(ycord))
    log.info("Wall Point Processed")
    return wallpoint


def save_obj(obj, name ):
    with open(name + '.json', 'w') as f:
        json.dump(obj, f)

def load_obj(name ):
    with open(name + '.json', 'r') as f:
        return json.load(f)

def checkIfInside(xcord,ycord,wallData,wallDataorg,bsplineWallData):
    for idx,itm in enumerate(wallData):
        compare = itm.split("\t")
        compareValX = float(compare[0])
        compareValY = float(compare[1])
        if xcord == compareValX and ycord == compareValY:
            if [xcord,ycord] in wallDataorg:
                return True,idx
            return False,0
            
    return False,0

def wallFloat(walldata):
    result = []
    for itm in walldata:
        itmdata = itm.split("\t")
        result.append([float(itmdata[0]), float(itmdata[1])])
    return result


def distance_squared(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def getItem(dictobj, key):
    data = []
    result = dictobj.get(key)
    if result != None:
        for itm in result:
            data.append(itm)
            itmcheck = str(itm[0]) + "," + str(itm[1])
            data = data + getItem(dictobj,itmcheck)
        return data
    else:
        return data