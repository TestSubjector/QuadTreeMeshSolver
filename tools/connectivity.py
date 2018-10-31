import core
from config import getConfig
import progress

def connectivityCheck(globaldata):
    for idx,itm in enumerate(globaldata):
        progress.printProgressBar(
            idx,
            len(globaldata) - 1,
            prefix="Progress:",
            suffix="Complete",
            length=50,
        )
        if(idx >0):
            if core.getFlag(idx,globaldata) == 0 or core.getFlag(idx,globaldata) == 2:
                result = connectivityCheckWallandOuterPoint(idx,globaldata)
                globaldata = core.setFlags(idx,globaldata,result)
            # else:
            #     result = connectivityCheckInteriorPoint(idx,globaldata)
            #     globaldata = setFlags(idx,globaldata,result)
    return globaldata


def connectivityCheckWallandOuterPoint(index,globaldata):
    result = []
    WALL_OUTER_THRESHOLD = int(getConfig()["triangulate"]["triangle"]["wallandOuterThreshold"])
    xpos = len(core.getDWallXPosPoints(index,globaldata))
    xneg = len(core.getDWallXNegPoints(index,globaldata))
    xposConditionValue = core.getWeightedNormalConditionValueofWallXPos(index,globaldata)
    xnegConditionValue = core.getWeightedNormalConditionValueofWallXNeg(index,globaldata)
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

def connectivityCheckInteriorPoint(index,globaldata):
    result = []
    INTERIOR_THRESHOLD = int(getConfig()["triangulate"]["triangle"]["interiorThreshold"])
    xpos = len(core.getDXPosPoints(index,globaldata))
    xneg = len(core.getDXNegPoints(index,globaldata))
    ypos = len(core.getDYPosPoints(index,globaldata))
    yneg = len(core.getDYNegPoints(index,globaldata))
    xposConditionValue = core.getWeightedInteriorConditionValueofXPos(index,globaldata)
    xnegConditionValue = core.getWeightedInteriorConditionValueofXNeg(index,globaldata)
    yposConditionValue = core.getWeightedInteriorConditionValueofYPos(index,globaldata)
    ynegConditionValue = core.getWeightedInteriorConditionValueofYNeg(index,globaldata)
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