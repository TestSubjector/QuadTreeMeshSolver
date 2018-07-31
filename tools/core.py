import numpy as np
import math
from progress import printProgressBar
import shapely.geometry
from shapely import wkt
from shapely.ops import linemerge, unary_union, polygonize
from shapely.geometry import Polygon,Point
import config
import logging
import multiprocessing
from multiprocessing.pool import ThreadPool
import time
import os
import errno
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

def appendNeighbours(index, globaldata, newpts):
    pt = getIndexFromPoint(newpts, globaldata)
    nbhs = getNeighbours(index, globaldata)
    nbhs = nbhs + [pt]
    nbhs = list(set(nbhs))
    globaldata[int(index)][12:] = nbhs
    globaldata[int(index)][11] = len(nbhs)
    return globaldata


def getFlag(indexval, list):
    indexval = int(indexval)
    return int(list[indexval][5])


def getNeighbours(index, globaldata):
    index = int(index)
    ptdata = globaldata[index]
    ptdata = ptdata[12:]
    return ptdata

def getLeftandRightPoint(index,globaldata):
    index = int(index)
    ptdata = globaldata[index]
    leftpt = ptdata[3]
    rightpt = ptdata[4]
    nbhs = []
    nbhs.append(getPointxy(leftpt,globaldata))
    nbhs.append(getPointxy(rightpt,globaldata))
    return nbhs

def getIndexFromPoint(pt, globaldata):
    ptx = float(pt.split(",")[0])
    pty = float(pt.split(",")[1])
    for itm in globaldata:
        if itm[1] == str(ptx) and itm[2] == str(pty):
            return int(itm[0])


def getPoint(index, globaldata):
    index = int(index)
    ptdata = globaldata[index]
    ptx = float(ptdata[1])
    pty = float(ptdata[2])
    return ptx, pty


def getPointxy(index, globaldata):
    index = int(index)
    ptx, pty = getPoint(index, globaldata)
    return str(ptx) + "," + str(pty)


def convertIndexToPoints(indexarray, globaldata):
    ptlist = []
    for item in indexarray:
        item = int(item)
        ptx, pty = getPoint(item, globaldata)
        ptlist.append((str(ptx) + "," + str(pty)))
    return ptlist


def weightedConditionValueForSetOfPoints(index, globaldata, points):
    index = int(index)
    mainptx = float(globaldata[index][1])
    mainpty = float(globaldata[index][2])
    deltaSumXX = 0
    deltaSumYY = 0
    deltaSumXY = 0
    data = []
    nbhs = points
    for nbhitem in nbhs:
        nbhitemX = float(nbhitem.split(",")[0])
        nbhitemY = float(nbhitem.split(",")[1])
        deltaX = nbhitemX - mainptx
        deltaY = nbhitemY - mainpty
        d = math.sqrt(deltaX ** 2 + deltaY ** 2)
        if d == 0:
            continue
        power = int(config.getConfig()["global"]["weightCondition"])
        w = d ** power
        deltaSumXX = deltaSumXX + w * (deltaX ** 2)
        deltaSumYY = deltaSumYY + w * (deltaY ** 2)
        deltaSumXY = deltaSumXY + w * (deltaX) * (deltaY)
    data.append(deltaSumXX)
    data.append(deltaSumXY)
    data.append(deltaSumXY)
    data.append(deltaSumYY)
    random = np.array(data)
    shape = (2, 2)
    random = random.reshape(shape)
    s = np.linalg.svd(random, full_matrices=False, compute_uv=False)
    s = max(s) / min(s)
    return s


def deltaX(xcord, orgxcord):
    return float(orgxcord - xcord)

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


def deltaY(ycord, orgycord):
    return float(orgycord - ycord)

