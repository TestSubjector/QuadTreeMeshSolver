import numpy as np
import math
import shapely.geometry
from shapely import wkt
from shapely.geometry import Polygon, Point
from shapely.ops import linemerge, unary_union, polygonize, nearest_points
import shapely
import config
from scipy import spatial
import scipy.interpolate as si
from scipy.interpolate import splprep, splev
import matplotlib.pyplot as plt
import logging
import itertools
import pickle
import json
import time
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
from tqdm import tqdm
import os
import errno

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


def getNeighbours(index, globaldata):
    index = int(index)
    ptdata = globaldata[index]
    ptdata = ptdata[20:]
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

def checkConditionNumberLogger(index, globaldata, threshold):
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
        f = open("History.txt","a+")
        f.write(str(index) + " " + str(len(dSPointXPos)) + " " + str(xpos) + " " + str(len(dSPointXNeg)) + " " + str(xneg) + " " + str(len(dSPointYPos)) + " " + str(ypos) + " " + str(len(dSPointYNeg)) + " " + str(yneg))
        f.close
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

def flattenList(ptdata):
    return list(itertools.chain.from_iterable(ptdata))


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
                                        with open("shit", "a+") as the_file:
                                            the_file.write("{} {} {}\n".format(px, py, idx))
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
    ptsToCheck = convertIndexToPoints(getLeftandRightPoint(leastidx,globaldata),globaldata)

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
    ptsToCheck = convertIndexToPoints(getLeftandRightPoint(leastidx,globaldata),globaldata)
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

def save_obj(obj, name ):
    with open(name + '.json', 'w') as f:
        json.dump(obj, f)

def load_obj(name ):
    with open(name + '.json', 'r') as f:
        return json.load(f)


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

def getNormals(idx,globaldata):
    nx = globaldata[idx][11]
    ny = globaldata[idx][12]
    return nx,ny

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
        # print(idx)
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

def angle(x1, y1, x2, y2, x3, y3):
    a = np.array([x1, y1])
    b = np.array([x2, y2])
    c = np.array([x3, y3])

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

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

def convertPointToShapelyPoint(pointarry):
    pointnewarry = []
    for itm in pointarry:
        xcord = float(itm.split(",")[0])
        ycord = float(itm.split(",")[1])
        pointnewarry.append((xcord, ycord))
    return pointnewarry

def nonAdaptWallPolygon(globaldata, wallpoints, dist, interiorpts):
    print("Creating Inflated Wall Point")
    pseudopts = []
    inflatedWall = []
    for itm in wallpoints:
        idx = getIndexFromPoint(itm,globaldata)
        orgWallpt = getPointxy(idx, globaldata)
        nx, ny = normalCalculation(idx, globaldata, True)
        orgWallptx = float(orgWallpt.split(",")[0])
        orgWallpty = float(orgWallpt.split(",")[1])
        normalVector = np.array([nx, ny])
        orgVector = np.array([orgWallptx, orgWallpty])
        newWallpt = orgVector + dist * normalVector
        newWallpt = tuple(newWallpt.tolist())
        inflatedWall.append(newWallpt)
    wallptsData = convertPointToShapelyPoint(wallpoints)
    wallpointGeo = Polygon(wallptsData)
    lastpt = wallptsData[0]
    newpt = (lastpt[0] + dist, lastpt[1])
    inflatedWall.pop(0)
    inflatedWall.insert(0, newpt)
    inflatedwallpointGeo = Polygon(inflatedWall)
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
        interiorpoint = Point(itmval)
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
        circle = Point(ptx,pty).buffer(dist[idx])
        for itm in interiorpts:
            itmval = convertPointToShapelyPoint(convertIndexToPoints([itm], globaldata))[0]
            interiorpoint = Point(itmval)
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
            nx, ny = normalCalculation(idx, globaldata, True)
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
        inflatedwallpointGeo = Polygon(inflatedWall)
        inflatedWallSet.append(inflatedwallpointGeo)
    log.info("Checking for Pseudo Wall Points")
    pseudopts = []
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            if flag == 1:
                itmval = convertPointToShapelyPoint(convertIndexToPoints([idx], globaldata))[0]
                interiorpoint = Point(itmval)
                for itm in inflatedWallSet:
                    if itm.contains(interiorpoint):
                        if checkConditionNumber(idx,globaldata,float(configData["normalWall"]["conditionValueThreshold"]), configData):
                            pseudopts.append(idx)
    return pseudopts

