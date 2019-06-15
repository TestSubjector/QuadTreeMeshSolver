import numpy as np
import os, errno, multiprocessing, math, logging, itertools, json, time, re, shutil, csv, redis, uuid
import shapely.geometry
from shapely.ops import linemerge, unary_union, polygonize
import shapely
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
from tqdm import tqdm
from multiprocessing.pool import ThreadPool
from collections import Counter
from time import sleep
from scipy.interpolate import splprep, splev
from scipy import spatial

def appendNeighbours(index, globaldata, newpts):
    pt = getIndexFromPoint(newpts, globaldata)
    nbhs = getNeighbours(index, globaldata)
    nbhs = nbhs + [pt]
    nbhs = list(set(nbhs))
    globaldata[int(index)][20:] = nbhs
    globaldata[int(index)][19] = len(nbhs)
    return globaldata

def getFlag(indexval, list):
    indexval = int(indexval)
    return int(list[indexval][5])

def setFlagsFromList(index,globaldata,flags):
    globaldata[index][7] = flags[0]
    globaldata[index][8] = flags[1]
    globaldata[index][9] = flags[2]
    globaldata[index][10] = flags[3]
    return globaldata

def setFlags(index, globaldata, threshold, configData):
    dxpos = getWeightedInteriorConditionValueofXPos(index, globaldata, configData)
    dxneg = getWeightedInteriorConditionValueofXNeg(index, globaldata, configData)
    dypos = getWeightedInteriorConditionValueofYPos(index, globaldata, configData)
    dyneg = getWeightedInteriorConditionValueofYNeg(index, globaldata, configData)
    if dxpos > threshold:
        globaldata[index][7] = 1
    if dxneg > threshold:
        globaldata[index][8] = 1
    if dypos > threshold:
        globaldata[index][9] = 1
    if dyneg > threshold:
        globaldata[index][10] = 1
    return globaldata

def getFlags(index,globaldata):
    flagxpos = int(globaldata[index][7])
    flagxneg = int(globaldata[index][8])
    flagypos = int(globaldata[index][9])
    flagyneg = int(globaldata[index][10])
    return flagxpos,flagxneg,flagypos,flagyneg

def getNeighbours(index, globaldata):
    index = int(index)
    ptdata = globaldata[index]
    ptdata = list(map(int, list(ptdata[20:])))
    return ptdata

def getIndexFromPoint(pt, globaldata):
    ptx = float(pt.split(",")[0])
    pty = float(pt.split(",")[1])
    for itm in globaldata:
        if str(itm[1]) == str(ptx) and str(itm[2]) == str(pty):
            return int(itm[0])

def getIndexFromPointTuple(pt, globaldata):
    ptx = pt[0]
    pty = pt[1]
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


def getWeightedInteriorConditionValueofXPos(index, globaldata, configData):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, False
    )
    return weightedConditionValueForSetOfPoints(index, globaldata, mypoints, configData)


def getWeightedInteriorConditionValueofXNeg(index, globaldata, configData):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, True
    )
    return weightedConditionValueForSetOfPoints(index, globaldata, mypoints, configData)


def getWeightedInteriorConditionValueofYPos(index, globaldata, configData):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, False
    )
    return weightedConditionValueForSetOfPoints(index, globaldata, mypoints, configData)


def getWeightedInteriorConditionValueofYNeg(index, globaldata, configData):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, True
    )
    return weightedConditionValueForSetOfPoints(index, globaldata, mypoints, configData)


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


def getDWallXPosPoints(index, globaldata, configData):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    nx,ny = normalCalculation(index,globaldata,True, configData)
    _, _, _, mypoints = deltaWallNeighbourCalculation(index,
        nbhs,nx,ny, True, globaldata
    )
    return mypoints


def getDWallXNegPoints(index, globaldata, configData):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    nx,ny = normalCalculation(index,globaldata,True, configData)
    _, _, _, mypoints = deltaWallNeighbourCalculation(index,
        nbhs,nx,ny, False, globaldata
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


def getDYPosPointsFromSetRaw(index, globaldata, points, configData):
    nbhs = points
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, False
    )
    return mypoints


def getDYNegPointsFromSetRaw(index, globaldata, points, configData):
    nbhs = points
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, True
    )
    return mypoints

def getDWallXPosPointsFromSetRaw(index, globaldata, points, configData):
    nbhs = points
    nx,ny = normalCalculation(index,globaldata,True, configData)
    _, _, _, mypoints = deltaWallNeighbourCalculation(index,
        nbhs,nx,ny, True, globaldata
    )
    return mypoints


def getDWallXNegPointsFromSetRaw(index, globaldata, points, configData):
    nbhs = points
    nx,ny = normalCalculation(index,globaldata,True, configData)
    _, _, _, mypoints = deltaWallNeighbourCalculation(index,
        nbhs,nx,ny, False, globaldata
    )
    return mypoints


def checkConditionNumber(index, globaldata, threshold, configData):
    xpos = getWeightedInteriorConditionValueofXPos(index, globaldata, configData)
    xneg = getWeightedInteriorConditionValueofXNeg(index, globaldata, configData)
    ypos = getWeightedInteriorConditionValueofYPos(index, globaldata, configData)
    yneg = getWeightedInteriorConditionValueofYNeg(index, globaldata, configData)
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
        # print(index)
        # print(xpos,xneg,ypos,yneg)
        return True
    else:
        return False

def checkConditionNumberWall(index, globaldata, threshold, configData):
    xpos = getWeightedInteriorConditionValueofXPos(index, globaldata, configData)
    xneg = getWeightedInteriorConditionValueofXNeg(index, globaldata, configData)
    ypos = getWeightedInteriorConditionValueofYPos(index, globaldata, configData)
    yneg = getWeightedInteriorConditionValueofYNeg(index, globaldata, configData)
    dSPointXPos = getDXPosPoints(index, globaldata)
    dSPointXNeg = getDXNegPoints(index, globaldata)
    dSPointYPos = getDYPosPoints(index, globaldata)
    dSPointYNeg = getDYNegPoints(index, globaldata)
    if (
        index == 2061
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

def checkConditionNumberLogger(index, globaldata, threshold, configData):
    xpos = getWeightedInteriorConditionValueofXPos(index, globaldata, configData)
    xneg = getWeightedInteriorConditionValueofXNeg(index, globaldata, configData)
    ypos = getWeightedInteriorConditionValueofYPos(index, globaldata, configData)
    yneg = getWeightedInteriorConditionValueofYNeg(index, globaldata, configData)
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
        return True
    else:
        return False

def cleanNeighbours(globaldata):
    log.info("Beginning Duplicate Neighbour Detection")
    for i in range(len(globaldata)):
        if i == 0:
            continue
        noneighours = int(globaldata[i][19])
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
        globaldata[i] = globaldata[i][:19] + [noneighours] + list(cordneighbours)
    log.info("Duplicate Neighbours Removed")
    return globaldata


def fixXPosMain(index, globaldata, threshold, wallpoints, control, configData):
    if control > 0:
        return
    else:
        control = control + 1
    currentnbhs = getNeighbours(index, globaldata)
    currentnbhs = [int(x) for x in currentnbhs]
    conditionNumber = getWeightedInteriorConditionValueofXPos(index, globaldata, configData)
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
                        index, globaldata, checkset, configData
                    )
                    if newcheck < conditionNumber:
                        conditionSet.append([ptcheck, newcheck])
            if len(conditionSet) > 0:
                conditionSet.sort(key=lambda x: x[1])
                if not isNonAeroDynamic(index,conditionSet[0][0],globaldata,wallpoints):
                    globaldata = appendNeighbours(index, globaldata, conditionSet[0][0])
                    fixXPosMain(index, globaldata, threshold, wallpoints, control, configData)
            else:
                None
    return globaldata


def fixXNegMain(index, globaldata, threshold, wallpoints, control, configData):
    if control > 0:
        return
    else:
        control = control + 1
    currentnbhs = getNeighbours(index, globaldata)
    currentnbhs = [int(x) for x in currentnbhs]
    conditionNumber = getWeightedInteriorConditionValueofXNeg(index, globaldata, configData)
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
                        index, globaldata, checkset, configData
                    )
                    if newcheck < conditionNumber:
                        conditionSet.append([ptcheck, newcheck])
            if len(conditionSet) > 0:
                conditionSet.sort(key=lambda x: x[1])
                if not isNonAeroDynamic(index,conditionSet[0][0],globaldata,wallpoints):
                    globaldata = appendNeighbours(index, globaldata, conditionSet[0][0])
                    fixXNegMain(index, globaldata, threshold, wallpoints, control, configData)
            else:
                None
    return globaldata


def fixYPosMain(index, globaldata, threshold, wallpoints, control, configData):
    if control > 0:
        return
    else:
        control = control + 1
    currentnbhs = getNeighbours(index, globaldata)
    currentnbhs = [int(x) for x in currentnbhs]
    conditionNumber = getWeightedInteriorConditionValueofYPos(index, globaldata, configData)
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
                        index, globaldata, checkset, configData
                    )
                    if newcheck < conditionNumber:
                        conditionSet.append([ptcheck, newcheck])
            if len(conditionSet) > 0:
                conditionSet.sort(key=lambda x: x[1])
                if not isNonAeroDynamic(index,conditionSet[0][0],globaldata,wallpoints):
                    globaldata = appendNeighbours(index, globaldata, conditionSet[0][0])
                    fixYPosMain(index, globaldata, threshold, wallpoints, control, configData)
            else:
                None
    return globaldata


def fixYNegMain(index, globaldata, threshold, wallpoints, control, configData):
    if control > 0:
        return
    else:
        control = control + 1
    currentnbhs = getNeighbours(index, globaldata)
    currentnbhs = [int(x) for x in currentnbhs]
    conditionNumber = getWeightedInteriorConditionValueofYNeg(index, globaldata, configData)
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
                        index, globaldata, checkset, configData
                    )
                    if newcheck < conditionNumber:
                        conditionSet.append([ptcheck, newcheck])
            if len(conditionSet) > 0:
                conditionSet.sort(key=lambda x: x[1])
                if not isNonAeroDynamic(index,conditionSet[0][0],globaldata,wallpoints):
                    globaldata = appendNeighbours(index, globaldata, conditionSet[0][0])
                    fixYNegMain(index, globaldata, threshold, wallpoints, control, configData)
            else:
                None
    return globaldata

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
        deltan = (nx * (itemx - xcord)) + (ny * (itemy - ycord))
        # if(index==730):
        #     print(deltas)
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
    if getFlag(index, globaldata) == 2:
        None
        # print(index,len(currentneighbours),deltaspos,deltasneg,deltaszero)
    return deltaspos, deltasneg, deltaszero, output