def normalCalculation(index, globaldata, wallpoint):
    nx = 0
    ny = 0
    cordx = float(globaldata[index][1])
    cordy = float(globaldata[index][2])
    pointdata = globaldata[index]
    leftpoint = getPointxy(pointdata[3], globaldata)
    rightpoint = getPointxy(pointdata[4], globaldata)
    leftpointx = float(leftpoint.split(",")[0])
    leftpointy = float(leftpoint.split(",")[1])
    rightpointx = float(rightpoint.split(",")[0])
    rightpointy = float(rightpoint.split(",")[1])
    if not wallpoint:
        nx1 = leftpointy - cordy
        nx2 = cordy - rightpointy
        ny1 = leftpointx - cordx
        ny2 = cordx - rightpointx
    else:
        nx1 = cordy - leftpointy
        nx2 = rightpointy - cordy
        ny1 = cordx - leftpointx
        ny2 = rightpointx - cordx
    nx = (nx1 + nx2) / 2
    ny = (ny1 + ny2) / 2
    det = math.sqrt((nx * nx) + (ny * ny))
    if not wallpoint:
        nx = nx / det
    else:
        direction = config.getConfig()["global"]["wallPointOrientation"]
        if direction == "cw":
            nx = (-nx) / det
        elif direction == "ccw":
            nx = nx / det
    ny = ny / det
    return nx, ny

def weightedConditionValueForSetOfPointsNormal(index, globaldata, nbh):
    nx,ny = normalCalculation(index,globaldata,True)
    mainptx = float(globaldata[index][1])
    mainpty = float(globaldata[index][2])
    nx = float(nx)
    ny = float(ny)
    tx = float(ny)
    ty = -float(nx)
    deltaSumS = 0
    deltaSumN = 0
    deltaSumSN = 0
    data = []
    for nbhitem in nbh:
        nbhitemX = float(nbhitem.split(",")[0])
        nbhitemY = float(nbhitem.split(",")[1])
        deltaS = (tx * (nbhitemX - mainptx)) + (ty * (nbhitemY - mainpty))
        deltaN = (nx * (nbhitemX - mainptx)) + (ny * (nbhitemY - mainpty))
        d = math.sqrt(deltaS ** 2 + deltaN ** 2)
        if d == 0:
            continue
        power = int(config.getConfig()["global"]["weightCondition"])
        w = d ** power
        deltaSumS = deltaSumS + w * (deltaS) ** 2
        deltaSumN = deltaSumN + w * (deltaN) ** 2
        deltaSumSN = deltaSumSN + w * (deltaS) * (deltaN)
    data.append(deltaSumS)
    data.append(deltaSumSN)
    data.append(deltaSumSN)
    data.append(deltaSumN)
    random = np.array(data)
    shape = (2, 2)
    random = random.reshape(shape)
    s = np.linalg.svd(random, full_matrices=False, compute_uv=False)
    s = max(s) / min(s)
    return s

def deltaWallNeighbourCalculation(
    index, currentneighbours, nx, ny, giveposdelta, globaldata
):
    deltaspos, deltasneg, deltaszero = 0, 0, 0
    nx = float(nx)
    ny = float(ny)
    tx = float(ny)
    ty = -float(nx)
    xcord = float(globaldata[index][1])
    ycord = float(globaldata[index][2])
    output = []
    for item in currentneighbours:
        itemx = float(item.split(",")[0])
        itemy = float(item.split(",")[1])
        deltas = (tx * (itemx - xcord)) + (ty * (itemy - ycord))
        if deltas <= 0:
            if giveposdelta:
                output.append(item)
            deltaspos = deltaspos + 1
        if deltas >= 0:
            if not giveposdelta:
                output.append(item)
            deltasneg = deltasneg + 1
        if deltas == 0:
            deltaszero = deltaszero + 1
    return deltaspos, deltasneg, deltaszero, output


def deltaNeighbourCalculation(currentneighbours, currentcord, isxcord, isnegative):
    xpos, xneg, ypos, yneg = 0, 0, 0, 0
    temp = []
    for item in currentneighbours:
        if (deltaX(float(currentcord.split(",")[0]), float(item.split(",")[0]))) <= 0:
            if isxcord and (not isnegative):
                temp.append(item)
            xpos = xpos + 1
        if (deltaX(float(currentcord.split(",")[0]), float(item.split(",")[0]))) >= 0:
            if isxcord and isnegative:
                temp.append(item)
            xneg = xneg + 1
        if (deltaY(float(currentcord.split(",")[1]), float(item.split(",")[1]))) <= 0:
            if (not isxcord) and (not isnegative):
                temp.append(item)
            ypos = ypos + 1
        if (deltaY(float(currentcord.split(",")[1]), float(item.split(",")[1]))) >= 0:
            if (not isxcord) and isnegative:
                temp.append(item)
            yneg = yneg + 1
    return xpos, ypos, xneg, yneg, temp