def setNormals(pseudopts,globaldata):
    log.info("Calculating Nearest Neighbours")
    wallptData = getWallPointArray(globaldata)
    wallptDataOr = wallptData
    wallptData = flattenList(wallptData)

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
            nx,ny = normalCalculation(itm,globaldata,True)
            nxavg = nxavg + nx
            nyavg = nyavg + ny
        nxavg = nxavg / 2
        nyavg = nyavg / 2

        condResult = calculateNormalConditionValues(idx,globaldata,nxavg,nyavg)

        dSPosNbhs,dSNegNbhs,dNPosNbhs,dNNegNbhs = condResult["spos"], condResult["sneg"], condResult["npos"], condResult["nneg"]
        dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition = condResult["sposCond"], condResult["snegCond"], condResult["nposCond"], condResult["nnegCond"]

        checkConditionNumber(idx,globaldata,float(config.getConfig()["normalWall"]["conditionValueThreshold"]))

        print(idx,len(dSPosNbhs),dSPosCondition,len(dSNegNbhs),dSNegCondition,len(dNPosNbhs),dNPosCondition,len(dNNegNbhs),dNNegCondition)
        
        maxCond = max(dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition)
        if maxCond > float(config.getConfig()["normalWall"]["conditionValueThreshold"]) or math.isnan(dSPosCondition) or math.isnan(dSNegCondition) or math.isnan(dNPosCondition) or math.isnan(dNNegCondition):
            None
        else:
            globaldata = updateNormals(idx,globaldata,nxavg,nyavg)
            pseudopts.remove(idx)

    log.info("Left Normal Method")

    for idx in pseudopts[:]:
        ptListIndex = pseudoptDict[idx]
        nxavg,nyavg = normalCalculation(ptListIndex[0],globaldata,True)

        condResult = calculateNormalConditionValues(idx,globaldata,nxavg,nyavg)

        dSPosNbhs,dSNegNbhs,dNPosNbhs,dNNegNbhs = condResult["spos"], condResult["sneg"], condResult["npos"], condResult["nneg"]
        dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition = condResult["sposCond"], condResult["snegCond"], condResult["nposCond"], condResult["nnegCond"]

        checkConditionNumber(idx,globaldata,float(config.getConfig()["normalWall"]["conditionValueThreshold"]))

        print(idx,len(dSPosNbhs),dSPosCondition,len(dSNegNbhs),dSNegCondition,len(dNPosNbhs),dNPosCondition,len(dNNegNbhs),dNNegCondition)
        
        maxCond = max(dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition)
        if maxCond > float(config.getConfig()["normalWall"]["conditionValueThreshold"]) or math.isnan(dSPosCondition) or math.isnan(dSNegCondition) or math.isnan(dNPosCondition) or math.isnan(dNNegCondition):
            None
        else:
            globaldata = updateNormals(idx,globaldata,nxavg,nyavg)
            pseudopts.remove(idx)

    log.info("Right Normal Method")

    for idx in pseudopts[:]:
        ptListIndex = pseudoptDict[idx]
        nxavg,nyavg = normalCalculation(ptListIndex[1],globaldata,True)

        condResult = calculateNormalConditionValues(idx,globaldata,nxavg,nyavg)

        dSPosNbhs,dSNegNbhs,dNPosNbhs,dNNegNbhs = condResult["spos"], condResult["sneg"], condResult["npos"], condResult["nneg"]
        dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition = condResult["sposCond"], condResult["snegCond"], condResult["nposCond"], condResult["nnegCond"]

        checkConditionNumber(idx,globaldata,float(config.getConfig()["normalWall"]["conditionValueThreshold"]))

        print(idx,len(dSPosNbhs),dSPosCondition,len(dSNegNbhs),dSNegCondition,len(dNPosNbhs),dNPosCondition,len(dNNegNbhs),dNNegCondition)
        
        maxCond = max(dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition)
        if maxCond > float(config.getConfig()["normalWall"]["conditionValueThreshold"]) or math.isnan(dSPosCondition) or math.isnan(dSNegCondition) or math.isnan(dNPosCondition) or math.isnan(dNNegCondition):
            None
        else:
            globaldata = updateNormals(idx,globaldata,nxavg,nyavg)
            pseudopts.remove(idx)

    print(len(pseudopts))

    return globaldata