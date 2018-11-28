from __future__ import print_function

import cython
cimport cython

import numpy as np
cimport numpy as np
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
import itertools
import re
import connectivity
import json
import point
from collections import Counter
from time import sleep
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

from cython.parallel import prange, parallel
cdef extern from "math.h":
    double sqrt(double m)

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

def convertOldDataToNewData(globaldata):
    newglobaldata = []
    for i in range(len(globaldata))
        data = globaldata[i][:20]
        nbhs = getNeighbours(i, globaldata)
        datalist = [data, nbhs]
        quadpt = QuadPointList(datalist)
        newglobaldata.append(quadpt)
    return newglobaldata

def QuadPointList(*args):
    return point.QuadPoint(args)


def printProgressBar(iteration, total, prefix="", suffix="", decimals=1, length=100, fill="█"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print("\r%s |%s| %s%% %s" % (prefix, bar, percent, suffix), end="\r")
    if iteration == total:
        print()


cdef list appendNeighbours(int index, list globaldata, list newpts):
    cdef int pt = getIndexFromPoint(newpts, globaldata)
    cdef list nbhs = getNeighbours(index, globaldata)
    nbhs = nbhs + [pt]
    nbhs = list(set(nbhs))
    globaldata[int(index)][20:] = nbhs
    globaldata[int(index)][19] = len(nbhs)
    return globaldata


cdef int getFlag(int indexval, list lista):
    return int(lista[indexval][5])


cdef list getNeighbours(int index, list globaldata):
    cdef list ptdata = globaldata[index]
    ptdata = ptdata[20:]
    return ptdata


cdef int getIndexFromPoint(int pt, list globaldata):
    cdef double ptx = pt.split(",")[0]
    cdef double pty = pt.split(",")[1]
    for itm in globaldata:
        if str(itm[1]) == str(ptx) and str(itm[2]) == str(pty):
            return int(itm[0])

cdef list convertPointsToIndex(list pointarray, list globaldata):
    cdef list ptlist = []
    for itm in pointarray:
        idx = getIndexFromPoint(itm,globaldata)
        ptlist.append(idx)
    return ptlist


def getPoint(index, globaldata):
    index = int(index)
    ptdata = globaldata[index]
    ptx = ptdata[1]
    pty = ptdata[2]
    return ptx, pty


def getPointxy(index, globaldata):
    ptx, pty = getPoint(index, globaldata)
    return str(ptx) + "," + str(pty)


cdef list convertIndexToPoints(list indexarray, list globaldata):
    cdef list listptlist = []
    for item in indexarray:
        item = int(item)
        ptx, pty = getPoint(item, globaldata)
        listptlist.append((str(ptx) + "," + str(pty)))
    return listptlist

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef double weightedConditionValueForSetOfPoints(int index, list globaldata, list nbhs):
    cdef double mainptx = <double>globaldata[index][1]
    cdef double mainpty = <double>globaldata[index][2]
    cdef double deltaSumXX, deltaSumYY, deltaSumXY, nbhitemX, nbhitemY, deltaX, deltaY, d = 0
    deltaSumXX = 0
    deltaSumYY = 0
    deltaSumXY = 0
    nbhitemX = 0
    nbhitemY = 0
    deltaX = 0
    deltaY = 0
    cdef list data = []
    cdef str nbhitem
    for nbhitem in nbhs:
        nbhitemX = <double>nbhitem.split(",")[0]
        nbhitemY = <double>nbhitem.split(",")[1]
        deltaX = nbhitemX - mainptx
        deltaY = nbhitemY - mainpty
        d = (deltaX ** 2) + (deltaY ** 2)
        d = sqrt(d)
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
    cdef np.ndarray[DTYPE_t, ndim=2] random
    random = np.array(data)
    shape = (2, 2)
    random = random.reshape(shape)
    s = np.linalg.svd(random, full_matrices=False, compute_uv=False)
    s = max(s) / min(s)
    return s


cdef double deltaX(double xcord, double orgxcord):
    return orgxcord - xcord


cdef double deltaY(double ycord, double orgycord):
    return orgycord - ycord

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

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]