def getWeightedNormalConditionValueofWallXPos(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    nx,ny = normalCalculation(index,globaldata,True)
    _, _, _, mypoints = deltaWallNeighbourCalculation(index,
        nbhs,nx,ny, True, globaldata
    )
    return weightedConditionValueForSetOfPointsNormal(index, globaldata, mypoints)


def getWeightedNormalConditionValueofWallXNeg(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    nx,ny = normalCalculation(index,globaldata,True)
    _, _, _, mypoints = deltaWallNeighbourCalculation(index,
        nbhs,nx,ny, False, globaldata
    )
    return weightedConditionValueForSetOfPointsNormal(index, globaldata, mypoints)



def getWeightedInteriorConditionValueofXPos(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, False
    )
    return weightedConditionValueForSetOfPoints(index, globaldata, mypoints)


def getWeightedInteriorConditionValueofXNeg(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, True
    )
    return weightedConditionValueForSetOfPoints(index, globaldata, mypoints)


def getWeightedInteriorConditionValueofYPos(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, False
    )
    return weightedConditionValueForSetOfPoints(index, globaldata, mypoints)


def getWeightedInteriorConditionValueofYNeg(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, True
    )
    return weightedConditionValueForSetOfPoints(index, globaldata, mypoints)


def getDXPosPoints(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, False
    )
    return mypoints


def getDXNegPoints(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, True
    )
    return mypoints

def getDWallXPosPoints(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    nx,ny = normalCalculation(index,globaldata,True)
    _, _, _, mypoints = deltaWallNeighbourCalculation(index,
        nbhs,nx,ny, True, globaldata
    )
    return mypoints


def getDWallXNegPoints(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    nx,ny = normalCalculation(index,globaldata,True)
    _, _, _, mypoints = deltaWallNeighbourCalculation(index,
        nbhs,nx,ny, False, globaldata
    )
    return mypoints



def getDYPosPoints(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, False
    )
    return mypoints


def getDYNegPoints(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, True
    )
    return mypoints


def getDXPosPointsFromSet(index, globaldata, points):
    nbhs = convertIndexToPoints(points, globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, False
    )
    return mypoints


def getDXNegPointsFromSet(index, globaldata, points):
    nbhs = convertIndexToPoints(points, globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, True
    )
    return mypoints


def getDYPosPointsFromSet(index, globaldata, points):
    nbhs = convertIndexToPoints(points, globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, False
    )
    return mypoints


def getDYNegPointsFromSet(index, globaldata, points):
    nbhs = convertIndexToPoints(points, globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, True
    )
    return mypoints

def getDXPosPointsFromSetRaw(index, globaldata, points):
    nbhs = points
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, False
    )
    return mypoints


def getDXNegPointsFromSetRaw(index, globaldata, points):
    nbhs = points
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, True
    )
    return mypoints


def getDYPosPointsFromSetRaw(index, globaldata, points):
    nbhs = points
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, False
    )
    return mypoints


def getDYNegPointsFromSetRaw(index, globaldata, points):
    nbhs = points
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, True
    )
    return mypoints

def getDWallXPosPointsFromSetRaw(index, globaldata, points):
    nbhs = points
    nx,ny = normalCalculation(index,globaldata,True)
    _, _, _, mypoints = deltaWallNeighbourCalculation(index,
        nbhs,nx,ny, True, globaldata
    )
    return mypoints


def getDWallXNegPointsFromSetRaw(index, globaldata, points):
    nbhs = points
    nx,ny = normalCalculation(index,globaldata,True)
    _, _, _, mypoints = deltaWallNeighbourCalculation(index,
        nbhs,nx,ny, False, globaldata
    )
    return mypoints


