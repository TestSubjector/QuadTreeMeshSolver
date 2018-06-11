import numpy as np
import math

def getFlag(indexval,list):
    indexval = int(indexval)
    return list[indexval][5]

def getNeighbours(index,globaldata):
    index = int(index)
    ptdata = globaldata[index]
    ptdata = ptdata[12:]
    return ptdata

def getPoint(index,globaldata):
    index = int(index)
    ptdata = globaldata[index]
    ptx = float(ptdata[1])
    pty = float(ptdata[2])
    return ptx,pty

def getPointxy(index,globaldata):
    index = int(index)
    ptx,pty = getPoint(index,globaldata)
    return str(ptx) + "," + str(pty)

def convertIndexToPoints(indexarray,globaldata):
    ptlist = []
    for item in indexarray:
        item = int(item)
        ptx,pty = getPoint(item,globaldata)
        ptlist.append((str(ptx) + "," + str(pty)))
    return ptlist

def weightedConditionValueForSetOfPoints(index,globaldata,points):
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
        deltaX = (nbhitemX - mainptx)
        deltaY = (nbhitemY - mainpty)
        d = math.sqrt(deltaX**2 + deltaY**2)
        if (d == 0):
            continue
        power = -2
        w = d ** power
        deltaSumXX = deltaSumXX + w * (deltaX**2)
        deltaSumYY = deltaSumYY + w * (deltaY**2)
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

def deltaX(xcord,orgxcord):
    return float(orgxcord - xcord)

def deltaY(ycord,orgycord):
    return float(orgycord - ycord)

def deltaNeighbourCalculation(currentneighbours,currentcord,isxcord,isnegative):
    xpos,xneg,ypos,yneg = 0,0,0,0
    temp = []
    for item in currentneighbours:
        if((deltaX(float(currentcord.split(",")[0]), float(item.split(",")[0]))) <= 0):
            if(isxcord and (not isnegative)):
                temp.append(item)
            xpos = xpos + 1
        if((deltaX(float(currentcord.split(",")[0]), float(item.split(",")[0]))) >= 0):
            if(isxcord and isnegative):
                temp.append(item)
            xneg = xneg + 1
        if((deltaY(float(currentcord.split(",")[1]), float(item.split(",")[1]))) <= 0):
            if((not isxcord) and (not isnegative)):
                temp.append(item)
            ypos = ypos + 1
        if((deltaY(float(currentcord.split(",")[1]), float(item.split(",")[1]))) >= 0):
            if((not isxcord) and isnegative):
                temp.append(item)
            yneg = yneg + 1
    return xpos,ypos,xneg,yneg,temp

def getWeightedInteriorConditionValueofXPos(index,globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPointxy(index,globaldata),True,False)
    return weightedConditionValueForSetOfPoints(index,globaldata,mypoints)

def getWeightedInteriorConditionValueofXNeg(index,globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPointxy(index,globaldata),True,True)
    return weightedConditionValueForSetOfPoints(index,globaldata,mypoints)

def getWeightedInteriorConditionValueofYPos(index,globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPointxy(index,globaldata),False,False)
    return weightedConditionValueForSetOfPoints(index,globaldata,mypoints)

def getWeightedInteriorConditionValueofYNeg(index,globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPointxy(index,globaldata),False,True)
    return weightedConditionValueForSetOfPoints(index,globaldata,mypoints)

def getDXPosPoints(index,globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPointxy(index,globaldata),True,False)
    return mypoints

def getDXNegPoints(index,globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPointxy(index,globaldata),True,True)
    return mypoints

def getDYPosPoints(index,globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPointxy(index,globaldata),False,False)
    return mypoints

def getDYNegPoints(index,globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPointxy(index,globaldata),False,True)
    return mypoints

def checkConditionNumber(index, globaldata, threshold):
    xpos = getWeightedInteriorConditionValueofXPos(index,globaldata)
    xneg = getWeightedInteriorConditionValueofXNeg(index,globaldata)
    ypos = getWeightedInteriorConditionValueofYPos(index,globaldata)
    yneg = getWeightedInteriorConditionValueofYNeg(index,globaldata)
    dSPointXPos = getDXPosPoints(index, globaldata)
    dSPointXNeg = getDXNegPoints(index, globaldata)
    dSPointYPos = getDYPosPoints(index, globaldata)
    dSPointYNeg = getDYNegPoints(index, globaldata)
    if(xneg > threshold or xpos > threshold or ypos > threshold or yneg > threshold):
        print(index, len(dSPointXPos),xpos,len(dSPointXNeg),xneg,len(dSPointYPos),ypos,len(dSPointYNeg),yneg)

