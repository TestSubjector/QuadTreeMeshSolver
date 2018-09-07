import numpy as np
import math
import shapely.geometry
from shapely import wkt
from shapely.ops import linemerge, unary_union, polygonize
from progress import printProgressBar
import config
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())


def appendNeighbours(index, globaldata, newpts):
    pt = getIndexFromPoint(newpts, globaldata)
    nbhs = getNeighbours(index, globaldata)
    nbhs = nbhs + [pt]
    nbhs = list(set(nbhs))
    globaldata[int(index)][15:] = nbhs
    globaldata[int(index)][14] = len(nbhs)
    return globaldata


def getFlag(indexval, list):
    indexval = int(indexval)
    return int(list[indexval][5])


def getNeighbours(index, globaldata):
    index = int(index)
    ptdata = globaldata[index]
    ptdata = ptdata[15:]
    return ptdata


def getIndexFromPoint(pt, globaldata):
    ptx = float(pt.split(",")[0])
    pty = float(pt.split(",")[1])
    for itm in globaldata:
        if str(itm[1]) == str(ptx) and str(itm[2]) == str(pty):
            return int(itm[0])

def convertPointsToIndex(pointarray,globaldata):
    ptlist = []
    for itm in pointarray:
        idx = getIndexFromPoint(itm,globaldata)
        ptlist.append(idx)
    return ptlist


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


def deltaY(ycord, orgycord):
    return float(orgycord - ycord)


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


def checkConditionNumber(index, globaldata, threshold):
    xpos = getWeightedInteriorConditionValueofXPos(index, globaldata)
    xneg = getWeightedInteriorConditionValueofXNeg(index, globaldata)
    ypos = getWeightedInteriorConditionValueofYPos(index, globaldata)
    yneg = getWeightedInteriorConditionValueofYNeg(index, globaldata)
    dSPointXPos = getDXPosPoints(index, globaldata)
    dSPointXNeg = getDXNegPoints(index, globaldata)
    dSPointYPos = getDYPosPoints(index, globaldata)
    dSPointYNeg = getDYNegPoints(index, globaldata)
    if (
        xneg > threshold
        or len(dSPointXNeg) < 2 or len(dSPointXPos) < 2 or len(dSPointYNeg) < 2 or len(dSPointYPos) < 2 
        or math.isnan(xneg)
        or xpos > threshold
        or math.isnan(xpos)
        or ypos > threshold
        or math.isnan(ypos)
        or yneg > threshold
        or math.isnan(yneg)
    ):
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

def checkConditionNumberWall(index, globaldata, threshold):
    xpos = getWeightedInteriorConditionValueofXPos(index, globaldata)
    xneg = getWeightedInteriorConditionValueofXNeg(index, globaldata)
    ypos = getWeightedInteriorConditionValueofYPos(index, globaldata)
    yneg = getWeightedInteriorConditionValueofYNeg(index, globaldata)
    dSPointXPos = getDXPosPoints(index, globaldata)
    dSPointXNeg = getDXNegPoints(index, globaldata)
    dSPointYPos = getDYPosPoints(index, globaldata)
    dSPointYNeg = getDYNegPoints(index, globaldata)
    if (
        index == 1561
    ):
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
    log.info("Beginning Duplicate Neighbour Detection")
    for i in range(len(globaldata)):
        if i == 0:
            continue
        noneighours = int(globaldata[i][14])
        cordneighbours = globaldata[i][-noneighours:]
        result = []
        for item in cordneighbours:
            try:
                if int(item) == i:
                    continue
            except BaseException:
                print(i)
            if str(item) not in result:
                result.append(str(item))
        cordneighbours = result

        noneighours = len(cordneighbours)
        globaldata[i] = globaldata[i][:14] + [noneighours] + list(cordneighbours)
    log.info("Duplicate Neighbours Removed")
    return globaldata