def checkConditionNumber(index, globaldata, threshold):
    xpos = getWeightedInteriorConditionValueofXPos(index, globaldata)
    xneg = getWeightedInteriorConditionValueofXNeg(index, globaldata)
    ypos = getWeightedInteriorConditionValueofYPos(index, globaldata)
    yneg = getWeightedInteriorConditionValueofYNeg(index, globaldata)
    dSPointXPos = getDXPosPoints(index, globaldata)
    dSPointXNeg = getDXNegPoints(index, globaldata)
    dSPointYPos = getDYPosPoints(index, globaldata)
    dSPointYNeg = getDYNegPoints(index, globaldata)
    if xneg > threshold or xpos > threshold or ypos > threshold or yneg > threshold:
        print(
            index,
            len(dSPointXPos),
            xpos,
            len(dSPointXNeg),
            xneg,
            len(dSPointYPos),
            ypos,
            len(dSPointYNeg),
            yneg,
        )


def cleanNeighbours(globaldata):
    print("Beginning Duplicate Neighbour Detection")
    for i in range(len(globaldata)):
        if i == 0:
            continue
        noneighours = int(globaldata[i][11])
        cordneighbours = globaldata[i][-noneighours:]
        result = []
        for item in cordneighbours:
            if int(item) == i:
                continue
            if str(item) not in result:
                result.append(str(item))
        cordneighbours = result

        noneighours = len(cordneighbours)
        globaldata[i] = globaldata[i][:11] + [noneighours] + list(cordneighbours)
    print("Duplicate Neighbours Removed")
    return globaldata


def convertPointToShapelyPoint(pointarry):
    pointnewarry = []
    for itm in pointarry:
        xcord = float(itm.split(",")[0])
        ycord = float(itm.split(",")[1])
        pointnewarry.append((xcord, ycord))
    return pointnewarry

def getWallPointArray(globaldata):
    wallpointarray = []
    startgeo = 0
    newstuff = []
    for idx,itm in enumerate(globaldata):
        if idx > 0:
            geoflag = int(itm[6])
            if(startgeo == geoflag and getFlag(idx,globaldata) == 0):
                newstuff.append(getPointxy(idx,globaldata))
            if(startgeo != geoflag and getFlag(idx,globaldata) == 0):
                newstuff = []
                wallpointarray.append(newstuff)
                newstuff.append(getPointxy(idx,globaldata))
                startgeo = startgeo + 1
    return wallpointarray

def getWallPointArrayIndex(globaldata):
    wallpointarray = []
    startgeo = 0
    newstuff = []
    for idx,itm in enumerate(globaldata):
        if idx > 0:
            geoflag = int(itm[6])
            if(startgeo == geoflag and getFlag(idx,globaldata) == 0):
                newstuff.append(idx)
            if(startgeo != geoflag and getFlag(idx,globaldata) == 0):
                newstuff = []
                wallpointarray.append(newstuff)
                newstuff.append(idx)
                startgeo = startgeo + 1
    return wallpointarray

def isNonAeroDynamic(index, cordpt, globaldata, wallPolygonData):
    main_pointx,main_pointy = getPoint(index, globaldata)
    cordptx = float(cordpt.split(",")[0])
    cordpty = float(cordpt.split(",")[1])
    line = shapely.geometry.LineString([[main_pointx, main_pointy], [cordptx, cordpty]])
    responselist = []
    for polygontocheck in wallPolygonData:
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

def generateWallPolygons(wallpoints):
    wallPolygonData = []
    for item in wallpoints:
        polygonpts = []
        for item2 in item:
            polygonpts.append([float(item2.split(",")[0]), float(item2.split(",")[1])])
        polygontocheck = shapely.geometry.Polygon(polygonpts)
        wallPolygonData.append(polygontocheck)
    return wallPolygonData

def getAeroPointsFromSet(index,cordlist,globaldata,wallpoints):
    finallist = []
    for itm in cordlist:
        if isNonAeroDynamic(index,itm,globaldata,wallpoints) == False:
            finallist.append(itm)
    return finallist