def deltaNeighbourCalculation(list currentneighbours, str currentcord, bint isxcord, bint isnegative):
    cdef double xpos, xneg, ypos, yneg = 0
    xpos = 0
    xneg = 0
    ypos = 0
    yneg = 0
    cdef list temp = []
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


cdef list getDXPosPoints(int index, list globaldata):
    cdef list nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, False
    )
    return mypoints


cdef list getDXNegPoints(int index, list globaldata):
    cdef list nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, True
    )
    return mypoints


cdef list getDYPosPoints(int index, list globaldata):
    cdef nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, False
    )
    return mypoints


cdef list getDYNegPoints(int index, list globaldata):
    cdef nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, True
    )
    return mypoints


cdef list getDXPosPointsFromSet(int index, list globaldata, list points):
    cdef list nbhs = convertIndexToPoints(points, globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, False
    )
    return mypoints


cdef list getDXNegPointsFromSet(int index, list globaldata, list points):
    cdef list nbhs = convertIndexToPoints(points, globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, True
    )
    return mypoints


cpdef list getDYPosPointsFromSet(int index, list globaldata, list points):
    cdef list nbhs = convertIndexToPoints(points, globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, False
    )
    return mypoints


cdef list getDYNegPointsFromSet(int index, list globaldata, int points):
    cdef list nbhs = convertIndexToPoints(points, globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, True
    )
    return mypoints


cdef bint checkConditionNumber(int index, list globaldata, int threshold):
    cdef int xpos = getWeightedInteriorConditionValueofXPos(index, globaldata)
    cdef int xneg = getWeightedInteriorConditionValueofXNeg(index, globaldata)
    cdef int ypos = getWeightedInteriorConditionValueofYPos(index, globaldata)
    cdef int yneg = getWeightedInteriorConditionValueofYNeg(index, globaldata)
    cdef list dSPointXPos = getDXPosPoints(index, globaldata)
    cdef list dSPointXNeg = getDXNegPoints(index, globaldata)
    cdef list dSPointYPos = getDYPosPoints(index, globaldata)
    cdef list dSPointYNeg = getDYNegPoints(index, globaldata)
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

cdef void checkConditionNumberWall(int index, list globaldata, int threshold):
    cdef double xpos = getWeightedInteriorConditionValueofXPos(index, globaldata)
    cdef double xneg = getWeightedInteriorConditionValueofXNeg(index, globaldata)
    cdef double ypos = getWeightedInteriorConditionValueofYPos(index, globaldata)
    cdef double yneg = getWeightedInteriorConditionValueofYNeg(index, globaldata)
    cdef list dSPointXPos = getDXPosPoints(index, globaldata)
    cdef list dSPointXNeg = getDXNegPoints(index, globaldata)
    cdef list dSPointYPos = getDYPosPoints(index, globaldata)
    cdef list dSPointYNeg = getDYNegPoints(index, globaldata)
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


cpdef list cleanNeighbours(list globaldata):
    log.info("Beginning Duplicate Neighbour Detection")
    cdef i = 0
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

def deltaWallNeighbourCalculation(int index, list currentneighbours, double nx, double ny, bint giveposdelta, list globaldata):
    cdef int deltaspos, deltasneg, deltaszero
    deltaspos = 0
    deltasneg = 0
    deltaszero = 0
    tx = ny
    ty = -nx
    cdef double xcord = float(globaldata[index][1])
    cdef double ycord = float(globaldata[index][2])
    cdef list output = []
    cdef double deltas, deltan
    deltas = 0
    deltan = 0
    cdef double itemx = 0
    cdef double itemy = 0
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

