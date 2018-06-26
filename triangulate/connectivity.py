from core import *

def connectivityCheck(globaldata):
    for idx,itm in enumerate(globaldata):
        printProgressBar(
            idx,
            len(globaldata) - 1,
            prefix="Progress:",
            suffix="Complete",
            length=50,
        )
        if(idx>0):
            if(getFlag(idx,globaldata) == 0 or getFlag(idx,globaldata) == 2):
                result = connectivityCheckWallandOuterPoint(idx,globaldata)
                globaldata = setFlags(idx,globaldata,result)
            else:
                result = connectivityCheckInteriorPoint(idx,globaldata)
                globaldata = setFlags(idx,globaldata,result)
    return globaldata


def connectivityCheckWallandOuterPoint(index,globaldata):
    result = []
    xpos = len(getDXPosPoints(index,globaldata))
    xneg = len(getDXNegPoints(index,globaldata))
    xposConditionValue = getWeightedInteriorConditionValueofXPos(index,globaldata)
    xnegConditionValue = getWeightedInteriorConditionValueofXNeg(index,globaldata)
    if(xposConditionValue < 30):
        if(xpos < 3):
            result.append(2)
        else:
            result.append(0)
    else:
        result.append(1)
    if(xnegConditionValue < 30):
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
    xpos = len(getDXPosPoints(index,globaldata))
    xneg = len(getDXNegPoints(index,globaldata))
    ypos = len(getDYPosPoints(index,globaldata))
    yneg = len(getDYNegPoints(index,globaldata))
    xposConditionValue = getWeightedInteriorConditionValueofXPos(index,globaldata)
    xnegConditionValue = getWeightedInteriorConditionValueofXNeg(index,globaldata)
    yposConditionValue = getWeightedInteriorConditionValueofYPos(index,globaldata)
    ynegConditionValue = getWeightedInteriorConditionValueofYNeg(index,globaldata)
    if(xposConditionValue < 30):
        if(xpos < 3):
            result.append(2)
        else:
            result.append(0)
    else:
        result.append(1)
    if(xnegConditionValue < 30):
        if(xneg < 3):
            result.append(2)
        else:
            result.append(0)
    else:
        result.append(1)
    if(yposConditionValue < 30):
        if(ypos < 3):
            result.append(2)
        else:
            result.append(0)
    else:
        result.append(1)
    if(ynegConditionValue < 30):
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
        if idx > 0:
            xpos,xneg,ypos,yneg = getFlags(idx,globaldata)
            if(xpos == 1 or xneg == 1 or ypos == 1 or yneg == 1):
                deletionpts.append(idx)
    return deletionpts