def deltaWallNeighbourCalculationN(
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
        deltas = (nx * (itemx - xcord)) + (ny * (itemy - ycord))
        # if(index==730):
        #     print(deltas)
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
    if getFlag(index, globaldata) == 2:
        None
        # print(index,len(currentneighbours),deltaspos,deltasneg,deltaszero)
    return deltaspos, deltasneg, deltaszero, output

def weightedConditionValueForSetOfPointsNormalWithInputs(index, globaldata, nbh, nx, ny, configData):
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
        power = int(configData["global"]["weightCondition"])
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

def weightedConditionValueForSetOfPointsNormal(index, globaldata, nbh, configData):
    nx,ny = normalCalculation(index,globaldata,True, configData)
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
        power = int(configData["global"]["weightCondition"])
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

def weightedConditionValueForSetOfPoints(index, globaldata, points, configData):
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
        power = int(configData["global"]["weightCondition"])
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

def getWeightedNormalConditionValueofWallXPos(index, globaldata, configData):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    nx,ny = normalCalculation(index,globaldata,True, configData)
    _, _, _, mypoints = deltaWallNeighbourCalculation(index,
        nbhs,nx,ny, True, globaldata
    )
    return weightedConditionValueForSetOfPointsNormal(index, globaldata, mypoints, configData)


def getWeightedNormalConditionValueofWallXNeg(index, globaldata, configData):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    nx,ny = normalCalculation(index,globaldata,True, configData)
    _, _, _, mypoints = deltaWallNeighbourCalculation(index,
        nbhs,nx,ny, False, globaldata
    )
    return weightedConditionValueForSetOfPointsNormal(index, globaldata, mypoints, configData)

def isNonAeroDynamic(index, cordpt, globaldata, wallData):
    main_pointx,main_pointy = getPoint(index, globaldata)
    cordptx = float(cordpt.split(",")[0])
    cordpty = float(cordpt.split(",")[1])
    line = shapely.geometry.LineString([[main_pointx, main_pointy], [cordptx, cordpty]])
    responselist = []

    if len(wallData) == 0:
        return False

    if isinstance(wallData[0], shapely.geometry.Polygon):
        return nonAeroDynamicPolygonHelper(line, wallData)
    else:
        return nonAeroDynamicPointHelper(line, wallData)

def nonAeroDynamicPointHelper(line, wallData):
    responselist = []
    for item in wallData:
        polygonpts = []
        for item2 in item:
            polygonpts.append([float(item2.split(",")[0]), float(item2.split(",")[1])])
        polygontocheck = shapely.geometry.Polygon(polygonpts)
        merged = linemerge([polygontocheck.boundary, line])
        borders = unary_union(merged)
        polygons = polygonize(borders)
        i = 0
        for _ in polygons:
            i += 1
        if i == 1:
            responselist.append(False)
        else:
            responselist.append(True)
    if True in responselist:
        return True
    else:
        return False

def nonAeroDynamicPolygonHelper(line, wallPolygonData):
    responselist = []
    for polygontocheck in wallPolygonData:
        merged = linemerge([polygontocheck.boundary, line])
        borders = unary_union(merged)
        polygons = polygonize(borders)
        i = 0
        for _ in polygons:
            i = i + 1
        if i == 1:
            responselist.append(False)
        else:
            responselist.append(True)
    if True in responselist:
        return True
    else:
        return False

def isNonAeroDynamicBetter(index, cordpt, globaldata, wallpoints):
    main_pointx,main_pointy = getPoint(index, globaldata)
    cordptx = float(cordpt.split(",")[0])
    cordpty = float(cordpt.split(",")[1])
    line = shapely.geometry.LineString([[main_pointx, main_pointy], [cordptx, cordpty]])
    responselist = []
    for item in wallpoints:
        merged = linemerge([item.boundary, line])
        borders = unary_union(merged)
        polygons = polygonize(borders)
        i = 0
        for _ in polygons:
            i += 1
        if i == 1:
            responselist.append(False)
        else:
            return True
    if True in responselist:
        return True
    else:
        return False

def wallDistance(cordpt, wallpoints):
    point = shapely.geometry.Point((cordpt[0], cordpt[1]))
    distance = []
    for item in wallpoints:
        distance.append(point.distance(item))
    return distance

def getNearestWallPoint(cordpt, wallpoints, limit=5):
    result = sorted(wallpoints, key=lambda pt: distancePoint(tuple(map(float, pt.split(","))), cordpt))
    return result[:limit]

def convertToShapely(wallpoints):
    wallPointsShapely = []
    for item in wallpoints:
        polygonpts = []
        for item2 in item:
            polygonpts.append([float(item2.split(",")[0]), float(item2.split(",")[1])])
        polygontocheck = shapely.geometry.Polygon(polygonpts)
        wallPointsShapely.append(polygontocheck)
    return wallPointsShapely

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

def getInteriorPointArrayIndex(globaldata):
    interiorarray = []
    for idx, _ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx, globaldata)
            if flag == 1:
                interiorarray.append(idx)
    return interiorarray


def flattenList(ptdata):
    return list(itertools.chain.from_iterable(ptdata))


def getLeftandRightPoint(index,globaldata):
    index = int(index)
    ptdata = globaldata[index]
    leftpt = ptdata[3]
    rightpt = ptdata[4]
    nbhs = []
    nbhs.append(getPointxy(leftpt,globaldata))
    nbhs.append(getPointxy(rightpt,globaldata))
    return nbhs

def getLeftandRightPointIndex(index,globaldata):
    index = int(index)
    ptdata = globaldata[index]
    leftpt = ptdata[3]
    rightpt = ptdata[4]
    nbhs = []
    nbhs.append(leftpt)
    nbhs.append(rightpt)
    return nbhs

def getLeftPoint(index, globaldata):
    index = int(index)
    ptdata = globaldata[index]
    return ptdata[3]

def getPointExcludeOuter(index, globaldata):
    if getFlag(index, globaldata) != 2:
        index = int(index)
        ptdata = globaldata[index]
        ptx = float(ptdata[1])
        pty = float(ptdata[2])
        return (ptx, pty)
    else:
        return (False, False)

def replaceNeighbours(index,nbhs,globaldata):
    data = globaldata[index]
    data = data[:19]
    data.append(len(nbhs))
    data = data + nbhs
    globaldata[index] = data
    return globaldata

def cleanWallPoints(globaldata):
    wallpoints = getWallPointArrayIndex(globaldata)
    wallpointsflat = [item for sublist in wallpoints for item in sublist]
    for idx,itm in enumerate(tqdm(globaldata)):
        if(idx > 0):
            if(getFlag(idx,globaldata) == 0):
                nbhcords =  getNeighbours(idx,globaldata)
                leftright = getLeftandRightPointIndex(idx,globaldata)
                nbhcords = list(map(int, nbhcords))
                finalcords = wallRemovedNeighbours(nbhcords,wallpointsflat)
                leftright = list(map(int,leftright))
                if idx not in getWallEndPoints(globaldata):
                    finalcords = finalcords + leftright
                globaldata = replaceNeighbours(idx,finalcords,globaldata)
    return globaldata

def cleanWallPointsSelectivity(globaldata,points):
    wallpoints = getWallPointArrayIndex(globaldata)
    wallpointsflat = [item for sublist in wallpoints for item in sublist]
    for idx in points:
        if(getFlag(idx,globaldata) == 0):
            nbhcords =  getNeighbours(idx,globaldata)
            leftright = getLeftandRightPointIndex(idx,globaldata)
            nbhcords = list(map(int, nbhcords))
            finalcords = wallRemovedNeighbours(nbhcords,wallpointsflat)
            finalcords = list(set(finalcords))
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

def getMaxDepth(globaldata):
    maxDepth = 0
    for idx in range(1, len(globaldata)):
        depth = getDepth(idx, globaldata)
        if depth > maxDepth:
            maxDepth = depth
    return maxDepth

def containsWallPoints(globaldata, idx, wallpts):
    nbhs = getNeighbours(idx, globaldata)
    S1 = set(nbhs)
    S2 = set(wallpts)
    if len(S1.intersection(S2)) == 0:
        return False
    else:
        return True


def checkPoints(globaldata, selectbspline, normal, configData, pseudocheck, shapelyWallData):
    wallptData = getWallPointArray(globaldata)
    wallptDataOr = wallptData
    wallptData = flattenList(wallptData)
    ptsToBeAdded = int(configData["bspline"]["pointControl"])
    ptListArray = []
    perpendicularListArray = []
    maxDepth = -999
    badpts = []
    if pseudocheck:
        maxDepth = getMaxDepth(globaldata)
    if not selectbspline:
        for idx,_ in enumerate(tqdm(globaldata)):
            if idx > 0:
                flag = getFlag(idx,globaldata)
                if flag == 1:
                    if configData['bspline']['wallGuard']:
                        if containsWallPoints(globaldata, idx, wallptData):
                            continue
                    result = isConditionBad(idx,globaldata, configData)
                    nancheck = isConditionNan(idx, globaldata, configData)
                    if nancheck:
                        log.warn("Warning: Point Index {} has a NaN. Manual Intervention is required to fix it.".format(idx))
                    else:
                        if(result):
                            ptList = findNearestNeighbourWallPoints(idx,globaldata,wallptData,shapelyWallData)
                            perpendicularPt = getPerpendicularPoint(idx,globaldata,normal, shapelyWallData, ptList)
                            if (perpendicularPt) not in perpendicularListArray:
                                ptListArray.append(ptList)
                                perpendicularListArray.append((perpendicularPt))
                                badpts.append(idx)
                        else:
                            if pseudocheck:
                                px, py = getPoint(idx, globaldata)
                                depth = getDepth(idx, globaldata)
                                if depth <= maxDepth - 3:
                                    dist = min(wallDistance((px, py), shapelyWallData))
                                    if dist <= float(configData['bspline']['pseudoDist']):
                                        ptList = findNearestNeighbourWallPoints(idx,globaldata,wallptData,shapelyWallData)
                                        perpendicularPt = getPerpendicularPoint(idx,globaldata,normal, shapelyWallData, ptList)
                                        if (perpendicularPt) not in perpendicularListArray:
                                            ptListArray.append(ptList)
                                            perpendicularListArray.append((perpendicularPt))
                                            badpts.append(idx)

    else:
        selectbspline = list(map(int, selectbspline))
        for idx,itm in enumerate(tqdm(selectbspline)):
            ptList = findNearestNeighbourWallPoints(itm, globaldata, wallptData, shapelyWallData)
            perpendicularPt = getPerpendicularPoint(itm, globaldata, normal, shapelyWallData, ptList)
            if (perpendicularPt) not in perpendicularListArray:
                ptListArray.append(ptList)
                perpendicularListArray.append((perpendicularPt))
                badpts.append(itm)

    return ptListArray, perpendicularListArray, badpts