def deltaWallNeighbourCalculationN(int index, list currentneighbours, double nx, double ny, bint giveposdelta, list globaldata):
    cdef int deltaspos, deltasneg, deltaszero
    deltaspos = 0
    deltasneg = 0
    deltaszero = 0
    tx = ny
    ty = -nx
    cdef double xcord = float(globaldata[index][1])
    cdef double ycord = float(globaldata[index][2])
    cdef list output = []
    cdef double deltas, deltan
    deltas = 0
    deltan = 0
    cdef double itemx = 0
    cdef double itemy = 0
    for item in currentneighbours:
        itemx = float(item.split(",")[0])
        itemy = float(item.split(",")[1])
        deltas = (nx * (itemx - xcord)) + (ny * (itemy - ycord))
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

cdef double weightedConditionValueForSetOfPointsNormalWithInputs(int index, list globaldata, list nbh, double nx, double ny):
    cdef double mainptx = float(globaldata[index][1])
    cdef double mainpty = float(globaldata[index][2])
    cdef double tx = ny
    cdef double ty = -nx
    cdef double deltaSumS = 0
    cdef double deltaSumN = 0
    cdef double deltaSumSN = 0
    cdef list data = []
    cdef str nbhitm
    cdef float nbhitemX, nbhitemY, deltaS, deltaN
    nbhitemX = 0
    nbhitemY = 0
    deltaS = 0
    deltaN = 0
    cdef str nbhitem
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

cdef list setFlags(int index, list globaldata, int threshold):
    cdef double dxpos = getWeightedInteriorConditionValueofXPos(index, globaldata)
    cdef double dxneg = getWeightedInteriorConditionValueofXNeg(index, globaldata)
    cdef double dypos = getWeightedInteriorConditionValueofYPos(index, globaldata)
    cdef double dyneg = getWeightedInteriorConditionValueofYNeg(index, globaldata)
    if dxpos > threshold:
        globaldata[index][7] = 1
    if dxneg > threshold:
        globaldata[index][8] = 1
    if dypos > threshold:
        globaldata[index][9] = 1
    if dyneg > threshold:
        globaldata[index][10] = 1
    return globaldata

cdef bint isNonAeroDynamic(int index, str cordpt, list globaldata, list wallpoints):
    main_pointx,main_pointy = getPoint(index, globaldata)
    cdef double cordptx = cordpt.split(",")[0]
    cdef double cordpty = cordpt.split(",")[1]
    line = shapely.geometry.LineString([[main_pointx, main_pointy], [cordptx, cordpty]])
    cdef list responselist = []
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

cpdef list generateWallPolygons(list wallpoints):
    cdef list wallPolygonData = []
    for item in wallpoints:
        polygonpts = []
        for item2 in item:
            polygonpts.append([float(item2.split(",")[0]), float(item2.split(",")[1])])
        polygontocheck = shapely.geometry.Polygon(polygonpts)
        wallPolygonData.append(polygontocheck)
    return wallPolygonData

cpdef list getWallPointArray(list globaldata):
    cdef list wallpointarray, newstuff = []
    wallpointarray = []
    cdef int startgeo, idx = 0
    startgeo = 0
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

cdef list getWallPointArrayIndex(list globaldata):
    cdef list wallpointarray, newstuff = []
    wallpointarray = []
    cdef int startgeo, idx = 0
    startgeo = 0
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


cdef list getLeftandRightPoint(int index, list globaldata):
    cdef list ptdata = globaldata[index]
    cdef int leftpt = ptdata[3]
    cdef int rightpt = ptdata[4]
    cdef list nbhs = []
    nbhs.append(leftpt)
    nbhs.append(rightpt)
    return nbhs

cpdef list replaceNeighbours(int index, list nbhs, list globaldata):
    cdef list data = globaldata[index]
    data = data[:19]
    data.append(len(nbhs))
    data = data + nbhs
    globaldata[index] = data
    return globaldata

def getAeroPointsFromSet(index,cordlist,globaldata,wallpoints):
    finallist = []
    for itm in cordlist:
        if isNonAeroDynamic(index,itm,globaldata,wallpoints) == False:
            finallist.append(itm)
    return finallist

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