def setFlags(index,globaldata,flags):
    globaldata[index][7] = flags[0]
    globaldata[index][8] = flags[1]
    globaldata[index][9] = flags[2]
    globaldata[index][10] = flags[3]
    return globaldata

def getFlags(index,globaldata):
    flagxpos = int(globaldata[index][7])
    flagxneg = int(globaldata[index][8])
    flagypos = int(globaldata[index][9])
    flagyneg = int(globaldata[index][10])
    return flagxpos,flagxneg,flagypos,flagyneg

def getConditionNumber(index, globaldata):
    xpos = getWeightedInteriorConditionValueofXPos(index, globaldata)
    xneg = getWeightedInteriorConditionValueofXNeg(index, globaldata)
    ypos = getWeightedInteriorConditionValueofYPos(index, globaldata)
    yneg = getWeightedInteriorConditionValueofYNeg(index, globaldata)
    result = {"xpos":xpos,"xneg":xneg,"ypos":ypos,"yneg":yneg}
    return result

def getConditionNumberNormal(index,globaldata):
    xpos = getWeightedNormalConditionValueofWallXPos(index,globaldata)
    xneg = getWeightedNormalConditionValueofWallXNeg(index,globaldata)
    result = {"xpos":xpos,"xneg":xneg,"ypos":"NA","yneg":"NA"}
    return result

def replaceNeighbours(index,nbhs,globaldata):
    data = globaldata[index]
    data = data[:11]
    data.append(len(nbhs))
    data = data + nbhs
    globaldata[index] = data
    return globaldata

def convertPointsToIndex(pointarray,globaldata):
    ptlist = []
    for itm in pointarray:
        idx = getIndexFromPoint(itm,globaldata)
        ptlist.append(idx)
    return ptlist

def fillNeighboursIndex(index,globaldata,nbhs):
    nbhs = list(set(nbhs))
    globaldata[int(index)][12:] = nbhs
    globaldata[int(index)][11] = len(nbhs)
    return globaldata

def checkAeroGlobal2(globaldata,wallpointsData):
    coresavail = multiprocessing.cpu_count()
    log.info("Found " + str(coresavail) + " available core(s).")
    log.info("BOOSTU BOOSTU BOOSTU")
    MAX_CORES = int(config.getConfig()["generator"]["maxCoresForReplacement"])
    log.info("Max Cores Allowed " + str(MAX_CORES))
    t1 = time.clock()
    pool = ThreadPool(min(MAX_CORES,coresavail))
    results = []
    chunksize = math.ceil(len(globaldata)/min(MAX_CORES,coresavail))
    globalchunks = list(chunks(globaldata,chunksize))
    for itm in globalchunks:
        results.append(pool.apply_async(checkAeroGlobal, args=(itm, globaldata,wallpointsData)))
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

def checkAeroGlobal(chunk,globaldata,wallpointsData):
    # t1 = time.clock()
    for index,itm in enumerate(chunk):
        if itm is not "start":
            idx = itm[0]
            # printProgressBar(idx, len(globaldata) - 1, prefix="Progress:", suffix="Complete", length=50)    
            nbhs = getNeighbours(idx,globaldata)
            nonaeronbhs = []
            for itm in nbhs:
                cord = getPointxy(itm,globaldata)
                if isNonAeroDynamic(idx,cord,globaldata,wallpointsData):
                    nonaeronbhs.append(itm)
            finalnbhs = list(set(nbhs) - set(nonaeronbhs))
            if(len(nbhs) != len(finalnbhs)):
                chunk = fillNeighboursIndex(index,chunk,finalnbhs)
                log.debug("Point %s has a non aero point with index %s",idx,itm)
    # t2 = time.clock()
    # log.info(t2 - t1)
    return chunk

