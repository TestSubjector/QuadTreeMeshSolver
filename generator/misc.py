
import math
import shapely.geometry
from shapely import wkt
from shapely.ops import linemerge, unary_union, polygonize
import os
import errno
import multiprocessing
from multiprocessing.pool import ThreadPool
import time

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def silentRemove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise

def cleanNeighbours(globaldata):  # Verified
    log.info("Beginning Duplicate Neighbour Detection")
    for i in range(len(globaldata)):
        try:
            noneighours = int(globaldata[i][20])  # Number of neighbours
        except IndexError:
            log.warn("No neighbours found for index " + str(i))
            noneighbours = 0
        try:
            cordneighbours = globaldata[i][-noneighours:]
        except:
            print(globaldata[i])
            log.warn("No neighbours found for index " + str(i))
        cordneighbours = [str(float(j.split(",")[0])) + "," + str(float(j.split(",")[1])) for j in cordneighbours]
        
        result = []
        for item in cordneighbours:
            if str(item) not in result:
                result.append(str(item))
        cordneighbours = result
        noneighours = len(cordneighbours)
        globaldata[i] = globaldata[i][:20] + [noneighours] + list(cordneighbours)
    log.info("Duplicate Neighbours Removed")
    return globaldata

def getPoint(indexval, list):
    currentcord = str(list[indexval][1]) + "," + str(list[indexval][2])
    return currentcord

def getIndexOf(pointxy, hashtable):
    return int(hashtable.index(pointxy)) - 1

def getNeighbours(indexval, list):
    val = []
    pointdata = list[indexval]
    numbneigh = int(pointdata[20])
    try:
        for i in range(numbneigh):
            val = val + [str(pointdata[i + 21])]
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
    maxCurr = 0
    currIdx = 0
    for item in list:
        if (
            isPositive(float(item.split(",")[0])) == True
            and isPositive(float(item.split(",")[1])) == True
        ):
            newlist.append(item)
    for itm in newlist:
        itmx = float(itm.split(",")[0])
        itmy = float(itm.split(",")[1])
        itmx = itmx * itmx
        itmy = itmy * itmy
        itmdist = (itmx + itmy) ** 0.5
        if maxCurr < itmdist:
            maxCurr = itmdist
            currIdx = itm
    return currIdx

def getSmallestXBiggestY(list):
    newlist = []
    maxCurr = 0
    currIdx = 0
    for item in list:
        if (
            isPositive(float(item.split(",")[0])) == False
            and isPositive(float(item.split(",")[1])) == True
        ):
            newlist.append(item)
    for itm in newlist:
        itmx = float(itm.split(",")[0])
        itmy = float(itm.split(",")[1])
        itmx = itmx * itmx
        itmy = itmy * itmy
        itmdist = (itmx + itmy) ** 0.5
        if maxCurr < itmdist:
            maxCurr = itmdist
            currIdx = itm
    return currIdx

def getBiggestXSmallestY(list):
    newlist = []
    maxCurr = 0
    currIdx = 0
    for item in list:
        if (
            isPositive(float(item.split(",")[0])) == True
            and isPositive(float(item.split(",")[1])) == False
        ):
            newlist.append(item)
    for itm in newlist:
        itmx = float(itm.split(",")[0])
        itmy = float(itm.split(",")[1])
        itmx = itmx * itmx
        itmy = itmy * itmy
        itmdist = (itmx + itmy) ** 0.5
        if maxCurr < itmdist:
            maxCurr = itmdist
            currIdx = itm
    return currIdx

def getSmallestXSmallestY(list):
    newlist = []
    maxCurr = 0
    currIdx = 0
    for item in list:
        if (
            isPositive(float(item.split(",")[0])) == False
            and isPositive(float(item.split(",")[1])) == False
        ):
            newlist.append(item)
    for itm in newlist:
        itmx = float(itm.split(",")[0])
        itmy = float(itm.split(",")[1])
        itmx = itmx * itmx
        itmy = itmy * itmy
        itmdist = (itmx + itmy) ** 0.5
        if maxCurr < itmdist:
            maxCurr = itmdist
            currIdx = itm
    return currIdx

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
    nbhcount = int(globaldata[index][20])
    nbhs = globaldata[index][-nbhcount:]
    nbhs = nbhs + neighbours
    nbhcount = nbhcount + len(neighbours)
    globaldata[index][20] = nbhcount
    globaldata[index] = globaldata[index][:21] + nbhs
    return globaldata

def cleanWallPoints(neighbours, wallpoint):
    return list(set(neighbours) - set(wallpoint))

def generateReplacement(hashtable, globaldata):
    log.info("Beginning Replacement")
    coresavail = multiprocessing.cpu_count()
    log.info("Found " + str(coresavail) + " available core(s).")
    log.info("BOOSTU BOOSTU BOOSTU")
    MAX_CORES = int(core.getConfig()["generator"]["maxCoresForReplacement"])
    log.info("Max Cores Allowed " + str(MAX_CORES))
    t1 = time.clock()
    pool = ThreadPool(min(MAX_CORES,coresavail))
    results = []
    chunksize = math.ceil(len(globaldata)/min(MAX_CORES,coresavail))
    globalchunks = list(chunks(globaldata,chunksize))
    hashtable = {k:v for v,k in enumerate(hashtable)}
    globalchunks = list(chunks(globaldata, chunksize))
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
    log.info(t2 - t1)
    log.info("Replacement Done")
    return globaldata

def replacer(hashtable, globaldata):
    for index, individualitem in enumerate(globaldata):
        for index2, morestuff in enumerate(individualitem):
            try:
                b = hashtable[morestuff]
            except KeyError:
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

def distFromOrigin(pt):
    ptx = float(pt.split(",")[0])
    pty = float(pt.split(",")[1])
    dist = ((ptx * ptx) + (pty * pty)) ** 0.5
    return dist

def getFarthestPoint(listpts):
    currentdist = 0
    currentpt = 0
    for itm in listpts:
        dist = distFromOrigin(itm)
        if dist > currentdist:
            currentdist = dist
            currentpt = itm
    return currentpt