cdef list cleanWallPoints(list globaldata):
    cdef list wallpoints = getWallPointArrayIndex(globaldata)
    cdef list wallpointsflat = [item for sublist in wallpoints for item in sublist]
    cdef str itm
    cdef int idx = 0
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

def checkPoints(globaldata,selectbspline,normal):
    wallptData = getWallPointArray(globaldata)
    wallptDataOr = wallptData
    wallptData = flattenList(wallptData)
    ptsToBeAdded = int(config.getConfig()["bspline"]["pointControl"])
    ptListArray = []
    perpendicularListArray = []
    cdef Py_ssize_t idx
    if not selectbspline:
        for idx,_ in enumerate(globaldata):
            printProgressBar(idx, len(globaldata) - 1, prefix="Progress:", suffix="Complete", length=50)
            if idx > 0:
                flag = getFlag(idx,globaldata)
                if flag == 1:
                    result = isConditionBad(idx,globaldata, False)
                    if(result):
                        # print(idx)
                        ptList = findNearestNeighbourWallPoints(idx,globaldata,wallptData,wallptDataOr)
                        perpendicularPt = getPerpendicularPoint(idx,globaldata,normal)
                        # print(ptList)
                        # print(perpendicularListArray)
                        if (perpendicularPt) not in perpendicularListArray:
                            ptListArray.append(ptList)
                            perpendicularListArray.append((perpendicularPt))
    else:
        selectbspline = list(map(int, selectbspline))
        for idx,itm in enumerate(selectbspline):
            printProgressBar(idx, len(selectbspline), prefix="Progress:", suffix="Complete", length=50)  
            ptList = findNearestNeighbourWallPoints(itm,globaldata,wallptData,wallptDataOr)
            perpendicularPt = getPerpendicularPoint(itm,globaldata,normal)
            if (perpendicularPt) not in perpendicularListArray:
                ptListArray.append(ptList)
                perpendicularListArray.append((perpendicularPt))

    return ptListArray,perpendicularListArray

def findNearestNeighbourWallPoints(idx,globaldata,wallptData,wallptDataOr):
    ptx,pty = getPoint(idx,globaldata)
    leastdt,leastidx = 1000,1000
    for itm in wallptData:
        if not isNonAeroDynamic(idx,itm,globaldata,wallptDataOr):
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
        if not isNonAeroDynamic(idx,itm,globaldata,wallptDataOr):
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
            return [itm.index(wallpts[0]),itm.index(wallpts[1]),idx,wallpt]

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

cdef list getInteriorPoints(list globaldata):
    cdef int i
    cdef int flag
    cdef list result = []
    for i in range(len(globaldata)):
        if i > 0:
            flag = getFlag(i, globaldata)
            if flag == 1:
                result.append(i)
    return result

cpdef void interiorConnectivityCheck(list globaldata):
    cdef Py_ssize_t idx
    cdef int flag = 0
    cdef list interiorPts = getInteriorPoints(globaldata)
    cdef int coresavail = multiprocessing.cpu_count()
    log.info("Found " + str(coresavail) + " available core(s).")
    log.info("BOOSTU BOOSTU BOOSTU")
    cdef int MAX_CORES = int(config.getConfig()["generator"]["maxCoresForReplacement"])
    log.info("Max Cores Allowed " + str(MAX_CORES))
    pool = ThreadPool(min(MAX_CORES,coresavail))
    results = []
    chunksize = math.ceil(len(interiorPts)/min(MAX_CORES,coresavail))
    globalchunks = list(chunks(interiorPts,chunksize))
    for itm in globalchunks:
        results.append(pool.apply_async(isConditionBadParallel, args=(itm, globaldata, True)))
    pool.close()
    pool.join()
    results = [r.get() for r in results]
    #print(interiorPts)
    # with nogil, parallel():
    # for idx in interiorPts:
    #     # checkConditionNumber(idx,globaldata,int(config.getConfig()["bspline"]["threshold"]))
    #     isConditionBad(idx, globaldata, True)

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
    madechanges = False
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            if flag == 0:
                xpos,xneg,_,_ = getFlags(idx,globaldata)
                if xpos == 1 or xneg == 1:
                    print(idx) 
                    madechanges = True
                    ptcordx, ptcordy = getPoint(idx,globaldata)
                    with open("adapted.txt", "a+") as text_file:
                        text_file.writelines(["%s %s " % (ptcordx, ptcordy)])
                        text_file.writelines("\n")
    if madechanges == True:
        with open("adapted.txt", "a+") as text_file:
            text_file.writelines("1000 1000\n")