def findNearestNeighbourWallPoints(idx, globaldata, wallptData, shapelyWallData):
    ptx,pty = getPoint(idx,globaldata)
    leastdt,leastidx = 1000,-9999
    # for itm in wallptData:
    #     if not isNonAeroDynamicBetter(idx,itm,globaldata,shapelyWallData):
    #         itmx = float(itm.split(",")[0])
    #         itmy = float(itm.split(",")[1])
    #         ptDist = math.sqrt((deltaX(itmx,ptx) ** 2) + (deltaY(itmy,pty) ** 2))
    #         if leastdt > ptDist:
    #             leastdt = ptDist
    #             leastidx = getIndexFromPoint(itm,globaldata)
    better = getNearestWallPoint((ptx, pty), wallptData, limit=10)
    for itm in better:
        if not isNonAeroDynamicBetter(idx,itm,globaldata,shapelyWallData):
            itmx = float(itm.split(",")[0])
            itmy = float(itm.split(",")[1])
            ptDist = math.sqrt((deltaX(itmx,ptx) ** 2) + (deltaY(itmy,pty) ** 2))
            if leastdt > ptDist:
                leastdt = ptDist
                leastidx = getIndexFromPoint(itm,globaldata)
    if leastidx == -9999:
        log.error("Failed to find nearest wallpoint")
        exit()
    ptsToCheck = convertIndexToPoints(getLeftandRightPointIndex(leastidx,globaldata),globaldata)

    leastidx2 = -9999
    leastptx,leastpty = getPoint(leastidx,globaldata)
    currangle = 1000
    for itm in ptsToCheck:
        if not isNonAeroDynamicBetter(idx,itm,globaldata,shapelyWallData):
            itmx = float(itm.split(",")[0])
            itmy = float(itm.split(",")[1])
            ptDist = math.sqrt((deltaX(itmx,ptx) ** 2) + (deltaY(itmy,pty) ** 2))
            anglecal = angle(ptx,pty,leastptx,leastpty,itmx,itmy)
            if currangle == 1000:
                currangle = anglecal
                leastidx2 = getIndexFromPoint(itm,globaldata)
            elif anglecal < currangle:
                currangle = anglecal
                leastidx2 = getIndexFromPoint(itm,globaldata)
    if leastidx > leastidx2 and leastidx2 != 1:
        leastidx,leastidx2 = leastidx2,leastidx
    if leastidx == 1 and leastidx2 > 1:
        leastidx,leastidx2 = leastidx2,leastidx
    return convertIndexToPoints([leastidx,leastidx2],globaldata)

# def findNearestNeighbourWallPoints(idx,globaldata,wallptData,wallptDataOr):
#     ptx,pty = getPoint(idx,globaldata)
#     leastdt,leastidx = 1000,1000
#     for itm in wallptData:
#         if not isNonAeroDynamic(idx,itm,globaldata,wallptDataOr):
#             itmx = float(itm.split(",")[0])
#             itmy = float(itm.split(",")[1])
#             ptDist = math.sqrt((deltaX(itmx,ptx) ** 2) + (deltaY(itmy,pty) ** 2))
#             if leastdt > ptDist:
#                 leastdt = ptDist
#                 leastidx = getIndexFromPoint(itm,globaldata)
#     ptsToCheck = convertIndexToPoints(getLeftandRightPoint(leastidx,globaldata),globaldata)
#     leastdt2,leastidx2 = 1000,1000
#     leastptx,leastpty = getPoint(leastidx,globaldata)
#     currangle = 1000
#     for itm in ptsToCheck:
#         if not isNonAeroDynamic(idx,itm,globaldata,wallptDataOr):
#             itmx = float(itm.split(",")[0])
#             itmy = float(itm.split(",")[1])
#             ptDist = math.sqrt((deltaX(itmx,ptx) ** 2) + (deltaY(itmy,pty) ** 2))
#             anglecal = angle(ptx,pty,leastptx,leastpty,itmx,itmy)
#             if currangle == 1000:
#                 currangle = anglecal
#                 leastidx2 = getIndexFromPoint(itm,globaldata)
#             elif anglecal < currangle:
#                 currangle = anglecal
#                 leastidx2 = getIndexFromPoint(itm,globaldata)
#     if leastidx > leastidx2 and leastidx2 != 1:
#         leastidx,leastidx2 = leastidx2,leastidx
#     if leastidx == 1 and leastidx2 > 1:
#         leastidx,leastidx2 = leastidx2,leastidx
#     return convertIndexToPoints([leastidx,leastidx2],globaldata)

def findNearestNeighbourWallPointsManual(pt,globaldata,wallptData,wallptDataOr):
    ptx,pty = pt[0],pt[1]
    leastdt,leastidx = 1000,1000
    for itm in wallptData:
        itmx = float(itm.split(",")[0])
        itmy = float(itm.split(",")[1])
        ptDist = math.sqrt((deltaX(itmx,ptx) ** 2) + (deltaY(itmy,pty) ** 2))
        if leastdt > ptDist:
            leastdt = ptDist
            leastidx = getIndexFromPoint(itm,globaldata)
    ptsToCheck = convertIndexToPoints(getLeftandRightPointIndex(leastidx,globaldata),globaldata)
    leastdt2,leastidx2 = 1000,1000
    leastptx,leastpty = getPoint(leastidx,globaldata)
    currangle = 1000
    for itm in ptsToCheck:
        itmx = float(itm.split(",")[0])
        itmy = float(itm.split(",")[1])
        ptDist = math.sqrt((deltaX(itmx,ptx) ** 2) + (deltaY(itmy,pty) ** 2))
        anglecal = angle(ptx,pty,leastptx,leastpty,itmx,itmy)
        if currangle == 1000:
            currangle = anglecal
            leastidx2 = getIndexFromPoint(itm,globaldata)
        elif anglecal < currangle:
            currangle = anglecal
            leastidx2 = getIndexFromPoint(itm,globaldata)
    if leastidx > leastidx2 and leastidx2 != 1:
        leastidx,leastidx2 = leastidx2,leastidx
    if leastidx == 1 and leastidx2 > 1:
        leastidx,leastidx2 = leastidx2,leastidx
    return convertIndexToPoints([leastidx,leastidx2],globaldata)

def feederData(wallpts,wallptData):
    wallpt = wallpts[0]
    for idx,itm in enumerate(wallptData):
        if wallpt in itm:
            return [itm.index(wallpts[0]),itm.index(wallpts[1]),idx,wallpt, wallpts[1]]

def undelimitXY(a):
    finallist = []
    for itm in a:
        cord = []
        cord.append(float(itm.split(",")[0]))
        cord.append(float(itm.split(",")[1]))
        finallist.append(cord)
    return finallist

def getPerpendicularPoint(idx, globaldata, normal, shapelyWallData, pts):
    wallptData = getWallPointArray(globaldata)
    wallptDataOr = wallptData
    wallptData = flattenList(wallptData)
    mainpt = getPointxy(idx,globaldata)
    mainptx = float(mainpt.split(",")[0])
    mainpty = float(mainpt.split(",")[1])
    pts1x = float(pts[0].split(",")[0])
    pts1y = float(pts[0].split(",")[1])
    pts2x = float(pts[1].split(",")[0])
    pts2y = float(pts[1].split(",")[1])
    if normal:
        return perpendicularPt(pts1x,pts2x,mainptx,pts1y,pts2y,mainpty)
    else:
        return midPt(pts1x,pts2x,pts1y,pts2y)

# def getPerpendicularPoint(idx,globaldata,normal):
#     wallptData = getWallPointArray(globaldata)
#     wallptDataOr = wallptData
#     wallptData = flattenList(wallptData)
#     pts = findNearestNeighbourWallPoints(idx,globaldata,wallptData,wallptDataOr)
#     mainpt = getPointxy(idx,globaldata)
#     mainptx = float(mainpt.split(",")[0])
#     mainpty = float(mainpt.split(",")[1])
#     pts1x = float(pts[0].split(",")[0])
#     pts1y = float(pts[0].split(",")[1])
#     pts2x = float(pts[1].split(",")[0])
#     pts2y = float(pts[1].split(",")[1])
#     if normal:
#         return perpendicularPt(pts1x,pts2x,mainptx,pts1y,pts2y,mainpty)
#     else:
#         return midPt(pts1x,pts2x,pts1y,pts2y)

def getPerpendicularPointManual(pt,globaldata,normal,quadrant):
    wallptData = getWallPointArray(globaldata)
    wallptDataOr = wallptData
    wallptData = flattenList(wallptData)
    pts = findNearestNeighbourWallPointsManual(pt,globaldata,wallptData,wallptDataOr)
    mainptx = pt[0]
    mainpty = pt[1]
    pts1x = float(pts[0].split(",")[0])
    pts1y = float(pts[0].split(",")[1])
    pts2x = float(pts[1].split(",")[0])
    pts2y = float(pts[1].split(",")[1])
    if normal:
        pptx,ppty = perpendicularPt(pts1x,pts2x,mainptx,pts1y,pts2y,mainpty)
        if quadrantContains(quadrant,(pptx,ppty)):
            return pptx,ppty
        else:
            return None
    else:
        return midPt(pts1x,pts2x,pts1y,pts2y)

def perpendicularPt(x1,x2,x3,y1,y2,y3):
    k = ((y2-y1) * (x3-x1) - (x2-x1) * (y3-y1)) / ((y2-y1)**2 + (x2-x1)**2)
    x4 = x3 - k * (y2-y1)
    y4 = y3 + k * (x2-x1)
    return x4,y4

def midPt(x1,x2,y1,y2):
    x3 = (x1+x2)/2
    y3 = (y1+y2)/2
    return x3,y3

def distance(ax,ay,bx,by):
    return math.sqrt((ax - bx)**2 + (ay - by)**2)

def distancePoint(x, y):
    ax = x[0]
    ay = x[1]
    bx = y[0]
    by = y[1]
    return math.sqrt((ax - bx)**2 + (ay - by)**2)

def undelimitXY(a):
    finallist = []
    for itm in a:
        cord = []
        cord.append(float(itm.split(",")[0]))
        cord.append(float(itm.split(",")[1]))
        finallist.append(cord)
    return finallist

def findNearestPoint(ptAtt,splineArray):
    if len(splineArray) == 0:
        return False
    cord = {"x":0,"y":0}
    dist = distance(ptAtt[0],ptAtt[1],splineArray[0][0],splineArray[0][1])
    cord["x"] = splineArray[0][0]
    cord["y"] = splineArray[0][1]
    for itm in splineArray:
        distcurr = distance(ptAtt[0],ptAtt[1],itm[0],itm[1])
        if distcurr > dist:
            None
        else:
            dist = distcurr
            cord["x"] = itm[0]
            cord["y"] = itm[1]
    return [cord["x"],cord["y"]]

def str_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError


def updateNormals(idx,globaldata,nx,ny):
    globaldata[idx][11] = nx
    globaldata[idx][12] = ny
    return globaldata

def getNormals(idx, globaldata):
    nx = globaldata[idx][11]
    ny = globaldata[idx][12]
    return nx,ny

def setNormals(idx, globaldata, normals):
    globaldata[idx][11] = normals[0] # nx
    globaldata[idx][12] = normals[1] # ny
    return globaldata