def fixXPosMain(index, globaldata, threshold, wallpoints, control):
    if control > 0:
        return
    else:
        control = control + 1
    currentnbhs = getNeighbours(index, globaldata)
    currentnbhs = [int(x) for x in currentnbhs]
    conditionNumber = getWeightedInteriorConditionValueofXPos(index, globaldata)
    numberofxpos = getDXPosPoints(index, globaldata)
    if conditionNumber > threshold or len(numberofxpos) < 3:
        totalnbhs = []
        for itm in currentnbhs:
            nbhofnbh = getNeighbours(int(itm), globaldata)
            nbhofnbh = [int(x) for x in nbhofnbh]
            totalnbhs = totalnbhs + nbhofnbh
        totalnbhs = list(set(totalnbhs) - set([index]) - set(currentnbhs))
        totalnbhs = getDXPosPointsFromSet(index, globaldata, totalnbhs)
        if len(totalnbhs) > 0:
            conditionSet = []
            for ptcheck in totalnbhs:
                if not isNonAeroDynamic(index,ptcheck,globaldata,wallpoints):
                    checkset = [ptcheck] + numberofxpos
                    newcheck = weightedConditionValueForSetOfPoints(
                        index, globaldata, checkset
                    )
                    if newcheck < conditionNumber:
                        conditionSet.append([ptcheck, newcheck])
            if len(conditionSet) > 0:
                conditionSet.sort(key=lambda x: x[1])
                if not isNonAeroDynamic(index,conditionSet[0][0],globaldata,wallpoints):
                    globaldata = appendNeighbours(index, globaldata, conditionSet[0][0])
                    fixXPosMain(index, globaldata, threshold, wallpoints, control)
            else:
                None
    return globaldata


def fixXNegMain(index, globaldata, threshold, wallpoints, control):
    if control > 0:
        return
    else:
        control = control + 1
    currentnbhs = getNeighbours(index, globaldata)
    currentnbhs = [int(x) for x in currentnbhs]
    conditionNumber = getWeightedInteriorConditionValueofXNeg(index, globaldata)
    numberofxpos = getDXNegPoints(index, globaldata)
    if conditionNumber > threshold or len(numberofxpos) < 3:
        totalnbhs = []
        for itm in currentnbhs:
            nbhofnbh = getNeighbours(int(itm), globaldata)
            nbhofnbh = [int(x) for x in nbhofnbh]
            totalnbhs = totalnbhs + nbhofnbh
        totalnbhs = list(set(totalnbhs) - set([index]) - set(currentnbhs))
        totalnbhs = getDXNegPointsFromSet(index, globaldata, totalnbhs)
        if len(totalnbhs) > 0:
            conditionSet = []
            for ptcheck in totalnbhs:
                if not isNonAeroDynamic(index,ptcheck,globaldata,wallpoints):
                    checkset = [ptcheck] + numberofxpos
                    newcheck = weightedConditionValueForSetOfPoints(
                        index, globaldata, checkset
                    )
                    if newcheck < conditionNumber:
                        conditionSet.append([ptcheck, newcheck])
            if len(conditionSet) > 0:
                conditionSet.sort(key=lambda x: x[1])
                if not isNonAeroDynamic(index,conditionSet[0][0],globaldata,wallpoints):
                    globaldata = appendNeighbours(index, globaldata, conditionSet[0][0])
                    fixXNegMain(index, globaldata, threshold, wallpoints, control)
            else:
                None
    return globaldata


def fixYPosMain(index, globaldata, threshold, wallpoints, control):
    if control > 0:
        return
    else:
        control = control + 1
    currentnbhs = getNeighbours(index, globaldata)
    currentnbhs = [int(x) for x in currentnbhs]
    conditionNumber = getWeightedInteriorConditionValueofYPos(index, globaldata)
    numberofxpos = getDYPosPoints(index, globaldata)
    if conditionNumber > threshold or len(numberofxpos) < 3:
        totalnbhs = []
        for itm in currentnbhs:
            nbhofnbh = getNeighbours(int(itm), globaldata)
            nbhofnbh = [int(x) for x in nbhofnbh]
            totalnbhs = totalnbhs + nbhofnbh
        totalnbhs = list(set(totalnbhs) - set([index]) - set(currentnbhs))
        totalnbhs = getDYPosPointsFromSet(index, globaldata, totalnbhs)
        if len(totalnbhs) > 0:
            conditionSet = []
            for ptcheck in totalnbhs:
                if not isNonAeroDynamic(index,ptcheck,globaldata,wallpoints):
                    checkset = [ptcheck] + numberofxpos
                    newcheck = weightedConditionValueForSetOfPoints(
                        index, globaldata, checkset
                    )
                    if newcheck < conditionNumber:
                        conditionSet.append([ptcheck, newcheck])
            if len(conditionSet) > 0:
                conditionSet.sort(key=lambda x: x[1])
                if not isNonAeroDynamic(index,conditionSet[0][0],globaldata,wallpoints):
                    globaldata = appendNeighbours(index, globaldata, conditionSet[0][0])
                    fixYPosMain(index, globaldata, threshold, wallpoints, control)
            else:
                None
    return globaldata