def silentRemove(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred

def getSquarePlot(x, y, side):
    return [(x+(side/2), y+(side/2)), (x-(side/2), y+(side/2)), (x-(side/2), y-(side/2)), (x+(side/2), y-(side/2))]

def findHeadOfWall(wallpoints):
    headPts = []
    for wallptset in wallpoints:
        minx = 1000
        currpt = 0
        for pt in wallptset:
            ptx = float(pt.split(",")[0])
            pty = float(pt.split(",")[1])
            if minx > ptx:
                minx = ptx
                currpt = pt
        headPts.append(currpt)
    return headPts

def returnPointDist(globaldata):
    stats = {"interior":0,"outer":0,"wall":0}
    for idx,itm in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            if flag == 1:
                stats["interior"] = stats["interior"] + 1
            elif flag == 2:
                stats["outer"] = stats["outer"] + 1
            else:
                stats["wall"] = stats["wall"] + 1
    return stats

def createBoxPolygon(wallpoints):
    BOX_SIDE_SIZE = float(config.getConfig()["box"]["boxSideLength"])
    headData = findHeadOfWall(wallpoints)
    boxData = []
    for itm in headData:
        x = float(itm.split(",")[0])
        y = float(itm.split(",")[1])
        squareData = getSquarePlot(x,y,BOX_SIDE_SIZE)
        squarePoly = Polygon(squareData)
        boxData.append(squarePoly)
    return boxData[:1]

def findBoxAdaptPoints(globaldata,wallpoints):
    boxPoly = createBoxPolygon(wallpoints)
    adaptPoints = []
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            ptx,pty = getPoint(idx,globaldata)
            pt = (ptx,pty)
            pt = Point(pt)
            for boxP in boxPoly:
                if boxP.intersects(pt):
                    adaptPoints.append(idx)
    return adaptPoints

def getBoxPlot(XRange,YRange):
    return [(XRange[0],YRange[0]),(XRange[0],YRange[1]),(XRange[1],YRange[1]),(XRange[1],YRange[0])]

def findGeneralBoxAdaptPoints(globaldata):
    XRange = tuple(config.getConfig()["box"]["XRange"])
    YRange = tuple(config.getConfig()["box"]["YRange"])
    boxPoly = getBoxPlot(XRange,YRange)
    boxPoly = Polygon(boxPoly)
    adaptPoints = []
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            ptx,pty = getPoint(idx,globaldata)
            pt = (ptx,pty)
            pt = Point(pt)
            if boxPoly.intersects(pt):
                adaptPoints.append(idx)
    return adaptPoints

def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False
    else:
         raise ValueError

def findAverageWallDistance(globaldata,wallpoints):
    result = {"max":0,"min":100000000,"total":0,"sum":0,"avg":0}
    flat_list = (item for sublist in wallpoints for item in sublist)
    flat_list = tuple(map(int,flat_list))
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            nbhs = tuple(getNeighbours(idx,globaldata))
            nbhs = tuple(map(int,nbhs))
            nbhs = set(nbhs).intersection(set(flat_list))
            for itm in nbhs:
                dist = getDistance(idx,itm,globaldata)
                result["total"] = result["total"] + 1
                result["sum"] = result["sum"] + dist
                if dist < result["min"]:
                    result["min"] = dist
                if dist > result["max"]:
                    result["max"] = dist
    result["avg"] = result["sum"] / result["total"]
    return result

def getDistance(point1,point2,globaldata):
    ptax,ptay = getPoint(point1,globaldata)
    ptbx,ptby = getPoint(point2,globaldata)
    ptx = deltaX(ptax,ptbx)**2
    pty = deltaY(ptay,ptby)**2
    result = math.sqrt(ptx + pty)
    return result

def wallConnectivityCheck(globaldata):
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            if flag == 0:
                xpos,xneg,_,_ = getFlags(idx,globaldata)
                if xpos == 1 or xneg == 1:
                    print(idx) 
                    ptcordx, ptcordy = getPoint(idx,globaldata)
                    with open("adapted.txt", "a+") as text_file:
                        text_file.writelines(["%s %s " % (ptcordx, ptcordy)])
                        text_file.writelines("\n")
    with open("adapted.txt", "a+") as text_file:
        text_file.writelines("1000 1000\n")