def calculateNormalConditionValues(idx,globaldata,nxavg,nyavg, configData):
    nbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
    # print(nbhs)
    _,_,_,dSPosNbhs = deltaWallNeighbourCalculation(idx,nbhs,nxavg,nyavg,True,globaldata)
    _,_,_,dSNegNbhs = deltaWallNeighbourCalculation(idx,nbhs,nxavg,nyavg,False,globaldata)
    _,_,_,dNPosNbhs = deltaWallNeighbourCalculationN(idx,nbhs,nxavg,nyavg,True,globaldata)
    _,_,_,dNNegNbhs = deltaWallNeighbourCalculationN(idx,nbhs,nxavg,nyavg,False,globaldata)

    dSPosCondition = weightedConditionValueForSetOfPointsNormalWithInputs(idx,globaldata,dSPosNbhs,nxavg,nyavg, configData)
    dSNegCondition = weightedConditionValueForSetOfPointsNormalWithInputs(idx,globaldata,dSNegNbhs,nxavg,nyavg, configData)
    dNPosCondition = weightedConditionValueForSetOfPointsNormalWithInputs(idx,globaldata,dNPosNbhs,nxavg,nyavg, configData)
    dNNegCondition = weightedConditionValueForSetOfPointsNormalWithInputs(idx,globaldata,dNNegNbhs,nxavg,nyavg, configData)

    result = {"spos":dSPosNbhs,"sposCond":dSPosCondition,"sneg":dSNegNbhs,"snegCond":dSNegCondition,"npos":dNPosNbhs,"nposCond":dNPosCondition,"nneg":dNNegNbhs,"nnegCond":dNNegCondition}
    return result

def isConditionBad(idx, globaldata, configData):
    nx,ny = getNormals(idx,globaldata)
    condResult = calculateNormalConditionValues(idx,globaldata,nx,ny, configData)
    dSPosNbhs,dSNegNbhs,dNPosNbhs,dNNegNbhs = condResult["spos"], condResult["sneg"], condResult["npos"], condResult["nneg"]
    dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition = condResult["sposCond"], condResult["snegCond"], condResult["nposCond"], condResult["nnegCond"]
    maxCond = max(dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition)
    if maxCond > float(configData["bspline"]["threshold"]) or math.isnan(dSPosCondition) or math.isnan(dSNegCondition) or math.isnan(dNPosCondition) or math.isnan(dNNegCondition):
        return True
    else:
        return False

def isConditionNan(idx, globaldata, configData):
    nx,ny = getNormals(idx,globaldata)
    condResult = calculateNormalConditionValues(idx,globaldata,nx,ny, configData)
    dSPosNbhs,dSNegNbhs,dNPosNbhs,dNNegNbhs = condResult["spos"], condResult["sneg"], condResult["npos"], condResult["nneg"]
    dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition = condResult["sposCond"], condResult["snegCond"], condResult["nposCond"], condResult["nnegCond"]
    maxCond = max(dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition)
    if math.isnan(dSPosCondition) or math.isnan(dSNegCondition) or math.isnan(dNPosCondition) or math.isnan(dNNegCondition):
        return True
    else:
        return False

def isConditionInf(idx, globaldata, configData):
    nx,ny = getNormals(idx,globaldata)
    condResult = calculateNormalConditionValues(idx,globaldata,nx,ny, configData)
    dSPosNbhs,dSNegNbhs,dNPosNbhs,dNNegNbhs = condResult["spos"], condResult["sneg"], condResult["npos"], condResult["nneg"]
    dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition = condResult["sposCond"], condResult["snegCond"], condResult["nposCond"], condResult["nnegCond"]
    maxCond = max(dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition)
    if math.isinf(dSPosCondition) or math.isinf(dSNegCondition) or math.isinf(dNPosCondition) or math.isinf(dNNegCondition):
        return True
    else:
        return False

def angle(x1, y1, x2, y2, x3, y3):
    a = np.array([x1, y1])
    b = np.array([x2, y2])
    c = np.array([x3, y3])

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = math.acos(cosine_angle)

    return np.degrees(angle)

def quadrantContains(quadrant,pt):
    quadpoly = shapely.geometry.Polygon(quadrant)
    ptpoly = shapely.geometry.Point(pt)
    if quadpoly.contains(ptpoly):
        return True
    else:
        return False

def quadrantContainsFaster(quadpoly,pt):
    ptpoly = shapely.geometry.Point(pt)
    if quadpoly.contains(ptpoly):
        return True
    else:
        return False

def getBoundingBoxOfQuadrant(index,globaldata):
    toplx = float(globaldata[index][15])
    toply = float(globaldata[index][16])
    bottomrx = float(globaldata[index][17])
    bottomry = float(globaldata[index][18])
    toprx = bottomrx
    topry = toply
    bottomlx = toplx
    bottomly = bottomry
    topl = (toplx,toply)
    topr = (toprx,topry)
    bottoml = (bottomlx,bottomly)
    bottomr = (bottomrx,bottomry)
    return (topl,topr,bottomr,bottoml)

def getBoundingPointsOfQuadrant(index,globaldata):
    toplx = float(globaldata[index][15])
    toply = float(globaldata[index][16])
    bottomrx = float(globaldata[index][17])
    bottomry = float(globaldata[index][18])
    # topl = (toplx,toply)
    # topr = (toprx,topry)
    # bottoml = (bottomlx,bottomly)
    # bottomr = (bottomrx,bottomry)
    return (toplx,toply,bottomrx,bottomry)

def getNorthWestQuadrant(index,globaldata):
    box = getBoundingBoxOfQuadrant(index,globaldata)
    midx,midy = getCentroidOfQuadrant(index,globaldata)
    topl = box[0]
    bottomr = (midx,midy)
    topr = (bottomr[0],topl[1])
    bottoml = (topl[0],bottomr[1])
    return (topl,topr,bottomr,bottoml)

def getNorthEastQuadrant(index,globaldata):
    box = getBoundingBoxOfQuadrant(index,globaldata)
    midx,midy = getCentroidOfQuadrant(index,globaldata)
    topr = box[1]
    bottoml = (midx,midy)
    topl = (bottoml[0],topr[1])
    bottomr = (topr[0],bottoml[1])
    return (topl,topr,bottomr,bottoml)

def getSouthWestQuadrant(index,globaldata):
    box = getBoundingBoxOfQuadrant(index,globaldata)
    midx,midy = getCentroidOfQuadrant(index,globaldata)
    bottoml = box[3]
    topr = (midx,midy)
    topl = (bottoml[0],topr[1])
    bottomr = (topr[0],bottoml[1])
    return (topl,topr,bottomr,bottoml)

def getSouthEastQuadrant(index,globaldata):
    box = getBoundingBoxOfQuadrant(index,globaldata)
    midx,midy = getCentroidOfQuadrant(index,globaldata)
    bottomr = box[2]
    topl = (midx,midy)
    topr = (bottomr[0],topl[1])
    bottoml = (topl[0],bottomr[1])
    return (topl,topr,bottomr,bottoml)

def getPerpendicularPointsFromQuadrants(index,globaldata):
    NWQ = getNorthWestQuadrant(index,globaldata)
    NEQ = getNorthEastQuadrant(index,globaldata)
    SWQ = getSouthWestQuadrant(index,globaldata)
    SEQ = getSouthEastQuadrant(index,globaldata)
    ptx,pty = getPoint(index,globaldata)
    pt = (ptx,pty)
    if len(set(NWQ)) < 4 or len(set(NEQ)) < 4 or len(set(SEQ)) < 4 or len(set(SWQ)) < 4:
        print("Warning point index: " + str(index) + " has same NW and SE bounding box")
        exit()

    perPoints = []
    walldata = getWallPointArray(globaldata)
    if doesItIntersect(index, NWQ,globaldata,walldata):
        centercord = getCentroidOfQuadrantManual(globaldata, NWQ)
        ppp = None
        # ppp = getPerpendicularPointManual(centercord,globaldata,True,NWQ)
        if ppp is None:
            perPoints.append((centercord,NWQ,pt))
        else:
            perPoints.append((ppp,NWQ,pt))
    if doesItIntersect(index, NEQ,globaldata,walldata):
        centercord = getCentroidOfQuadrantManual(globaldata, NEQ)
        ppp = None
        # ppp = getPerpendicularPointManual(centercord,globaldata,True,NEQ)
        if ppp is None:
            perPoints.append((centercord,NEQ,pt))
        else:
            perPoints.append((ppp,NEQ,pt))
    if doesItIntersect(index, SWQ,globaldata,walldata):
        centercord = getCentroidOfQuadrantManual(globaldata, SWQ)
        ppp = None
        # ppp = getPerpendicularPointManual(centercord,globaldata,True,SWQ)
        if ppp is None:
            perPoints.append((centercord,SWQ,pt))
        else:
            perPoints.append((ppp,SWQ,pt))
    if doesItIntersect(index, SEQ,globaldata,walldata):
        centercord = getCentroidOfQuadrantManual(globaldata, SEQ)
        ppp = None
        # ppp = getPerpendicularPointManual(centercord,globaldata,True,SEQ)
        if ppp is None:
            perPoints.append((centercord,SEQ,pt))
        else:
            perPoints.append((ppp,SEQ,pt))
    return perPoints

def getCentroidOfQuadrant(index,globaldata):
    quadrant = getBoundingBoxOfQuadrant(index,globaldata)
    midx = quadrant[0][0] + quadrant[2][0]
    midx = midx / 2
    midy = quadrant[0][1] + quadrant[2][1]
    midy = midy / 2
    return midx,midy

def getCentroidOfQuadrantManual(globaldata,quadrant):
    midx = quadrant[0][0] + quadrant[2][0]
    midx = midx / 2
    midy = quadrant[0][1] + quadrant[2][1]
    midy = midy / 2
    return midx,midy

def getDepth(idx,globaldata):
    depth = int(globaldata[idx][13])
    return depth

def doesItIntersect(idx, quadrant, globaldata, wallpoints):
    quadrantpoly = shapely.geometry.Polygon(quadrant)
    getPtx,getPty = getPoint(idx,globaldata)
    pttocheck = shapely.geometry.Point([getPtx,getPty])
    responselist = []
    if quadrantpoly.contains(pttocheck):
        responselist.append(False)
    else:
        for item in wallpoints:
            polygonpts = []
            for item2 in item:
                polygonpts.append([float(item2.split(",")[0]), float(item2.split(",")[1])])
            polygontocheck = shapely.geometry.Polygon(polygonpts)
            response = polygontocheck.intersects(quadrantpoly)
            response = True
            if response:
                responselist.append(True)
            else:
                responselist.append(False)
    if True in responselist:
        return True
    else:
        return False

def getWallGeometry(walldata, globaldata, itm):
    itmx, itmy = getPoint(itm, globaldata)
    for idx,itm in enumerate(walldata):
        if [itmx, itmy] in itm:
            return itm

