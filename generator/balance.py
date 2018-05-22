import math
import numpy as np
from numpy import linalg as LA
from misc import *

def normalCalculation(index,cord,hashtable,globaldata,wallpoint):
    nx = 0
    ny = 0
    cordx = float(cord.split(",")[0])
    cordy = float(cord.split(",")[1])
    val = hashtable.index(cord)
    pointdata = globaldata[val - 1]
    if(wallpoint):
        leftpoint = hashtable[pointdata[3]]
        rightpoint = hashtable[pointdata[4]]
    else:
        leftpoint = pointdata[3]
        rightpoint = pointdata[4]
    leftpointx = float(leftpoint.split(",")[0])
    leftpointy = float(leftpoint.split(",")[1])
    rightpointx = float(rightpoint.split(",")[0])
    rightpointy = float(rightpoint.split(",")[1])
    if(not wallpoint):
        nx1 = leftpointy - cordy
        nx2 = cordy - rightpointy
        ny1 = leftpointx - cordx
        ny2 = cordx - rightpointx
    nx1 = cordy - leftpointy
    nx2 = rightpointy - cordy
    ny1 = cordx - leftpointx
    ny2 = rightpointx - cordx
    nx = (nx1+nx2)/2
    ny = (ny1+ny2)/2
    det = math.sqrt((nx*nx) + (ny*ny))
    if(not wallpoint):
        nx = nx/det
    else:
        nx = (-nx)/det
    ny = ny/det
    return nx,ny

def conditionCheckWithNeighbours(index, globaldata, cord, nbh):
    item = cord
    mainptx = float(item.split(",")[0])
    mainpty = float(item.split(",")[1])
    deltaSumX = 0
    deltaSumY = 0
    deltaSumXY = 0
    data = []
    for nbhitem in nbh:
        nbhitemX = float(nbhitem.split(",")[0])
        nbhitemY = float(nbhitem.split(",")[1])
        deltaSumX = deltaSumX + (nbhitemX - mainptx) ** 2
        deltaSumY = deltaSumY + (nbhitemY - mainpty) ** 2
        deltaSumXY = deltaSumXY + (nbhitemX - mainptx) * (nbhitemY - mainpty)
    data.append(deltaSumX)
    data.append(deltaSumXY)
    data.append(deltaSumXY)
    data.append(deltaSumY)
    random = np.array(data)
    shape = (2, 2)
    random = random.reshape(shape)
    s = np.linalg.svd(random, full_matrices=False, compute_uv=False)
    s = max(s) / min(s)
    return s


def minConditionValue(index, globaldata, cord, nbhs):
    item = cord
    mainptx = float(item.split(",")[0])
    mainpty = float(item.split(",")[1])
    nbh = getNeighbours(index, globaldata)
    nbh = nbh + nbhs
    deltaSumX = 0
    deltaSumY = 0
    deltaSumXY = 0
    data = []
    for nbhitem in nbh:
        nbhitemX = float(nbhitem.split(",")[0])
        nbhitemY = float(nbhitem.split(",")[1])
        deltaSumX = deltaSumX + (nbhitemX - mainptx) ** 2
        deltaSumY = deltaSumY + (nbhitemY - mainpty) ** 2
        deltaSumXY = deltaSumXY + (nbhitemX - mainptx) * (nbhitemY - mainpty)
    data.append(deltaSumX)
    data.append(deltaSumXY)
    data.append(deltaSumXY)
    data.append(deltaSumY)
    random = np.array(data)
    shape = (2, 2)
    random = random.reshape(shape)
    w, v = LA.eig(random)
    w = max(w) / min(w)
    return w


def minCondition(index, globaldata, cord, nbs, threshold):
    nbsMin = []
    for index, item in enumerate(nbs):
        w = minConditionValue(index, globaldata, cord, nbs)
        if (w < threshold):
            nbsMin.append([item, index, w])
        nbsMin.sort(key=lambda x: x[2])
        nbsFinalList = []
        for item in nbsMin:
            nbsFinalList.append(item[0])
        return nbsFinalList

def conditionCheck(index, globaldata, cord):
    item = cord
    mainptx = float(item.split(",")[0])
    mainpty = float(item.split(",")[1])
    nbh = getNeighbours(index, globaldata)
    deltaSumX = 0
    deltaSumY = 0
    deltaSumXY = 0
    data = []
    for nbhitem in nbh:
        nbhitemX = float(nbhitem.split(",")[0])
        nbhitemY = float(nbhitem.split(",")[1])
        deltaSumX = deltaSumX + (nbhitemX - mainptx) ** 2
        deltaSumY = deltaSumY + (nbhitemY - mainpty) ** 2
        deltaSumXY = deltaSumXY + (nbhitemX - mainptx) * (nbhitemY - mainpty)
    data.append(deltaSumX)
    data.append(deltaSumXY)
    data.append(deltaSumXY)
    data.append(deltaSumY)
    random = np.array(data)
    shape = (2, 2)
    random = random.reshape(shape)
    w, v = LA.eig(random)
    w = max(w) / min(w)
    s = np.linalg.svd(random, full_matrices=False, compute_uv=False)
    s = max(s) / min(s)
    return w, s

def minDistance(neighbours,cord):
    dists = []
    for item in neighbours:
        dists.append(euclideanDistance(item,cord))
    dists.sort(key=takeFirst)
    dists2 = []
    for item in dists:
        dists2.append(item[1])
    return dists2

def deltaWallNeighbourCalculation(index,currentneighbours,currentcord,nx,ny,giveposdelta,globaldata):
    deltaspos,deltasneg,deltaszero = 0,0,0
    nx = float(nx)
    ny = float(ny)
    tx = float(ny)
    ty = -float(nx)
    xcord = float(currentcord.split(",")[0])
    ycord = float(currentcord.split(",")[1])
    output = []
    for item in currentneighbours:
        itemx = float(item.split(",")[0])
        itemy = float(item.split(",")[1])
        deltas = (tx * (itemx - xcord)) + (ty * (itemy - ycord))
        # if(index==730):
        #     print(deltas)
        if(deltas <= 0):
            if(giveposdelta):
                output.append(item)
            deltaspos = deltaspos + 1
        if(deltas >= 0):
            if(not giveposdelta):
                output.append(item)
            deltasneg = deltasneg + 1
        if(deltas == 0):
            deltaszero = deltaszero + 1
    if(getFlag(index,globaldata)==2):
        None
        # print(index,len(currentneighbours),deltaspos,deltasneg,deltaszero)
    return deltaspos,deltasneg,deltaszero,output