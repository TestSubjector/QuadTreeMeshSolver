from core import *
from config import getConfig
from tqdm import trange, tqdm


def connectivityCheck(globaldata, badPoints, configData):
    badPointsNew = []
    if len(badPoints) == 0:
        for idx in trange(len(globaldata)):
            if(idx >0):
                if(getFlag(idx,globaldata) == 0 or getFlag(idx,globaldata) == 2):
                    result = connectivityCheckWallandOuterPoint(idx,globaldata, configData)
                    if 1 in result or 2 in result:
                        badPointsNew.append(idx)
                    globaldata = setFlags(idx,globaldata,result)
                else:
                    result = connectivityCheckInteriorPoint(idx,globaldata, configData)
                    if 1 in result or 2 in result:
                        badPointsNew.append(idx)
                    globaldata = setFlags(idx,globaldata,result)
    else:
        for _,idx in enumerate(tqdm(badPoints)):
            if(idx >0):
                if(getFlag(idx,globaldata) == 0 or getFlag(idx,globaldata) == 2):
                    result = connectivityCheckWallandOuterPoint(idx,globaldata, configData)
                    if 1 in result or 2 in result:
                        badPointsNew.append(idx)
                    globaldata = setFlags(idx,globaldata,result)
                else:
                    result = connectivityCheckInteriorPoint(idx,globaldata, configData)
                    if 1 in result or 2 in result:
                        badPointsNew.append(idx)
                    globaldata = setFlags(idx,globaldata,result)
    return globaldata,badPointsNew


def connectivityCheckWallandOuterPoint(index, globaldata, configData):
    result = []
    WALL_OUTER_THRESHOLD = int(configData["triangulate"]["triangle"]["wallandOuterThreshold"])
    xpos = len(getDWallXPosPoints(index,globaldata, configData))
    xneg = len(getDWallXNegPoints(index,globaldata, configData))
    xposConditionValue = getWeightedNormalConditionValueofWallXPos(index,globaldata, configData)
    xnegConditionValue = getWeightedNormalConditionValueofWallXNeg(index,globaldata, configData)
    if(xposConditionValue < WALL_OUTER_THRESHOLD):
        if(xpos < 3):
            result.append(2)
        else:
            result.append(0)
    else:
        result.append(1)
    if(xnegConditionValue < WALL_OUTER_THRESHOLD):
        if(xneg < 3):
            result.append(2)
        else:
            result.append(0)
    else:
        result.append(1)
    result.append(0)
    result.append(0)
    return result

def connectivityCheckInteriorPoint(index, globaldata, configData):
    result = []
    INTERIOR_THRESHOLD = int(configData["triangulate"]["triangle"]["interiorThreshold"])
    xpos = len(getDXPosPoints(index,globaldata))
    xneg = len(getDXNegPoints(index,globaldata))
    ypos = len(getDYPosPoints(index,globaldata))
    yneg = len(getDYNegPoints(index,globaldata))
    xposConditionValue = getWeightedInteriorConditionValueofXPos(index,globaldata)
    xnegConditionValue = getWeightedInteriorConditionValueofXNeg(index,globaldata)
    yposConditionValue = getWeightedInteriorConditionValueofYPos(index,globaldata)
    ynegConditionValue = getWeightedInteriorConditionValueofYNeg(index,globaldata)
    if(xposConditionValue < INTERIOR_THRESHOLD):
        if(xpos < 3):
            result.append(2)
        else:
            result.append(0)
    else:
        result.append(1)
    if(xnegConditionValue < INTERIOR_THRESHOLD):
        if(xneg < 3):
            result.append(2)
        else:
            result.append(0)
    else:
        result.append(1)
    if(yposConditionValue < INTERIOR_THRESHOLD):
        if(ypos < 3):
            result.append(2)
        else:
            result.append(0)
    else:
        result.append(1)
    if(ynegConditionValue < INTERIOR_THRESHOLD):
        if(yneg < 3):
            result.append(2)
        else:
            result.append(0)
    else:
        result.append(1)
    return result

def findDeletionPoints(globaldata):
    deletionpts = []
    for idx,itm in enumerate(globaldata):
        if idx > 0 and int(getFlag(idx,globaldata)) == 1:
            xpos,xneg,ypos,yneg = getFlags(idx,globaldata)
            if(xpos == 1 or xneg == 1 or ypos == 1 or yneg == 1):
                deletionpts.append(idx)
    return deletionpts