def silentRemove(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred

def normalCalculation(index, globaldata, wallpoint, configData):
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
        direction = configData["global"]["wallPointOrientation"]
        if direction == "cw":
            nx = (-nx) / det
        elif direction == "ccw":
            nx = nx / det
    ny = ny / det
    return nx, ny

def convertPointToShapelyPoint(pointarry):
    pointnewarry = []
    for itm in pointarry:
        xcord = float(itm.split(",")[0])
        ycord = float(itm.split(",")[1])
        pointnewarry.append((xcord, ycord))
    return pointnewarry

def nonAdaptWallPolygon(globaldata, wallpoints, dist, interiorpts, configData):
    print("Creating Inflated Wall Point")
    pseudopts = []
    inflatedWall = []
    for itm in wallpoints:
        idx = getIndexFromPoint(itm,globaldata)
        orgWallpt = getPointxy(idx, globaldata)
        nx, ny = normalCalculation(idx, globaldata, True, configData)
        orgWallptx = float(orgWallpt.split(",")[0])
        orgWallpty = float(orgWallpt.split(",")[1])
        normalVector = np.array([nx, ny])
        orgVector = np.array([orgWallptx, orgWallpty])
        newWallpt = orgVector + dist * normalVector
        newWallpt = tuple(newWallpt.tolist())
        inflatedWall.append(newWallpt)
    wallptsData = convertPointToShapelyPoint(wallpoints)
    wallpointGeo = shapely.geometry.Polygon(wallptsData)
    lastpt = wallptsData[0]
    newpt = (lastpt[0] + dist, lastpt[1])
    inflatedWall.pop(0)
    inflatedWall.insert(0, newpt)
    inflatedwallpointGeo = shapely.geometry.Polygon(inflatedWall)
    print("Checking for Pseudo Points")
    # fig, ax = plt.subplots()
    # x1,y1 = wallpointGeo.exterior.xy
    # x2,y2 = inflatedwallpointGeo.exterior.xy
    # # ax = fig.add_subplot(111)
    # # ax.scatter(x1, y1, color='red', alpha=0.7, zorder=2)
    # # ax.set_title('Polygon')
    # # ax = fig.add_subplot(111)
    # # ax.scatter(x2, y2, color='blue', alpha=0.7, zorder=2)
    # # ax.set_title('Polygon2')
    # # ax = fig.add_subplot(111)
    # ax.plot(x1, y1, color='red', alpha=0.7, zorder=2)
    # ax.plot(x2, y2, color='blue', alpha=0.7, zorder=2)
    # plt.show()
    for itm in interiorpts:
        itmval = convertPointToShapelyPoint(convertIndexToPoints([itm], globaldata))[0]
        interiorpoint = shapely.geometry.Point(itmval)
        if inflatedwallpointGeo.contains(interiorpoint):
            pseudopts.append(itm)
    print("Found", len(pseudopts), "points which aren't gonna be adapted!")
    with open("pseudopoints.txt", "a") as text_file:
        for item1 in pseudopts:
            text_file.writelines(str(item1))
            text_file.writelines("\t\n")
    return pseudopts

def createEdgeCircle(globaldata, edgePoints, dist, interiorpts):
    pseudopts = []
    for idx,edge in enumerate(edgePoints):
        ptx,pty = getPoint(edge,globaldata)
        circle = shapely.geometry.Point(ptx,pty).buffer(dist[idx])
        for itm in interiorpts:
            itmval = convertPointToShapelyPoint(convertIndexToPoints([itm], globaldata))[0]
            interiorpoint = shapely.geometry.Point(itmval)
            if circle.contains(interiorpoint):
                pseudopts.append(itm)
    print("Found", len(pseudopts), "points which aren't gonna be adapted!")
    with open("pseudopoints.txt", "a") as text_file:
        for item1 in pseudopts:
            text_file.writelines(str(item1))
            text_file.writelines("\t\n")
    return pseudopts

def getDistance(point1,point2,globaldata):
    ptax,ptay = getPoint(point1,globaldata)
    ptbx,ptby = getPoint(point2,globaldata)
    ptx = deltaX(ptax,ptbx)**2
    pty = deltaY(ptay,ptby)**2
    result = math.sqrt(ptx + pty)
    return result

def convertToSuperNicePoints(quadrant,data):
    quadCheck = quadrant[1]
    finallist = []
    for itm in data:
        if quadrantContains(quadCheck,itm):
            finallist.append(itm)
        else:
            None
    return finallist

def inflatedWallPolygon(globaldata, dist, configData):
    log.info("Creating Inflated Wall Point")
    wallpoints = getWallPointArrayIndex(globaldata)
    inflatedWallSet = []
    for itm in wallpoints:
        inflatedWall = []
        for itm2 in itm:
            idx = itm2
            orgWallpt = getPointxy(idx, globaldata)
            nx, ny = normalCalculation(idx, globaldata, True, configData)
            orgWallptx = float(orgWallpt.split(",")[0])
            orgWallpty = float(orgWallpt.split(",")[1])
            normalVector = np.array([nx, ny])
            orgVector = np.array([orgWallptx, orgWallpty])
            newWallpt = orgVector + dist * normalVector
            newWallpt = tuple(newWallpt.tolist())
            inflatedWall.append(newWallpt)
        lastpt = itm[0]
        lastptx,lastpty = getPoint(lastpt,globaldata)
        newpt = (lastptx, lastpty)
        inflatedWall.pop(0)
        inflatedWall.insert(0, newpt)
        inflatedwallpointGeo = shapely.geometry.Polygon(inflatedWall)
        inflatedWallSet.append(inflatedwallpointGeo)
    log.info("Checking for Pseudo Wall Points")
    pseudopts = []
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            if flag == 1:
                itmval = convertPointToShapelyPoint(convertIndexToPoints([idx], globaldata))[0]
                interiorpoint = shapely.geometry.Point(itmval)
                for itm in inflatedWallSet:
                    if itm.contains(interiorpoint):
                        if checkConditionNumber(idx,globaldata,float(configData["normalWall"]["conditionValueThreshold"]), configData):
                            pseudopts.append(idx)
    return pseudopts

def rotateNormals(pseudopts,globaldata, configData):
    log.info("Calculating Nearest Neighbours")
    wallptData = getWallPointArray(globaldata)
    wallptDataOr = wallptData
    wallptData = flattenList(wallptData)
    wallptDataOr = convertToShapely(wallptDataOr)

    pseudoptDict = {}

    for idx2,idx in enumerate(tqdm(pseudopts)):
        ptList = findNearestNeighbourWallPoints(idx,globaldata,wallptData,wallptDataOr)
        ptListIndex = convertPointsToIndex(ptList,globaldata)
        pseudoptDict[idx] = ptListIndex

    log.info("Average Normal Method")

    for idx in pseudopts[:]:
        ptListIndex = pseudoptDict[idx]
        nxavg,nyavg = 0,0
        for itm in ptListIndex:
            nx,ny = normalCalculation(itm,globaldata,True, configData)
            nxavg = nxavg + nx
            nyavg = nyavg + ny
        nxavg = nxavg / 2
        nyavg = nyavg / 2

        condResult = calculateNormalConditionValues(idx,globaldata,nxavg,nyavg,configData)

        dSPosNbhs,dSNegNbhs,dNPosNbhs,dNNegNbhs = condResult["spos"], condResult["sneg"], condResult["npos"], condResult["nneg"]
        dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition = condResult["sposCond"], condResult["snegCond"], condResult["nposCond"], condResult["nnegCond"]

        checkConditionNumber(idx,globaldata,float(configData["normalWall"]["conditionValueThreshold"]), configData)

        print(idx,len(dSPosNbhs),dSPosCondition,len(dSNegNbhs),dSNegCondition,len(dNPosNbhs),dNPosCondition,len(dNNegNbhs),dNNegCondition)

        maxCond = max(dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition)
        if maxCond > float(configData["normalWall"]["conditionValueThreshold"]) or math.isnan(dSPosCondition) or math.isnan(dSNegCondition) or math.isnan(dNPosCondition) or math.isnan(dNNegCondition):
            None
        else:
            globaldata = updateNormals(idx,globaldata,nxavg,nyavg)
            pseudopts.remove(idx)

    log.info("Left Normal Method")

    for idx in pseudopts[:]:
        ptListIndex = pseudoptDict[idx]
        nxavg,nyavg = normalCalculation(ptListIndex[0],globaldata,True, configData)

        condResult = calculateNormalConditionValues(idx,globaldata,nxavg,nyavg, configData)

        dSPosNbhs,dSNegNbhs,dNPosNbhs,dNNegNbhs = condResult["spos"], condResult["sneg"], condResult["npos"], condResult["nneg"]
        dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition = condResult["sposCond"], condResult["snegCond"], condResult["nposCond"], condResult["nnegCond"]

        checkConditionNumber(idx,globaldata,float(configData["normalWall"]["conditionValueThreshold"]), configData)

        print(idx,len(dSPosNbhs),dSPosCondition,len(dSNegNbhs),dSNegCondition,len(dNPosNbhs),dNPosCondition,len(dNNegNbhs),dNNegCondition)

        maxCond = max(dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition)
        if maxCond > float(configData["normalWall"]["conditionValueThreshold"]) or math.isnan(dSPosCondition) or math.isnan(dSNegCondition) or math.isnan(dNPosCondition) or math.isnan(dNNegCondition):
            None
        else:
            globaldata = updateNormals(idx,globaldata,nxavg,nyavg)
            pseudopts.remove(idx)

    log.info("Right Normal Method")

    for idx in pseudopts[:]:
        ptListIndex = pseudoptDict[idx]
        nxavg,nyavg = normalCalculation(ptListIndex[1],globaldata,True, configData)

        condResult = calculateNormalConditionValues(idx,globaldata,nxavg,nyavg, configData)

        dSPosNbhs,dSNegNbhs,dNPosNbhs,dNNegNbhs = condResult["spos"], condResult["sneg"], condResult["npos"], condResult["nneg"]
        dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition = condResult["sposCond"], condResult["snegCond"], condResult["nposCond"], condResult["nnegCond"]

        checkConditionNumber(idx,globaldata,float(configData["normalWall"]["conditionValueThreshold"]), configData)

        print(idx,len(dSPosNbhs),dSPosCondition,len(dSNegNbhs),dSNegCondition,len(dNPosNbhs),dNPosCondition,len(dNNegNbhs),dNNegCondition)

        maxCond = max(dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition)
        if maxCond > float(configData["normalWall"]["conditionValueThreshold"]) or math.isnan(dSPosCondition) or math.isnan(dSNegCondition) or math.isnan(dNPosCondition) or math.isnan(dNNegCondition):
            None
        else:
            globaldata = updateNormals(idx,globaldata,nxavg,nyavg)
            pseudopts.remove(idx)

    print(len(pseudopts))

    return globaldata

def checkConditionNumberBad(globaldata, threshold, configData):
    badList = []
    for index,itm in enumerate(globaldata):
        if index > 0 and getFlag(index, globaldata) == 1:
            xpos = getWeightedInteriorConditionValueofXPos(index, globaldata, configData)
            xneg = getWeightedInteriorConditionValueofXNeg(index, globaldata, configData)
            ypos = getWeightedInteriorConditionValueofYPos(index, globaldata, configData)
            yneg = getWeightedInteriorConditionValueofYNeg(index, globaldata, configData)
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
                badList.append(index)
    return badList

def checkConditionNumberSelectively(globaldata, threshold, badList, configData):
    badList = []
    for index in badList:
        if getFlag(index, globaldata) == 1:
            xpos = getWeightedInteriorConditionValueofXPos(index, globaldata, configData)
            xneg = getWeightedInteriorConditionValueofXNeg(index, globaldata, configData)
            ypos = getWeightedInteriorConditionValueofYPos(index, globaldata, configData)
            yneg = getWeightedInteriorConditionValueofYNeg(index, globaldata, configData)
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
                badList.append(index)
    return badList

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]

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