def wallConnectivityCheckNearest(globaldata):
    madechanges = False
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            if flag == 0:
                xpos,xneg,_,_ = getFlags(idx,globaldata)
                if xpos == 1 or xneg == 1:
                    print(idx) 
                    madechanges = True
                    ptcord = getNearestProblemPoint(idx,globaldata)
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
            for idx,itm in enumerate(globaldata):
                if idx > 0:
                    if idx in sensorBox:
                        text_file.writelines("  " + str(idx) + "  1\n")
                    else:
                        text_file.writelines("  " + str(idx) + "  0\n")


def sparseNullifier(globaldata):
    madechanges = False
    sensorBox = []
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = getFlag(idx,globaldata)
            if flag == 0:
                xpos,xneg,_,_ = getFlags(idx,globaldata)
                if xpos == 1:
                    getXposPoints = getDWallXPosPoints(idx,globaldata)
                    for itm in getXposPoints:
                        index = getIndexFromPoint(itm,globaldata)
                        flag = getFlag(index,globaldata)
                        if flag == 0:
                            madechanges = True
                            sensorBox.append(index)
                if xneg == 1:
                    getXnegPoints = getDWallXNegPoints(idx,globaldata)
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
                   

def getPerpendicularPoint(idx,globaldata,normal):
    wallptData = getWallPointArray(globaldata)
    wallptDataOr = wallptData
    wallptData = flattenList(wallptData)
    pts = findNearestNeighbourWallPoints(idx,globaldata,wallptData,wallptDataOr)
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

def findNearestPoint(ptAtt,splineArray):
    if len(splineArray) == 0:
        print("Warning no bspline points were available")
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


def fillNeighboursIndex(index,globaldata,nbhs):
    nbhs = list(set(nbhs))
    globaldata[int(index)][20:] = nbhs
    globaldata[int(index)][19] = len(nbhs)
    return globaldata

