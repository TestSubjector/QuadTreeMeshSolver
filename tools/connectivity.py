
from tqdm import tqdm
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def connectivityCheck(globaldata, wallouter = True, interior = False):
    conf = core.getConfig()
    for idx,itm in enumerate(tqdm(globaldata)):
        if(idx >0):
            if (core.getFlag(idx,globaldata) == 0 or core.getFlag(idx,globaldata) == 2) and wallouter == True:
                result = connectivityCheckWallandOuterPoint(idx,globaldata, conf)
                globaldata = core.setFlagsFromList(idx,globaldata,result)
            else:
                if interior == True:
                    result = connectivityCheckInteriorPoint(idx,globaldata, conf)
                    globaldata = core.setFlagsFromList(idx,globaldata,result)
    return globaldata


def connectivityCheckWallandOuterPoint(index, globaldata, conf):
    result = []
    WALL_OUTER_THRESHOLD = int(conf["triangulate"]["triangle"]["wallandOuterThreshold"])
    xpos = len(core.getDWallXPosPoints(index,globaldata,conf))
    xneg = len(core.getDWallXNegPoints(index,globaldata,conf))
    xposConditionValue = core.getWeightedNormalConditionValueofWallXPos(index,globaldata,conf)
    xnegConditionValue = core.getWeightedNormalConditionValueofWallXNeg(index,globaldata,conf)
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

def connectivityCheckInteriorPoint(index, globaldata, conf):
    result = []
    INTERIOR_THRESHOLD = int(conf["triangulate"]["triangle"]["interiorThreshold"])
    xpos = len(core.getDXPosPoints(index,globaldata))
    xneg = len(core.getDXNegPoints(index,globaldata))
    ypos = len(core.getDYPosPoints(index,globaldata))
    yneg = len(core.getDYNegPoints(index,globaldata))
    xposConditionValue = core.getWeightedInteriorConditionValueofXPos(index,globaldata,conf)
    xnegConditionValue = core.getWeightedInteriorConditionValueofXNeg(index,globaldata,conf)
    yposConditionValue = core.getWeightedInteriorConditionValueofYPos(index,globaldata,conf)
    ynegConditionValue = core.getWeightedInteriorConditionValueofYNeg(index,globaldata,conf)
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
        if idx > 0 and int(core.getFlag(idx,globaldata)) == 1:
            xpos,xneg,ypos,yneg = core.getFlags(idx,globaldata)
            if(xpos == 1 or xneg == 1 or ypos == 1 or yneg == 1):
                deletionpts.append(idx)
    return deletionpts