def getConditionNumber(index, globaldata, conf):
    xpos = getWeightedInteriorConditionValueofXPos(index, globaldata, conf)
    xneg = getWeightedInteriorConditionValueofXNeg(index, globaldata, conf)
    ypos = getWeightedInteriorConditionValueofYPos(index, globaldata, conf)
    yneg = getWeightedInteriorConditionValueofYNeg(index, globaldata, conf)
    result = {"xpos":xpos,"xneg":xneg,"ypos":ypos,"yneg":yneg}
    return result

def getConditionNumberNormal(index,globaldata, conf):
    xpos = getWeightedNormalConditionValueofWallXPos(index,globaldata, conf)
    xneg = getWeightedNormalConditionValueofWallXNeg(index,globaldata, conf)
    result = {"xpos":xpos,"xneg":xneg,"ypos":"NA","yneg":"NA"}
    return result

def fillNeighboursIndex(index,globaldata,nbhs):
    nbhs = list(set(nbhs))
    globaldata[int(index)][20:] = nbhs
    globaldata[int(index)][19] = len(nbhs)
    return globaldata


def checkAeroGlobal2(globaldata,wallpointsData,wallcount):
    coresavail = multiprocessing.cpu_count()
    log.info("Found " + str(coresavail) + " available core(s).")
    log.info("BOOSTU BOOSTU BOOSTU")
    configData = getConfig()
    MAX_CORES = int(configData["generator"]["maxCoresForReplacement"])
    log.info("Max Cores Allowed " + str(MAX_CORES))
    t1 = time.clock()
    pool = ThreadPool(min(MAX_CORES,coresavail))
    results = []
    chunksize = math.ceil(len(globaldata)/min(MAX_CORES,coresavail))
    globalchunks = list(chunks(globaldata,chunksize))
    for itm in globalchunks:
        results.append(pool.apply_async(checkAeroGlobal, args=(itm, globaldata, wallpointsData, wallcount, configData)))
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

def checkAeroGlobal(chunk, globaldata, wallpointsData, wallcount, configData):
    # t1 = time.clock()
    distance = configData["preChecker"]["distanceLimiter"]
    for index, itm in enumerate(chunk):
        if itm is not "start":
            idx = int(itm[0])
            ptx, pty = getPoint(idx, globaldata)
            if min(wallDistance((ptx, pty), wallpointsData)) <= distance:
                # printProgressBar(idx, len(globaldata) - 1, prefix="Progress:", suffix="Complete", length=50)
                nbhs = getNeighbours(idx, globaldata)
                nbhs = list(map(int, nbhs))
                # if True:
                if min(nbhs) < wallcount:
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

def createBoxPolygon(wallpoints, configData):
    BOX_SIDE_SIZE = float(configData["box"]["boxSideLength"])
    headData = findHeadOfWall(wallpoints)
    boxData = []
    for itm in headData:
        x = float(itm.split(",")[0])
        y = float(itm.split(",")[1])
        squareData = getSquarePlot(x,y,BOX_SIDE_SIZE)
        squarePoly = shapely.geometry.Polygon(squareData)
        boxData.append(squarePoly)
    return boxData[:1]


def findBoxAdaptPoints(globaldata,wallpoints, configData):
    boxPoly = createBoxPolygon(wallpoints, configData)
    adaptPoints = []
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            ptx,pty = getPoint(idx,globaldata)
            pt = (ptx,pty)
            pt = shapely.geometry.Point(pt)
            for boxP in boxPoly:
                if boxP.intersects(pt):
                    adaptPoints.append(idx)
    return adaptPoints

def getBoxPlot(XRange,YRange):
    return [(XRange[0],YRange[0]),(XRange[0],YRange[1]),(XRange[1],YRange[1]),(XRange[1],YRange[0])]

def findGeneralBoxAdaptPoints(globaldata, configData):
    XRange = tuple(configData["box"]["XRange"])
    YRange = tuple(configData["box"]["YRange"])
    boxPoly = getBoxPlot(XRange,YRange)
    boxPoly = shapely.geometry.Polygon(boxPoly)
    adaptPoints = []
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            ptx,pty = getPoint(idx,globaldata)
            pt = (ptx,pty)
            pt = shapely.geometry.Point(pt)
            if boxPoly.intersects(pt):
                adaptPoints.append(idx)
    return adaptPoints

def pushCache(globaldata):
    globaldata.pop(0)
    setKeyVal("globaldata",globaldata)
    log.info("Pushed to Cache!")

def verifyIntegrity():
    loadWall = dict(load_obj("wall"))
    with open("adapted.txt","r") as fileman:
        data = fileman.read()
    matchdata = re.findall("(?<=2000 2000)([\S\s]*?)(?=1000 1000)",str(data))
    pointsToCheck = []
    for itm in matchdata:
        itmsplit = itm.split("\n")
        itmsplit.pop(0)
        itmsplit.pop(-1)
        itmsplit = [s.strip() for s in itmsplit]
        pointsToCheck = pointsToCheck + itmsplit
    pointsToCheckOld = pointsToCheck
    itCount = len(pointsToCheck)
    pointsToCheck = list(set(pointsToCheck))
    finCount = len(pointsToCheck)
    if itCount != finCount:
        print("Warning repeated elements detected in adapted file")
        print([k for k,v in Counter(pointsToCheckOld).items() if v>1])
    pointsToCheck = [tuple(float(y) for y in s.split(" ")) for s in pointsToCheck]

    allItems = loadWall.values()
    allItems = list(itertools.chain(*allItems))
    allItems = [tuple(s) for s in allItems]
    # print(allItems)
    try:
        notPresent = set(pointsToCheck) - set(allItems)
        if len(notPresent) > 0:
            print("Not Present in Adapted File")
            print(list(notPresent))
        notPresent = set(allItems) - set(pointsToCheck)
        if len(notPresent) > 0:
            print("Not Present in Wall File")
            print(list(notPresent))
    except TypeError:
        print("Either adapted.txt or wall.json is invalid")
    # (?<=2000 2000)([\S\s]*?)(?=1000 1000)

def cleanAdapted():
    None

def fullRefine(globaldata):
    with open("adapted.txt", "a+") as text_file:
        for idx,_ in enumerate(globaldata):
            if idx > 0:
                ptX,ptY = getPoint(idx,globaldata)
                text_file.writelines(["%s %s " % (ptX,ptY)])
                text_file.writelines("\n")
        text_file.writelines("1000 1000\n")

def fullRefineOuter(globaldata):
    with open("adapted.txt", "a+") as text_file:
        for idx,_ in enumerate(globaldata):
            if idx > 0:
                ptX,ptY = getPointExcludeOuter(idx,globaldata)
                if ptX != False and ptY != False:
                    text_file.writelines(["%s %s " % (ptX,ptY)])
                    text_file.writelines("\n")
        text_file.writelines("1000 1000\n")

def refineCustom(globaldata):
    res = input("Enter the Point Types delimited by space you want to refine: ")
    if len(res) > 0:
        res = list(map(int,res.split(" ")))
        with open("adapted.txt", "a+") as text_file:
            for idx,_ in enumerate(globaldata):
                if idx > 0:
                    flag = getFlag(idx, globaldata)
                    if flag in res:
                        ptX,ptY = getPointExcludeOuter(idx,globaldata)
                        if ptX != False and ptY != False:
                            text_file.writelines(["%s %s " % (ptX,ptY)])
                            text_file.writelines("\n")
            text_file.writelines("1000 1000\n")


def oldMode(globaldata):
    globaldata.pop(0)
    with open("preprocessorfile_oldmode.txt", "w") as text_file:
        for item1 in globaldata:
            item1.pop(14)
            item1.pop(14)
            item1.pop(14)
            item1.pop(14)
            item1.pop(14)
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")

def printBadness(val, globaldata):
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            if flag == 1:
                xpos,xneg,ypos,yneg = getFlags(idx,globaldata)
                if xpos == val or xneg == val or ypos == val or yneg == val:
                    print(idx)

def splitWrite(globaldata):
    outer = []
    inter = []
    wall = []
    for idx in range(len(globaldata)):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            ptx,pty = getPoint(idx,globaldata)
            if flag == 0:
                wall.append((ptx,pty))
            elif flag == 1:
                inter.append((ptx,pty))
            elif flag == 2:
                outer.append((ptx,pty))
    with open("outerpts.txt", "w") as text_file:
        for itm in outer:
            text_file.writelines(["%s %s " % (itm[0],itm[1])])
            text_file.writelines("\n")
    with open("interpts.txt", "w") as text_file:
        for itm in inter:
            text_file.writelines(["%s %s " % (itm[0],itm[1])])
            text_file.writelines("\n")
    with open("wallpts.txt", "w") as text_file:
        for itm in wall:
            text_file.writelines(["%s %s " % (itm[0],itm[1])])
            text_file.writelines("\n")

def configManager():
    while True:
        clearScreen()
        configData = load_obj("config")
        print("*******************************")
        print("Current Configuration")
        print("BSpline Condition Number: %s" % configData["bspline"]["threshold"])
        print("Rechecker Condition Number: %s" % configData["rechecker"]["conditionValueThreshold"])
        print("*******************************")
        print("Type 'exit' to go back")
        print("Type 'thres' to change threshold value (Normal and BSpline Only)")
        print("Type 'thres!' to change threshold value")
        ptidx = input("Awaiting Command: ")
        if ptidx == 'thres':
            thresholdval = int(input("Enter threshold value: "))
            configData["bspline"]["threshold"] = thresholdval
            configData["normalWall"]["conditionValueThreshold"] = thresholdval
            save_obj(configData,"config")
            clearScreen()
            print("Updated Configuration")
            sleep(1)
            clearScreen()
            break
        elif ptidx == 'thres!':
            thresholdval = int(input("Enter threshold value: "))
            configData["bspline"]["threshold"] = thresholdval
            configData["normalWall"]["conditionValueThreshold"] = thresholdval
            configData["rechecker"]["conditionValueThreshold"] = thresholdval
            configData["triangulate"]["leftright"]["wallThreshold"] = thresholdval
            configData["triangulate"]["general"]["wallThreshold"] = thresholdval
            save_obj(configData,"config")
            clearScreen()
            print("Updated Configuration")
            sleep(1)
            clearScreen()
            break
        elif ptidx == 'exit':
            clearScreen()
            print("Going back")
            sleep(1)
            clearScreen()
            break
        else:
            clearScreen()
            print("Invalid input going back")
            sleep(1)
            clearScreen()
            break
    return None

