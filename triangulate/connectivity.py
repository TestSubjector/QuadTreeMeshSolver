from tqdm import trange, tqdm
import sys, os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def connectivityCheck(globaldata, badPoints, configData):
    badPointsNew = []
    if len(badPoints) == 0:
        for idx in trange(len(globaldata)):
            if(idx >0):
                if(core.getFlag(idx,globaldata) == 0 or core.getFlag(idx,globaldata) == 2):
                    result = connectivityCheckWallandOuterPoint(idx,globaldata, configData)
                    if 1 in result or 2 in result:
                        badPointsNew.append(idx)
                    globaldata = core.setFlagsFromList(idx,globaldata,result)
                else:
                    result = connectivityCheckInteriorPoint(idx,globaldata, configData)
                    if 1 in result or 2 in result:
                        badPointsNew.append(idx)
                    globaldata = core.setFlagsFromList(idx,globaldata,result)
    else:
        for _,idx in enumerate(tqdm(badPoints)):
            if(idx >0):
                if(core.getFlag(idx,globaldata) == 0 or core.getFlag(idx,globaldata) == 2):
                    result = connectivityCheckWallandOuterPoint(idx,globaldata, configData)
                    if 1 in result or 2 in result:
                        badPointsNew.append(idx)
                    globaldata = core.setFlagsFromList(idx,globaldata,result)
                else:
                    result = connectivityCheckInteriorPoint(idx,globaldata, configData)
                    if 1 in result or 2 in result:
                        badPointsNew.append(idx)
                    globaldata = core.setFlagsFromList(idx,globaldata,result)
    return globaldata,badPointsNew


def connectivityCheckWallandOuterPoint(index, globaldata, configData):
    result = []
    WALL_OUTER_THRESHOLD = int(configData["triangulate"]["triangle"]["wallandOuterThreshold"])
    xpos = len(core.getDWallXPosPoints(index,globaldata, configData))
    xneg = len(core.getDWallXNegPoints(index,globaldata, configData))
    xposConditionValue = core.getWeightedNormalConditionValueofWallXPos(index,globaldata, configData)
    xnegConditionValue = core.getWeightedNormalConditionValueofWallXNeg(index,globaldata, configData)
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
    xpos = len(core.getDXPosPoints(index,globaldata))
    xneg = len(core.getDXNegPoints(index,globaldata))
    ypos = len(core.getDYPosPoints(index,globaldata))
    yneg = len(core.getDYNegPoints(index,globaldata))
    xposConditionValue = core.getWeightedInteriorConditionValueofXPos(index,globaldata, configData)
    xnegConditionValue = core.getWeightedInteriorConditionValueofXNeg(index,globaldata, configData)
    yposConditionValue = core.getWeightedInteriorConditionValueofYPos(index,globaldata, configData)
    ynegConditionValue = core.getWeightedInteriorConditionValueofYNeg(index,globaldata, configData)
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

def writeNormalsToText(globaldata, configData):
    for idx,itm in enumerate(globaldata):
        if idx > 0:
            flag = core.getFlag(idx,globaldata)
            if(flag == 0):
                x,y = core.getPoint(idx,globaldata)
                nx,ny = core.normalCalculation(idx,globaldata,True, configData)
                with open("file.dat", "a") as text_file:
                    text_file.writelines(str(x) + " " + str(y) + " " + str(nx) + " " + str(ny))
                    text_file.writelines("\n")


## To Plot
# plot 'file.dat' using 1:2:3:4 with vectors head filled lt 2


def writeConditionValuesForWall(globaldata, configData):
    for idx,itm in enumerate(globaldata):
        if idx > 0:
            flag = core.getFlag(idx,globaldata)
            if(flag == 0):
                x,y = core.getPoint(idx,globaldata)
                xpos = core.getWeightedNormalConditionValueofWallXPos(idx,globaldata, configData)
                xneg = core.getWeightedNormalConditionValueofWallXNeg(idx,globaldata, configData)
                xposcount = len(core.getDWallXPosPoints(idx,globaldata, configData))
                xnegcount = len(core.getDWallXNegPoints(idx,globaldata, configData))
                if(xpos > 100 or xneg > 100 or xposcount < 3 or xnegcount < 3):
                    with open("condition.dat", "a") as text_file:
                        text_file.writelines(str(x) + " " + str(y) + " " + str(xposcount) + " " + str(xpos) + " " + str(xnegcount) + " " + str(xneg))
                        text_file.writelines("\n")