# from progress import *
import math
import shapely.geometry
from shapely import wkt
from shapely.ops import linemerge, unary_union, polygonize
import os
import errno
from progress import *
from logger import *
import multiprocessing
from multiprocessing.pool import ThreadPool
import time


def silentRemove(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def cleanNeighbours(globaldata):  # Verified
    print("Beginning Duplicate Neighbour Detection")
    for i in range(len(globaldata)):
        # printProgressBar(i, len(globaldata) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        noneighours = int(globaldata[i][11])  # Number of neighbours
        cordneighbours = globaldata[i][-noneighours:]
        # TODO - Ask, why get the same thing as above?
        cordneighbours = [
            str(float(j.split(",")[0])) + "," + str(float(j.split(",")[1]))
            for j in cordneighbours
        ]

        cordneighbours = dict.fromkeys(cordneighbours).keys()
        noneighours = len(cordneighbours)
        globaldata[i] = globaldata[i][:11] + [noneighours] + list(cordneighbours)
        # with open("duplication_removal.txt", "w") as text_file:
        #     for item1 in globaldata:
        #         text_file.writelines(["%s " % item for item in item1])
        #         text_file.writelines("\n")
    print("Duplicate Neighbours Removed")
    return globaldata


def getPoint(indexval, list):
    currentcord = str(list[indexval][1]) + "," + str(list[indexval][2])
    return currentcord


def getIndexOf(pointxy, hashtable):
    return int(hashtable.index(pointxy)) - 1


def getNeighbours(indexval, list):
    val = []
    pointdata = list[indexval]
    numbneigh = int(pointdata[11])
    try:
        for i in range(numbneigh):
            val = val + [str(pointdata[i + 12])]
    except Exception:
        pass
    return val


def getFlag(indexval, list):
    return list[indexval][5]


def updateLeft(indexval, list, leftpoint):
    list[indexval][3] = leftpoint
    return list


def updateRight(indexval, list, rightpoint):
    list[indexval][4] = rightpoint
    return list


def updateFlag(indexval, list, newflag):
    list[indexval][5] = newflag
    return list


def getYCordNeighbours(list):
    stuff = []
    for item in list:
        stuff.append(float(item.split(",")[1]))
    return stuff


def getXCordNeighbours(list):
    stuff = []
    for item in list:
        stuff.append(float(item.split(",")[0]))
    return stuff


def isPositive(val):
    if float(val) >= 0:
        return True
    else:
        return False


def getBiggestXBiggestY(list):
    newlist = []
    for item in list:
        if (
            isPositive(float(item.split(",")[0])) == True
            and isPositive(float(item.split(",")[1])) == True
        ):
            newlist.append(item)
    getBiggestX = max(getXCordNeighbours(newlist))
    templist = []
    for item in newlist:
        if float((item.split(",")[0])) == getBiggestX:
            templist.append(item)
    getBiggestY = max(getYCordNeighbours(templist))
    return str(getBiggestX) + "," + str(getBiggestY)


def getSmallestXBiggestY(list):
    newlist = []
    for item in list:
        if (
            isPositive(float(item.split(",")[0])) == False
            and isPositive(float(item.split(",")[1])) == True
        ):
            newlist.append(item)
    getSmallestX = min(getXCordNeighbours(newlist))
    templist = []
    for item in newlist:
        if float((item.split(",")[0])) == getSmallestX:
            templist.append(item)
    getBiggestY = max(getYCordNeighbours(templist))
    return str(getSmallestX) + "," + str(getBiggestY)


def getBiggestXSmallestY(list):
    newlist = []
    for item in list:
        if (
            isPositive(float(item.split(",")[0])) == True
            and isPositive(float(item.split(",")[1])) == False
        ):
            newlist.append(item)
    getBiggestX = max(getXCordNeighbours(newlist))
    templist = []
    for item in newlist:
        if float((item.split(",")[0])) == getBiggestX:
            templist.append(item)
    getSmallestY = min(getYCordNeighbours(templist))
    return str(getBiggestX) + "," + str(getSmallestY)


def getSmallestXSmallestY(list):
    newlist = []
    for item in list:
        if (
            isPositive(float(item.split(",")[0])) == False
            and isPositive(float(item.split(",")[1])) == False
        ):
            newlist.append(item)
    getBiggestX = min(getXCordNeighbours(newlist))
    templist = []
    for item in newlist:
        if float((item.split(",")[0])) == getBiggestX:
            templist.append(item)
    getSmallestY = min(getYCordNeighbours(templist))
    return str(getBiggestX) + "," + str(getSmallestY)


def getNeighboursDirectional(direction, maincord, list):
    finallist = []
    xcord = float(maincord.split(",")[0])
    ycord = float(maincord.split(",")[1])
    if direction == 1:
        # All points towards left of X
        finallist = [x for x in list if float(x.split(",")[0]) <= xcord]
    elif direction == 2:
        # All points towards bottom of Y
        finallist = [x for x in list if float(x.split(",")[1]) <= ycord]
    elif direction == 3:
        # All points towards right of X
        finallist = [x for x in list if float(x.split(",")[0]) >= xcord]
    elif direction == 4:
        # All points towar s top of Y
        finallist = [x for x in list if float(x.split(",")[1]) >= ycord]
    return finallist


def getLeftPoint(cord, globaldata, hashtable):
    val = hashtable.index(cord)
    leftpt = globaldata[val - 1][3]
    if isinstance(leftpt, int):
        return hashtable[leftpt]
    else:
        return hashtable.index(leftpt)


def getRightPoint(cord, globaldata, hashtable):
    val = hashtable.index(cord)
    rightpt = globaldata[val - 1][4]
    if isinstance(rightpt, int):
        return hashtable[rightpt]
    else:
        return hashtable.index(rightpt)


def setFlagValue(index, flagindex, value, globaldata):
    globaldata[index][flagindex] = value
    return globaldata


def takeFirst(elem):
    return elem[0]


def euclideanDistance(a, b):
    ax = float(a.split(",")[0])
    ay = float(a.split(",")[1])
    bx = float(b.split(",")[0])
    by = float(b.split(",")[1])
    return (float(math.sqrt(((bx - ax) ** 2) + ((by - ay) ** 2))), a)


def appendNeighbours(neighbours, index, globaldata):
    nbhcount = int(globaldata[index][11])
    nbhs = globaldata[index][-nbhcount:]
    nbhs = nbhs + neighbours
    nbhcount = nbhcount + len(neighbours)
    globaldata[index][11] = nbhcount
    globaldata[index] = globaldata[index][:12] + nbhs
    return "Done"


def cleanWallPoints(neighbours, wallpoint):
    return list(set(neighbours) - set(wallpoint))


def generateReplacement(hashtable, globaldata):
    print("Beginning Replacement")
    coresavail = multiprocessing.cpu_count()
    globalchunks = list(chunks(globaldata, coresavail))
    print("Found", coresavail, "available core(s).")
    print("BOOSTU BOOSTU BOOSTU")
    t1 = time.clock()
    pool = ThreadPool(coresavail)
    results = []
    for itm in globalchunks:
        results.append(pool.apply_async(replacer, args=(hashtable, itm)))
    pool.close()
    pool.join()
    results = [r.get() for r in results]
    globaldata = []
    stuff = []
    for itm in results:
        stuff = stuff + itm
    globaldata = stuff
    t2 = time.clock()
    print(t2 - t1)
    print("Replacement Done")
    return globaldata


def replacer(hashtable, globaldata):
    for index, individualitem in enumerate(globaldata):
        for index2, morestuff in enumerate(individualitem):
            try:
                b = hashtable.index(morestuff)
            except ValueError:
                "Do nothing"
            else:
                globaldata[index][index2] = b
    return globaldata


def isNonAeroDynamic(index, cordpt, globaldata, wallpoints):
    main_point = getPoint(index, globaldata)
    main_pointx = float(main_point.split(",")[0])
    main_pointy = float(main_point.split(",")[1])
    cordptx = float(cordpt.split(",")[0])
    cordpty = float(cordpt.split(",")[1])
    line = shapely.geometry.LineString([[main_pointx, main_pointy], [cordptx, cordpty]])
    responselist = []
    for item in wallpoints:
        polygonpts = []
        for item2 in item:
            polygonpts.append([float(item2.split(",")[0]), float(item2.split(",")[1])])
        polygontocheck = shapely.geometry.Polygon(polygonpts)
        merged = linemerge([polygontocheck.boundary, line])
        borders = unary_union(merged)
        polygons = polygonize(borders)
        i = 0
        for p in polygons:
            i = i + 1
        if i == 1:
            responselist.append(False)
        else:
            responselist.append(True)
    if True in responselist:
        return True
    else:
        return False


def nonAeroCheck(index, globaldata, wallpoints):
    cordnbhs = getNeighbours(index, globaldata)
    for itm in cordnbhs:
        if isNonAeroDynamic(index, itm, globaldata, wallpoints):
            print("Warning this point", index, "has a non aerodynamic point")
            writeLog(["Warning this point", index, "has a non aerodynamic point"])


def perpendicularDistance(pta, ptb, main_point):
    ptax = float(pta.split(",")[0])
    ptay = float(pta.split(",")[1])
    ptbx = float(ptb.split(",")[0])
    ptby = float(ptb.split(",")[1])
    main_pointx = float(main_point.split(",")[0])
    main_pointy = float(main_point.split(",")[1])
    top = abs(
        ((ptby - ptay) * main_pointx)
        - ((ptbx - ptax) * main_pointy)
        + (ptbx * ptay)
        - (ptax * ptby)
    )
    bottom = euclideanDistance(pta, ptb)
    return float(top / bottom[0])


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]