def plotManager(globaldata, wallpoints):
    while True:
        clearScreen()
        print("*******************************")
        print("Plot Manager")
        print("*******************************")
        print("Type 'exit' to go back")
        print("Type 'problem' to generate problematic points plot (1 Level)")
        print("Type 'problem!' to generate problematic points plot (2 Level)")
        print("Type 'sub' to create subplots")
        ptidx = input("Awaiting Command: ")
        if ptidx == 'problem':
            problemPlot(globaldata, wallpoints)
            sleep(1)
            clearScreen()
            break
        elif ptidx == 'problem!':
            problemPlot(globaldata, wallpoints, twoLevel=True)
            sleep(1)
            clearScreen()
            break
        elif ptidx == 'sub':
            subPlot(globaldata, wallpoints)
            sleep(1)
            clearScreen()
            break
        elif ptidx == 'exit':
            clearScreen()
            print("Going back")
            sleep(1)
            clearScreen()
            break
        else:
            clearScreen()
            print("Invalid input going back")
            sleep(1)
            clearScreen()
            break
    return None

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

def generateOutput(globaldata, wallPointArray, wallShapely):
    numPts = len(globaldata) - 1
    with open("preprocessorfile.poly", "w+") as the_file:
        the_file.write("# Generated by QuadTree Mesh Solver\n\n")
        the_file.write("{} 2 0 1\n".format(numPts))
        geoidx = 0
        segments = 0
        for wallidx, itm in enumerate(wallPointArray):
            the_file.write("# Shape {}\n".format(wallidx + 1))
            for itm2 in itm:
                wallx = float(itm2.split(",")[0])
                wally = float(itm2.split(",")[1])
                geoidx += 1
                segments += 1
                the_file.write("{} {} {} {}\n".format(geoidx, wallx, wally, (wallidx + 1)))
        the_file.write("# Interior Points and Outer Points\n")
        captureOuter = None
        for i in range(geoidx + 1, len(globaldata)):
            ptx, pty = getPoint(i, globaldata)
            flag = getFlag(i, globaldata)
            if flag == 2:
                segments += 1
                if captureOuter == None:
                    captureOuter = i
            the_file.write("{} {} {} {}\n".format(i, ptx, pty, flag + 100))
        the_file.write("# Line Segments\n")
        the_file.write("{} 1\n".format(segments))
        the_file.write("# Wall Line Segments\n")
        segidx = 0
        wallPtIndices = getWallPointArrayIndex(globaldata)
        for wallidxI, itm in enumerate(wallPtIndices):
            for idx, wallidx in enumerate(itm):
                if idx == len(itm) - 1:
                    nextPt = itm[0]
                else:
                    nextPt = itm[idx + 1]
                segidx += 1
                the_file.write("{} {} {} {}\n".format(segidx, wallidx, nextPt, (wallidxI + 1)))
        currPt = captureOuter
        the_file.write("# Outer Line Segments\n")
        while True:
            nextPt = getLeftPoint(currPt, globaldata)
            segidx += 1
            the_file.write("{} {} {} {}\n".format(segidx, currPt, nextPt, 102))
            currPt = nextPt
            if int(nextPt) == int(captureOuter):
                break
        the_file.write("{}\n".format(len(wallPointArray)))
        holeidx = 0
        the_file.write("# Holes\n")
        for itm in wallShapely:
            holeidx += 1
            avgpt = random_points_within(itm, 1)[0]
            avgpt = list(avgpt.coords)[0]
            the_file.write("{} {} {}\n".format(holeidx, avgpt[0], avgpt[1]))


def random_points_within(poly, num_points):
    min_x, min_y, max_x, max_y = poly.bounds

    points = []

    while len(points) < num_points:
        random_point = shapely.geometry.Point([np.random.uniform(min_x, max_x), np.random.uniform(min_y, max_y)])
        if (random_point.within(poly)):
            points.append(random_point)

    return points

def subPlot(globaldata, wallpoints, noClean=False):
    if noClean == False:
        if os.path.isdir("plots"):
            shutil.rmtree("plots")
            os.mkdir("plots")
        else:
            os.mkdir("plots")
    with open("plots/wall_combined", "w+") as the_file_main:
        superidx = 0
        for idx, itm in enumerate(wallpoints):
            with open("plots/wall_{}".format(idx), "w+") as the_file:
                for idx2, itm2 in enumerate(itm):
                    superidx += 1
                    pt = itm2.split(",")
                    ptx = float(pt[0])
                    pty = float(pt[1])
                    the_file.write("{} {} {}\n".format(idx2 + 1, ptx, pty))
                    the_file_main.write("{} {} {}\n".format(superidx, ptx, pty))
    print("Generated Subplots")

def problemPlot(globaldata, wallpoints, twoLevel=False):
    conf = getConfig()
    problemPts = []
    finalPts = []
    if os.path.isdir("plots"):
        shutil.rmtree("plots")
        os.mkdir("plots")
    else:
        os.mkdir("plots")
    for idx, _ in enumerate(tqdm(globaldata)):
        if idx > 0:
            flag = getFlag(idx, globaldata)
            if flag == 1:
                if isConditionBad(idx, globaldata, conf):
                    problemPts.append(idx)
    for idx in problemPts:
        finalPts += getNeighbours(idx, globaldata)
        finalPts += [idx]
    if twoLevel:
        finalPts2 = []
        for idx in finalPts:
            finalPts2 += getNeighbours(idx, globaldata)
            finalPts2 += [idx]
    finalPts = list(set(finalPts2))
    with open("plots/problem_plot", "w+") as the_file_main:
        for idx in finalPts:
            flag = getFlag(idx, globaldata)
            if flag != 0:
                ptx, pty = getPoint(idx, globaldata)
                the_file_main.write("{} {} {}\n".format(idx, ptx, pty))
    subPlot(globaldata, wallpoints, noClean=True)
    print("Generated Problem Plot")

def getNearestProblemPoint(idx,globaldata, conf):
    xpos = getDWallXPosPoints(idx,globaldata, conf)
    xneg = getDWallXNegPoints(idx,globaldata, conf)
    leftright = getLeftandRightPoint(idx,globaldata)
    mainptx,mainpty = getPoint(idx,globaldata)
    mainpt = (mainptx,mainpty)
    currang = 0
    currpt = 0
    if len(xpos) == 1:
        leftright.remove(xpos[0])
        wallx = float(leftright[0].split(",")[0])
        wally = float(leftright[0].split(",")[1])
        wallpt = (wallx,wally)
        for itm in xneg:
            itmx = float(itm.split(",")[0])
            itmy = float(itm.split(",")[1])
            itmpt = (itmx,itmy)
            try:
                angitm = angle(wallx,wally,mainptx,mainpty,itmx,itmy)
            except:
                print(wallx,wally,mainptx,mainpty,itmx,itmy)
            if currang < angitm:
                curang = angitm
                currpt = itm
    if len(xneg) == 1:
        leftright.remove(xneg[0])
        wallx = float(leftright[0].split(",")[0])
        wally = float(leftright[0].split(",")[1])
        wallpt = (wallx,wally)
        for itm in xpos:
            itmx = float(itm.split(",")[0])
            itmy = float(itm.split(",")[1])
            itmpt = (itmx,itmy)
            try:
                angitm = angle(wallx,wally,mainptx,mainpty,itmx,itmy)
            except:
                print(wallx,wally,mainptx,mainpty,itmx,itmy)
            if currang < angitm:
                curang = angitm
                currpt = itm
    return currpt

def interiorConnectivityCheck(globaldata):
    conf = getConfig()
    badPtsNan = []
    badPtsInf = []
    badPtsAll = []
    for idx,_ in enumerate(tqdm(globaldata)):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            if flag == 1:
                # checkConditionNumber(idx,globaldata,int(getConfig()["bspline"]["threshold"]))
                if isConditionNan(idx,globaldata, conf):
                    badPtsNan.append(idx)
                if isConditionInf(idx, globaldata, conf):
                    badPtsInf.append(idx)
                if isConditionBad(idx, globaldata, conf):
                    badPtsAll.append(idx)
    badPtsAll = list(set(badPtsAll) - set(badPtsInf) - set(badPtsNan))
    badPtsNan = list(map(str, badPtsNan))
    badPtsInf = list(map(str, badPtsInf))
    badPtsAll = list(map(str, badPtsAll))
    print("Bad Points (NaN) Detected: {}".format(" ".join(badPtsNan)))
    print("Bad Points (Inf) Detected: {}".format(" ".join(badPtsInf)))
    print("Bad Points (Conn) Detected: {}".format(" ".join(badPtsAll)))

def sparseNullifier(globaldata):
    madechanges = False
    sensorBox = []
    conf = getConfig()
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            if flag == 0:
                xpos,xneg,_,_ = getFlags(idx,globaldata)
                if xpos == 1:
                    getXposPoints = getDWallXPosPoints(idx,globaldata, conf)
                    for itm in getXposPoints:
                        index = getIndexFromPoint(itm,globaldata)
                        flag = getFlag(index,globaldata)
                        if flag == 0:
                            madechanges = True
                            sensorBox.append(index)
                if xneg == 1:
                    getXnegPoints = getDWallXNegPoints(idx,globaldata, conf)
                    for itm in getXnegPoints:
                        index = getIndexFromPoint(itm,globaldata)
                        flag = getFlag(index,globaldata)
                        if flag == 0:
                            madechanges = True
                            sensorBox.append(index)
    if madechanges == True:
        with open("sensor_flag.dat", "w") as text_file:
            for idx,itm in enumerate(globaldata):
                if idx > 0:
                    if idx in sensorBox:
                        text_file.writelines("  " + str(idx) + "  1\n")
                    else:
                        text_file.writelines("  " + str(idx) + "  0\n")

def wallConnectivityCheckNearest(globaldata):
    madechanges = False
    conf = getConfig()
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            if flag == 0:
                xpos,xneg,_,_ = getFlags(idx,globaldata)
                if xpos == 1 or xneg == 1:
                    print(idx)
                    madechanges = True
                    ptcord = getNearestProblemPoint(idx,globaldata, conf)
                    if ptcord != 0:
                        ptcordx = float(ptcord.split(",")[0])
                        ptcordy = float(ptcord.split(",")[1])
                    with open("adapted.txt", "a+") as text_file:
                        text_file.writelines(["%s %s " % (ptcordx, ptcordy)])
                        text_file.writelines("\n")
    if madechanges == True:
        with open("adapted.txt", "a+") as text_file:
            text_file.writelines("1000 1000\n")

def wallConnectivityCheckSensor(globaldata):
    madechanges = False
    sensorBox = []
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            if flag == 0:
                xpos,xneg,_,_ = getFlags(idx,globaldata)
                if xpos == 1 or xneg == 1:
                    print(idx)
                    madechanges = True
                    sensorBox.append(idx)
    if madechanges == True:
        with open("sensor_flag.dat", "w") as text_file:
            for idx,_ in enumerate(globaldata):
                if idx > 0:
                    if idx in sensorBox:
                        text_file.writelines("  " + str(idx) + "  1\n")
                    else:
                        text_file.writelines("  " + str(idx) + "  0\n")