def fixYNegMain(index, globaldata, threshold, wallpoints, control):
    if control > 0:
        return
    else:
        control = control + 1
    currentnbhs = getNeighbours(index, globaldata)
    currentnbhs = [int(x) for x in currentnbhs]
    conditionNumber = getWeightedInteriorConditionValueofYNeg(index, globaldata)
    numberofxpos = getDYNegPoints(index, globaldata)
    if conditionNumber > threshold or len(numberofxpos) < 3:
        totalnbhs = []
        for itm in currentnbhs:
            nbhofnbh = getNeighbours(int(itm), globaldata)
            nbhofnbh = [int(x) for x in nbhofnbh]
            totalnbhs = totalnbhs + nbhofnbh
        totalnbhs = list(set(totalnbhs) - set([index]) - set(currentnbhs))
        totalnbhs = getDYNegPointsFromSet(index, globaldata, totalnbhs)
        if len(totalnbhs) > 0:
            conditionSet = []
            for ptcheck in totalnbhs:
                if not isNonAeroDynamic(index,ptcheck,globaldata,wallpoints):
                    checkset = [ptcheck] + numberofxpos
                    newcheck = weightedConditionValueForSetOfPoints(
                        index, globaldata, checkset
                    )
                    if newcheck < conditionNumber:
                        conditionSet.append([ptcheck, newcheck])
            if len(conditionSet) > 0:
                conditionSet.sort(key=lambda x: x[1])
                if not isNonAeroDynamic(index,conditionSet[0][0],globaldata,wallpoints):
                    globaldata = appendNeighbours(index, globaldata, conditionSet[0][0])
                    fixYNegMain(index, globaldata, threshold, wallpoints, control)
            else:
                None
    return globaldata


def setFlags(index, globaldata, threshold):
    dxpos = getWeightedInteriorConditionValueofXPos(index, globaldata)
    dxneg = getWeightedInteriorConditionValueofXNeg(index, globaldata)
    dypos = getWeightedInteriorConditionValueofYPos(index, globaldata)
    dyneg = getWeightedInteriorConditionValueofYNeg(index, globaldata)
    if dxpos > threshold:
        globaldata[index][7] = 1
    if dxneg > threshold:
        globaldata[index][8] = 1
    if dypos > threshold:
        globaldata[index][9] = 1
    if dyneg > threshold:
        globaldata[index][10] = 1
    return globaldata

def isNonAeroDynamic(index, cordpt, globaldata, wallpoints):
    main_pointx,main_pointy = getPoint(index, globaldata)
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


def getLeftandRightPoint(index,globaldata):
    index = int(index)
    ptdata = globaldata[index]
    leftpt = ptdata[3]
    rightpt = ptdata[4]
    nbhs = []
    nbhs.append(leftpt)
    nbhs.append(rightpt)
    return nbhs

def replaceNeighbours(index,nbhs,globaldata):
    data = globaldata[index]
    data = data[:14]
    data.append(len(nbhs))
    data = data + nbhs
    globaldata[index] = data
    return globaldata

def cleanWallPoints(globaldata):
    wallpoints = getWallPointArrayIndex(globaldata)
    wallpointsflat = [item for sublist in wallpoints for item in sublist]
    for idx,itm in enumerate(globaldata):
        printProgressBar(
            idx, len(globaldata) - 1, prefix="Progress:", suffix="Complete", length=50
        )
        if(idx > 0):
            if(getFlag(idx,globaldata) == 0):
                nbhcords =  getNeighbours(idx,globaldata)
                leftright = getLeftandRightPoint(idx,globaldata)
                nbhcords = list(map(int, nbhcords))
                finalcords = wallRemovedNeighbours(nbhcords,wallpointsflat)
                leftright = list(map(int,leftright))
                if idx not in getWallEndPoints(globaldata):
                    finalcords = finalcords + leftright
                globaldata = replaceNeighbours(idx,finalcords,globaldata)
    return globaldata

        
def wallRemovedNeighbours(points,wallpoints):
    new_list = [fruit for fruit in points if fruit not in wallpoints]
    return new_list

def getWallEndPoints(globaldata):
    wallIndex = getWallPointArrayIndex(globaldata)
    endPoints = []
    for itm in wallIndex:
        endPoints.append(int(itm[-1]))
    return endPoints