def silentRemove(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred

def checkAeroGlobal2(globaldata,wallpointsData,wallcount):
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
        results.append(pool.apply_async(checkAeroGlobal, args=(itm, globaldata,wallpointsData,wallcount)))
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


def checkAeroGlobal(chunk,globaldata,wallpointsData,wallcount):
    # t1 = time.clock()
    for index,itm in enumerate(chunk):
        if itm is not "start":
            idx = itm[0]
            # printProgressBar(idx, len(globaldata) - 1, prefix="Progress:", suffix="Complete", length=50)    
            nbhs = getNeighbours(idx,globaldata)
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

def getNearestProblemPoint(idx,globaldata):
    xpos = getDWallXPosPoints(idx,globaldata)
    xneg = getDWallXNegPoints(idx,globaldata)
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


def updateNormals(idx,globaldata,nx,ny):
    globaldata[idx][11] = nx
    globaldata[idx][12] = ny
    return globaldata

def getNormals(idx,globaldata):
    cdef double nx = float(globaldata[idx][11])
    cdef double ny = float(globaldata[idx][12])
    return nx,ny

cdef dict calculateNormalConditionValues(int idx, list globaldata, double nxavg, double nyavg):
    cdef list nbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
    cdef list dSPosNbhs, dSNegNbhs, dNPosNbhs, dNNegNbhs
    dSPosNbhs = []
    dSNegNbhs = []
    dNPosNbhs = []
    dNNegNbhs = []
    # print(nbhs)
    _,_,_,dSPosNbhs = deltaWallNeighbourCalculation(idx,nbhs,nxavg,nyavg,True,globaldata)
    _,_,_,dSNegNbhs = deltaWallNeighbourCalculation(idx,nbhs,nxavg,nyavg,False,globaldata)
    _,_,_,dNPosNbhs = deltaWallNeighbourCalculationN(idx,nbhs,nxavg,nyavg,True,globaldata)
    _,_,_,dNNegNbhs = deltaWallNeighbourCalculationN(idx,nbhs,nxavg,nyavg,False,globaldata)
    
    cdef double dSPosCondition = weightedConditionValueForSetOfPointsNormalWithInputs(idx,globaldata,dSPosNbhs,nxavg,nyavg)
    cdef double dSNegCondition = weightedConditionValueForSetOfPointsNormalWithInputs(idx,globaldata,dSNegNbhs,nxavg,nyavg)
    cdef double dNPosCondition = weightedConditionValueForSetOfPointsNormalWithInputs(idx,globaldata,dNPosNbhs,nxavg,nyavg)
    cdef double dNNegCondition = weightedConditionValueForSetOfPointsNormalWithInputs(idx,globaldata,dNNegNbhs,nxavg,nyavg)

    cdef dict result = {}
    result = {"spos":dSPosNbhs,"sposCond":dSPosCondition,"sneg":dSNegNbhs,"snegCond":dSNegCondition,"npos":dNPosNbhs,"nposCond":dNPosCondition,"nneg":dNNegNbhs,"nnegCond":dNNegCondition}
    return result

cdef void isConditionBadParallel(list data, list globaldata, bint verbose):
    cdef int idx
    for idx in data:
        isConditionBad(idx, globaldata, verbose)

cpdef bint isConditionBad(int idx, list globaldata, bint verbose):
    cdef double nx,ny
    nx = 0
    ny = 0
    cdef dict condResult
    cdef list dSPosNbhs, dSNegNbhs, dNPosNbhs, dNNegNbhs
    cdef double dSPosCondition, dSNegCondition, dNPosCondition, dNNegCondition
    dSPosNbhs = []
    dSNegNbhs = []
    dNPosNbhs = []
    dNNegNbhs = []
    dSPosCondition = 0
    dSNegCondition = 0
    dNPosCondition = 0
    dNNegCondition = 0
    nx,ny = getNormals(idx,globaldata)
    condResult = calculateNormalConditionValues(idx,globaldata,nx,ny)
    dSPosNbhs,dSNegNbhs,dNPosNbhs,dNNegNbhs = condResult["spos"], condResult["sneg"], condResult["npos"], condResult["nneg"]
    dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition = condResult["sposCond"], condResult["snegCond"], condResult["nposCond"], condResult["nnegCond"]
    maxCond = max(dSPosCondition,dSNegCondition,dNPosCondition,dNNegCondition)
    if maxCond > float(config.getConfig()["bspline"]["threshold"]) or math.isnan(dSPosCondition) or math.isnan(dSNegCondition) or math.isnan(dNPosCondition) or math.isnan(dNNegCondition):
        # print(idx)
        if verbose:
            print(idx,len(dSPosNbhs),dSPosCondition,len(dSNegNbhs),dSNegCondition,len(dNPosNbhs),dNPosCondition,len(dNNegNbhs),dNNegCondition)
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

def pushCache(globaldata):
    globaldata.pop(0)
    config.setKeyVal("globaldata",globaldata)
    log.info("Pushed to Cache!")

def verifyIntegrity():
    loadWall = dict(config.load_obj("wall"))
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
        configData = config.load_obj("config")
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
            config.save_obj(configData,"config")
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
            config.save_obj(configData,"config")
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

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')