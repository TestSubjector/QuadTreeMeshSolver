import logging
import pickle
import json
import math
from tqdm import trange
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())


def loadWall(geometrydata,hashtable,globaldata,idf):
    log.info("Beginning Wall Point Processing")
    wallpoint = []
    index = len(hashtable) + 1
    startpt = index
    lastpt = len(globaldata) + len(geometrydata) - 1
    for i in range(len(geometrydata)):
        try:
            xcord = float(geometrydata[i].split()[0])
            ycord = float(geometrydata[i].split()[1])

            cords = (xcord, ycord)
            hashtable[cords] = index
            wallpoint.append(str(xcord) + "," + str(ycord))  # Storing Wallpoints

            walldata = []
            # First Point
            if index == startpt:
                walldata.append(index)
                walldata.insert(1, xcord)
                walldata.insert(2, ycord)
                walldata.insert(3, lastpt)
                walldata.insert(4, index + 1)
                walldata.insert(5, 0)
                walldata.insert(6, idf)
                walldata.insert(7, 0)
                walldata.insert(8, 0)
                walldata.insert(9, 0)
                walldata.insert(10, 0)
                walldata.insert(11, 0)
                walldata.insert(12, 1)
                globaldata.append(walldata)
                index += 1
            # Last Point
            elif index == lastpt:
                walldata.append(index)
                walldata.insert(1, xcord)
                walldata.insert(2, ycord)
                walldata.insert(3, startpt + len(geometrydata) - 3)
                walldata.insert(4, startpt)
                walldata.insert(5, 0)
                walldata.insert(6, idf)
                walldata.insert(7, 0)
                walldata.insert(8, 0)
                walldata.insert(9, 0)
                walldata.insert(10, 0)
                walldata.insert(11, 0)
                walldata.insert(12, 1)
                globaldata.append(walldata)
                index += 1
            # Other Points
            else:
                walldata.append(index)
                walldata.insert(1, xcord)
                walldata.insert(2, ycord)
                walldata.insert(3, index - 1)
                walldata.insert(4, index + 1)
                walldata.insert(5, 0)
                walldata.insert(6, idf)
                walldata.insert(7, 0)
                walldata.insert(8, 0)
                walldata.insert(9, 0)
                walldata.insert(10, 0)
                walldata.insert(11, 0)
                walldata.insert(12, 1)
                globaldata.append(walldata)
                index += 1
        except:
            pass
    log.info("Wall Point Processed")
    return hashtable, wallpoint, globaldata


def loadInterior(data, hashtable, globaldata, index):
    log.info("Beginning Interior Point and Wall Point Neighbour Processing")
    for i in trange(len(data)):
        cleandata = str(data[i]).split(" ")
        if len(cleandata) > 1:
            depth = int(cleandata[2])
            direction = int(cleandata[3])
            topcordx = str(float(cleandata[4]))
            topcordy = str(float(cleandata[5]))
            bottomcordx = str(float(cleandata[6]))
            bottomcordy = str(float(cleandata[7]))
            leafcond = int(cleandata[8])
            cleandata.pop(2)
            cleandata.pop(2)
            cleandata.pop(2)
            cleandata.pop(2)
            cleandata.pop(2)
            cleandata.pop(2)
            cleandata.pop(2)
            cord = (float(cleandata[1].split(",")[0]), float(cleandata[1].split(",")[1]))
            try:
                if i != len(data) - 1:
                    val = hashtable.get(cord, None)
                    if val is not None:
                        cleandata.pop(0)  # Pop index
                        cleandata.pop(-1)  # Pop blank space
                        cleandata.pop(-2)  # Pop number of neighbours
                        cleandata.pop(0)  # Pop blank space
                        cleandata.insert(0, str(int(cleandata[len(cleandata) - 1])))
                        cleandata.insert(0, leafcond)
                        cleandata.insert(0, bottomcordy)
                        cleandata.insert(0, bottomcordx)
                        cleandata.insert(0, topcordy)
                        cleandata.insert(0, topcordx)
                        cleandata.insert(0, direction)
                        cleandata.insert(0, depth)
                        cleandata.pop(-1)
                        globaldata[val - 1] = globaldata[val - 1] + cleandata
                    else:
                        raise KeyError
                else:
                    val = hashtable.get(cord, None)
                    if val is not None:
                        cleandata.pop(0)
                        cleandata.pop(-2)
                        cleandata.pop(0)
                        cleandata.insert(0, str(int(cleandata[len(cleandata) - 1])))
                        cleandata.insert(0, leafcond)
                        cleandata.insert(0, bottomcordy)
                        cleandata.insert(0, bottomcordx)
                        cleandata.insert(0, topcordy)
                        cleandata.insert(0, topcordx)
                        cleandata.insert(0, direction)
                        cleandata.insert(0, depth)
                        cleandata.pop(-1)
                        globaldata[val - 1] = globaldata[val - 1] + cleandata
                    else:
                        raise KeyError
            except KeyError:
                if len(cleandata) > 4:
                    if i != len(data) - 1:
                        hashtable[cord] = index + 1
                        cleandata.pop(0)
                        cleandata.pop(-1)
                        cleandata.pop(-2)
                        cleandata.pop(0)
                        cleandata.insert(0, cleandata[len(cleandata) - 1])
                        cleandata.pop(-1)
                        cleandata.insert(0, leafcond)
                        cleandata.insert(0, bottomcordy)
                        cleandata.insert(0, bottomcordx)
                        cleandata.insert(0, topcordy)
                        cleandata.insert(0, topcordx)
                        cleandata.insert(0, direction)
                        cleandata.insert(0, depth)
                        cleandata.insert(0, 1)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 1)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, cord[1])
                        cleandata.insert(0, cord[0])
                        cleandata.insert(0, index + 1)
                        index += 1
                        globaldata.append(cleandata)
                    else:
                        hashtable[cord] = index + 1
                        cleandata.pop(0)
                        cleandata.pop(-2)
                        cleandata.pop(0)
                        cleandata.insert(0, cleandata[len(cleandata) - 1])
                        cleandata.pop(-1)
                        cleandata.insert(0, leafcond)
                        cleandata.insert(0, bottomcordy)
                        cleandata.insert(0, bottomcordx)
                        cleandata.insert(0, topcordy)
                        cleandata.insert(0, topcordx)
                        cleandata.insert(0, direction)
                        cleandata.insert(0, depth)
                        cleandata.insert(0, 1)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 1)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, 0)
                        cleandata.insert(0, cord[1])
                        cleandata.insert(0, cord[0])
                        cleandata.insert(0, index + 1)
                        index += 1
                        globaldata.append(cleandata)
                else:
                    log.warn("Warning: QuadTree Generated a Point which cannot be parsed.")
    log.info("Interior Point and Wall Point Neighbour Processed")
    return hashtable, globaldata

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
        try:
            result.append([float(itmdata[0]), float(itmdata[1])])
        except:
            pass
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