def wallConnectivityCheck(globaldata, verbose=False):
    madechanges = False
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            if flag == 0:
                xpos,xneg,_,_ = getFlags(idx,globaldata)
                if xpos == 1 or xneg == 1:
                    print(idx)
                    if not verbose:
                        madechanges = True
                        ptcordx, ptcordy = getPoint(idx,globaldata)
                        with open("adapted.txt", "a+") as text_file:
                            text_file.writelines(["%s %s " % (ptcordx, ptcordy)])
                            text_file.writelines("\n")
    if madechanges == True:
        with open("adapted.txt", "a+") as text_file:
            text_file.writelines("1000 1000\n")

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

def adaptGetWallPointArray(globaldata):
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

# cv: Input array of the body
# point_division: Number of new points required between given point indexes
# index1: First point index
# index2: Second point index

def typeObtuseRightAcute(x1, y1, x2, y2, x3, y3):
    #no idea if this is a good value but works for example
    #and should be low enough to give right answers for all but crazy close triangles

    # Using Pythagoras theorem
    sideAB = distance(x1, y1, x2, y2)
    sideBC = distance(x2, y2, x3, y3)
    sideAC = distance(x3, y3, x1, y1)

    [var1, var2, largest] = sorted([sideAB, sideBC, sideAC])

    if largest == sideAC and (largest) ** 2 > ((var1 ** 2 + (var2) ** 2)):
        return 1
    else:
        return 0

def bsplineCall(cv, point_division, index1, index2):
    cv = np.concatenate((cv, [cv[0]]), axis = 0)
    # plt.plot(cv[:,0],cv[:,1], 'o-', label='Control Points')

    if(index1 > len(cv) or index2 > len(cv)):
        exit("ERROR: Index not in range")

    # tck : A tuple (t,c,k) containing the vector of knots, the B-spline coefficients, and the degree of the spline
    # u : The weighted sum of squared residuals of the spline approximation.
    tck, u = splprep([cv[:,0], cv[:,1]], s=0)

    generated_points = []
    update = 2000
    while len(generated_points) < point_division and update < 100000:
        # print(update)
        generated_points.clear()
        u_new = np.linspace(u.min(), u.max(), (update + point_division)*(len(cv)))
        if update < 300:
            update = update + 1
        elif update < 2000:
            update = update + 100
        else:
            update = update + 1000
        new_points = splev(u_new, tck, der = 0)

        for i in range(len(new_points[0])):
            # The cv[x] represents point index (subtracted by one) in between which the new generated points are found
            if (typeObtuseRightAcute(cv[index1][0], cv[index1][1], new_points[0][i],new_points[1][i], cv[index2][0], cv[index2][1])== 1):
                if(angle(cv[index1][0], cv[index1][1], new_points[0][i],new_points[1][i], cv[index2][0], cv[index2][1]) > 170 and
                    angle(cv[index1][0], cv[index1][1], new_points[0][i],new_points[1][i], cv[index2][0], cv[index2][1]) < 190):
                    generated_points.append([new_points[0][i], new_points[1][i]])
                    # print(new_points[0][i], new_points[1][i])
    else:
        None
        # print(update)

    # plt.plot(new_points[0], new_points[1], 'o-', label = 'direction point')

    # plt.minorticks_on()
    # plt.legend()
    # plt.xlabel('x')
    # plt.ylabel('y')
    # # plt.xlim(-0.1, 1.1)
    # # plt.ylim(-0.1, 0.1)
    # # plt.gca().set_aspect('equal', adjustable='box')
    # plt.show()
    return generated_points

def generateBSplinePoints(cv,update):
    cv = np.concatenate((cv, [cv[0]]), axis = 0)
    tck, u = splprep([cv[:,0], cv[:,1]], s=0)
    u_new = np.linspace(u.min(), u.max(), update*len(cv))
    new_points = splev(u_new, tck, der = 0)
    return new_points

def generateBSplineBetween(cv,index1,index2, num_points = 20):
    cv = np.concatenate((cv, [cv[0]]), axis = 0)
    if index2 == 0:
        None
        index2 = len(cv) - 1
    if(index1 > len(cv) or index2 > len(cv)):
        exit("ERROR: Index not in range")
    tck, u = splprep([cv[:,0], cv[:,1]], s=0)
    u_new = np.linspace(u[index1], u[index2], num_points)
    new_points = splev(u_new, tck, der = 0)
    new_points = convertPointsToNicePoints(new_points)
    new_points.pop(0)
    new_points.pop(-1)
    return new_points

def getPointsOnlyInQuadrant(ptslist, idx, globaldata):
    goodpoints = []
    quad1 = getBoundingBoxOfQuadrant(idx,globaldata)
    for itm in ptslist:
        if quadrantContains(quad1,itm):
            goodpoints.append(itm)
    return goodpoints

def convertPointsToKdTree(points):
    return spatial.cKDTree(list(zip(points[0].ravel(), points[1].ravel())))

def convertPointsToNicePoints(bsplineData):
    return list(zip(bsplineData[0].ravel(), bsplineData[1].ravel()))

def getPointsBetween(kdTree,startx,stopx):
    startx = tuple(map(float,startx.split(",")))
    stopx = tuple(map(float,stopx.split(",")))
    startrg = kdTree.query(np.array(startx))[1]
    stoprg = kdTree.query(np.array(stopx))[1]
    result = kdTree.data[startrg:stoprg]
    return verifyPointsBetween(result.tolist(),startx,stopx)

def verifyPointsBetween(search_list,startpt,stoppt):
    generated_points = []
    for i in range(len(search_list)):
        if (typeObtuseRightAcute(startpt[0], startpt[1], search_list[i][0],search_list[i][1], stoppt[0], stoppt[1])== 1):
            if(angle(startpt[0], startpt[1], search_list[i][0],search_list[i][1], stoppt[0], stoppt[1]) > 170 and
                angle(startpt[0], startpt[1], search_list[i][0],search_list[i][1], stoppt[0], stoppt[1]) < 190):
                generated_points.append([search_list[i][0], search_list[i][1]])
    return generated_points

def getPointsBetween2(bsplineData,startx,stopx):
    startx = tuple(map(float,startx.split(",")))
    stopx = tuple(map(float,stopx.split(",")))
    startrg = spatial.distance.cdist(np.array(bsplineData),np.array([startx]),"euclidean").argmin()
    stoprg = spatial.distance.cdist(np.array(bsplineData),np.array([stopx]),"euclidean").argmin()
    if startrg > stoprg:
        startrg,stoprg = stoprg,startrg
    result = bsplineData[startrg:stoprg]
    return verifyPointsBetween(result,startx,stopx)

def getConfig():
    with open("config.json","r") as f:
        config = json.load(f)
    return config

conn = redis.Redis(getConfig()["global"]["redis"]["host"],getConfig()["global"]["redis"]["port"],getConfig()["global"]["redis"]["db"],getConfig()["global"]["redis"]["password"])

def setKeyVal(keyitm,keyval):
    PREFIX = getConfig()["global"]["redis"]["prefix"]
    if PREFIX == "NONE":
        setPrefix()
    PREFIX = getConfig()["global"]["redis"]["prefix"]
    conn.set(PREFIX + "_" + str(keyitm),json.dumps({keyitm: keyval}))
    return True

def getKeyVal(keyitm):
    PREFIX = getConfig()["global"]["redis"]["prefix"]
    if PREFIX == "NONE":
        setPrefix()
    PREFIX = getConfig()["global"]["redis"]["prefix"]
    try:
        result = dict(json.loads(conn.get(PREFIX + "_" + str(keyitm))))
        return result.get(keyitm)
    except TypeError:
        return None

def setPrefix():
    PREFIX = getConfig()["global"]["redis"]["prefix"]
    if PREFIX == "NONE":
        conn = redis.Redis(getConfig()["global"]["redis"]["host"],getConfig()["global"]["redis"]["port"],getConfig()["global"]["redis"]["db"],getConfig()["global"]["redis"]["password"])
        PREFIX = str(uuid.uuid4()).replace("-","")
        data = dict(load_obj("config"))
        data["global"]["redis"]["prefix"] = PREFIX
        save_obj(data,"config")

def save_obj(obj, name, indent=None):
    with open(name + '.json', 'w') as f:
        json.dump(obj, f, indent=indent)

def load_obj(name):
    with open(name + '.json', 'r') as f:
        return json.load(f)

def orientation(file, verbose=True):
    reader = csv.reader(file, delimiter = "\t")

    plist = []
    for x,y in reader:
        plist.append((float(x), float(y)))

    def f(x1, y1, x2, y2, x3, y3):
        crossProduct = (x2 - x1) * (y3 - y2) - (x3 - x2) * (y2 - y1)
        if crossProduct > 0:
            return "ccw"
        else:
            return "cw"

    cwTurns = 0
    ccwTurns = 0
    plist.append(plist[0])
    plist.append(plist[1])

    for j in range(len(plist) - 2):
        (x1, y1) = plist[j]
        (x2, y2) = plist[j+1]
        (x3, y3) = plist[j+2]
        if (f(x1, y1, x2, y2, x3, y3) == "cw"):
            cwTurns += 1
        else:
            ccwTurns += 1

    if verbose:
        if cwTurns == 0 or ccwTurns == 0:
            print("\tGeometry: Convex")
        else:
            print("\tGeometry: Not Convex")

        if cwTurns > ccwTurns:
            print("\tOrientation: Clockwise")
            return "cw"
        else:
            print("\tOrientation: Anti Clockwise")
            return "ccw"
    else:
        if cwTurns > ccwTurns:
            return "cw"
        else:
            return "ccw"

def hills_manager():
    adapted_lines = []
    adapted_file = open("adapted.txt", "r+")
    adapted_lines = adapted_file.readlines()

    enable = 0
    disable = 0
    able = True

    for line in adapted_lines:
        if line == "4000 4000\n":
            disable += 1
        elif line == "5000 5000\n":
            enable += 1

    clearScreen()
    print("*****************\n")
    print("Welcome to Hills and Valleys Manager")
    if enable < disable:
        able = False
        print("Current: DISABLED.")
    else:
        print("Current: ENABLED.")

    print("\n*****************\n")

    choice = input("Do you want to toggle? (Y/n): ").lower()

    if choice == "y" and able == True:
        adapted_lines.append("4000 4000\n")
        print("\nHills and Valleys is now DISABLED.")
    if choice == "y" and able == False:
        adapted_lines.append("5000 5000\n")
        print("\nHills and Valleys is now ENABLED.")

    print("\n*****************\n")
    time.sleep(2)
    clearScreen()
    adapted_file.seek(0)
    for line in adapted_lines:
        adapted_file.write(line)
    adapted_file.close()