from balance import *
from misc import *
from logger import writeLog
import numpy as np
import shapely.geometry
from shapely import wkt
from shapely.ops import linemerge, unary_union, polygonize
import math
from numpy.linalg import inv

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

def conditionValueOfPointFull(index,globaldata):
    mainptx = float(globaldata[index][1])
    mainpty = float(globaldata[index][2])
    deltaSumX = 0
    deltaSumY = 0
    deltaSumXY = 0
    data = []
    nbhs = getNeighbours(index,globaldata)
    for nbhitem in nbhs:
        nbhitemX = float(nbhitem.split(",")[0])
        nbhitemY = float(nbhitem.split(",")[1])
        deltaSumX = deltaSumX + ((nbhitemX - mainptx)**2)
        deltaSumY = deltaSumY + ((nbhitemY - mainpty)**2)
        deltaSumXY = deltaSumXY + (nbhitemX - mainptx) * (nbhitemY - mainpty)
    data.append(deltaSumX)
    data.append(deltaSumXY)
    data.append(deltaSumXY)
    data.append(deltaSumY)
    random = np.array(data)
    shape = (2, 2)
    random = random.reshape(shape)
    s = np.linalg.svd(random, full_matrices=False, compute_uv=False)
    if(min(s)==0):
        print(index,"ITS LOW")
    s = max(s) / min(s)
    return s

def conditionValueForSetOfPoints(index,globaldata,points):
    mainptx = float(globaldata[index][1])
    mainpty = float(globaldata[index][2])
    deltaSumX = 0
    deltaSumY = 0
    deltaSumXY = 0
    data = []
    nbhs = points
    for nbhitem in nbhs:
        nbhitemX = float(nbhitem.split(",")[0])
        nbhitemY = float(nbhitem.split(",")[1])
        deltaSumX = deltaSumX + ((nbhitemX - mainptx)**2)
        deltaSumY = deltaSumY + ((nbhitemY - mainpty)**2)
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

def conditionValueForSetOfPoints2(index,globaldata,points,mvalue):
    mvalue = float(mvalue)
    mainptx = float(globaldata[index][1])
    mainpty = float(globaldata[index][2])
    deltaSumX = 0
    deltaSumY = 0
    deltaSumXY = 0
    data = []
    nbhs = points
    for nbhitem in nbhs:
        nbhitemX = float(nbhitem.split(",")[0])
        nbhitemY = float(nbhitem.split(",")[1])
        deltaSumX = deltaSumX + ((nbhitemX - mainptx)**2)
        deltaSumY = deltaSumY + ((nbhitemY - mainpty)**2)
        deltaSumXY = deltaSumXY + (nbhitemX - mainptx) * (nbhitemY - mainpty)
    data.append(deltaSumX)
    data.append(deltaSumXY)
    data.append(deltaSumXY)
    data.append(deltaSumY)
    A = np.array(data)
    shape = (2, 2)
    A = A.reshape(shape)
    I = np.identity(2)
    X = mvalue*I
    M = A+X
    Minv = inv(M)
    Y = np.identity(2) + (mvalue*Minv)
    Anewinv = np.matmul(Minv,Y)
    Anew = inv(Anewinv)
    s = np.linalg.svd(Anew, full_matrices=False, compute_uv=False)
    s = max(s) / min(s)
    return s  
    

def getInteriorConditionValueofXPos(index,globaldata,hashtable):
    nbhs = getNeighbours(index,globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPoint(index,globaldata),True,False)
    return conditionValueForSetOfPoints(index,globaldata,mypoints)

def getInteriorConditionValueofXNeg(index,globaldata,hashtable):
    nbhs = getNeighbours(index,globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPoint(index,globaldata),True,True)
    return conditionValueForSetOfPoints(index,globaldata,mypoints)

def getInteriorConditionValueofYPos(index,globaldata,hashtable):
    nbhs = getNeighbours(index,globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPoint(index,globaldata),False,False)
    return conditionValueForSetOfPoints(index,globaldata,mypoints)

def getInteriorConditionValueofYNeg(index,globaldata,hashtable):
    nbhs = getNeighbours(index,globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPoint(index,globaldata),False,True)
    return conditionValueForSetOfPoints(index,globaldata,mypoints)

def getInteriorConditionValueofXPos2(index,globaldata,hashtable):
    nbhs = getNeighbours(index,globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPoint(index,globaldata),True,False)
    return conditionValueForSetOfPoints2(index,globaldata,mypoints,10e-8)

def getInteriorConditionValueofXNeg2(index,globaldata,hashtable):
    nbhs = getNeighbours(index,globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPoint(index,globaldata),True,True)
    return conditionValueForSetOfPoints2(index,globaldata,mypoints,10e-8)

def getInteriorConditionValueofYPos2(index,globaldata,hashtable):
    nbhs = getNeighbours(index,globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPoint(index,globaldata),False,False)
    return conditionValueForSetOfPoints2(index,globaldata,mypoints,10e-8)

def getInteriorConditionValueofYNeg2(index,globaldata,hashtable):
    nbhs = getNeighbours(index,globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPoint(index,globaldata),False,True)
    return conditionValueForSetOfPoints2(index,globaldata,mypoints,10e-8)

def getDXPosPoints(index,globaldata,hashtable):
    nbhs = getNeighbours(index,globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPoint(index,globaldata),True,False)
    return mypoints

def getDXNegPoints(index,globaldata,hashtable):
    nbhs = getNeighbours(index,globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPoint(index,globaldata),True,True)
    return mypoints

def getDYPosPoints(index,globaldata,hashtable):
    nbhs = getNeighbours(index,globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPoint(index,globaldata),False,False)
    return mypoints

def getDYNegPoints(index,globaldata,hashtable):
    nbhs = getNeighbours(index,globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPoint(index,globaldata),False,True)
    return mypoints


def conditionValueFixForXPos(index,globaldata,hashtable,threshold,wallpoints,control):
    initialConditionValue = getInteriorConditionValueofXPos(index,globaldata,hashtable)
    dSPoints = getDXPosPoints(index,globaldata,hashtable)
    # writeLog([index,initialConditionValue)
    if(initialConditionValue > threshold):
        # Point Failed Threshold. Let's try balancing it.
        oldnbhs = getNeighbours(index,globaldata)
        # Get Neighbour of Neighbours
        newnbhs = []
        for itm in oldnbhs:
            nbhofnbh = getNeighbours(getIndexOf(itm,hashtable),globaldata)
            # Removes original point and its neighbours. We only want new neighbours
            newnbhs = newnbhs + list(set(nbhofnbh) - set([getPoint(index,globaldata)]) - set(oldnbhs) - set(newnbhs))
        # We got a new list of points to be tested against lets find the points.
        _,_,_,_,newdxpospoints = deltaNeighbourCalculation(newnbhs,getPoint(index,globaldata),True,False)
        if(len(newdxpospoints)==0):
            writeLog(["We tried finding neighbour of neighbours but none satisfy the delta xpos condition for",getPoint(index,globaldata)])
        else:
            finalList = []
            nothresList = []
            for newitm in newdxpospoints:
                if(not isNonAeroDynamic(index,newitm,globaldata,wallpoints)):
                    tempnbh = []
                    tempnbh = dSPoints
                    tempnbh = tempnbh + [newitm]
                    conditionVal = conditionValueForSetOfPoints(index,globaldata,tempnbh)
                    nothresList.append([newitm,conditionVal])
                    if(conditionVal < threshold):
                        finalList.append([newitm,conditionVal])
                else:
                    writeLog(["Found non aero point skipping."])
            if(len(finalList) == 0 or finalList is None):
                writeLog(["We tried finding points to reduce threshold value to",threshold,"but couldn't find any for index",index])
                writeLog(["It's condition value for dx pos is",initialConditionValue])
                if(len(nothresList) != 0):
                    writeLog(["The least we can reduce it to is",nothresList[0][1]])
                    if(float(nothresList[0][1]) < initialConditionValue):
                        pointToBeAdded = nothresList[0][0]
                        appendNeighbours([pointToBeAdded],index,globaldata)
                        initialConditionValue = getInteriorConditionValueofXPos(index,globaldata,hashtable)
                        writeLog(["We will be running again to reduce further"])
                        if(control <= 0):                        
                            conditionValueFixForXPos(index,globaldata,hashtable,threshold,wallpoints, control + 1)
                    else:
                        writeLog(["We don't want to worsen the condition value so we are not gonna do anything else"])
                else:
                    writeLog(["We couldn't find a single point to reduce it to."])
            else:
                finalList.sort(key=lambda x: x[1])
                pointToBeAdded = finalList[0][0]
                appendNeighbours([pointToBeAdded],index,globaldata)
                initialConditionValue = getInteriorConditionValueofXPos(index,globaldata,hashtable)
                # writeLog([index,initialConditionValue)

def conditionValueFixForXNeg(index,globaldata,hashtable,threshold,wallpoints,control):
    initialConditionValue = getInteriorConditionValueofXNeg(index,globaldata,hashtable)
    dSPoints = getDXNegPoints(index,globaldata,hashtable)
    # writeLog([index,initialConditionValue)
    if(initialConditionValue > threshold):
        # Point Failed Threshold. Let's try balancing it.
        oldnbhs = getNeighbours(index,globaldata)
        # Get Neighbour of Neighbours
        newnbhs = []
        for itm in oldnbhs:
            nbhofnbh = getNeighbours(getIndexOf(itm,hashtable),globaldata)
            # Removes original point and its neighbours. We only want new neighbours
            newnbhs = newnbhs + list(set(nbhofnbh) - set([getPoint(index,globaldata)]) - set(oldnbhs) - set(newnbhs))
        # We got a new list of points to be tested against lets find the points.
        _,_,_,_,newdxpospoints = deltaNeighbourCalculation(newnbhs,getPoint(index,globaldata),True,True)
        if(len(newdxpospoints)==0):
            writeLog(["We tried finding neighbour of neighbours but none satisfy the delta xneg condition for",getPoint(index,globaldata)])
        else:
            finalList = []
            nothresList = []
            for newitm in newdxpospoints:
                if(not isNonAeroDynamic(index,newitm,globaldata,wallpoints)):
                    tempnbh = []
                    tempnbh = dSPoints
                    tempnbh = tempnbh + [newitm]
                    conditionVal = conditionValueForSetOfPoints(index,globaldata,tempnbh)
                    nothresList.append([newitm,conditionVal])
                    if(conditionVal < threshold):
                        finalList.append([newitm,conditionVal])
                else:
                    writeLog(["Found non aero point skipping."])
            if(len(finalList) == 0 or finalList is None):
                writeLog(["We tried finding points to reduce threshold value to",threshold,"but couldn't find any for index",index])
                writeLog(["It's condition value for dx neg is",initialConditionValue])
                nothresList.sort(key=lambda x: x[1])
                if(len(nothresList) != 0):
                    writeLog(["The least we can reduce it to is",nothresList[0][1]])
                    if(float(nothresList[0][1]) < initialConditionValue):
                        pointToBeAdded = nothresList[0][0]
                        appendNeighbours([pointToBeAdded],index,globaldata)
                        initialConditionValue = getInteriorConditionValueofXNeg(index,globaldata,hashtable)
                        writeLog(["We will be running again to reduce further"])
                        if(control <= 0):
                            conditionValueFixForXNeg(index,globaldata,hashtable,threshold,wallpoints, control + 1)
                    else:
                        writeLog(["We don't want to worsen the condition value so we are not gonna do anything else"])
                else:
                    writeLog(["We couldn't find a single point to reduce it to."])
            else:
                finalList.sort(key=lambda x: x[1])
                pointToBeAdded = finalList[0][0]
                appendNeighbours([pointToBeAdded],index,globaldata)
                initialConditionValue = getInteriorConditionValueofXNeg(index,globaldata,hashtable)
                # writeLog([index,initialConditionValue)
    
def conditionValueFixForYPos(index,globaldata,hashtable,threshold,wallpoints,control):
    initialConditionValue = getInteriorConditionValueofYPos(index,globaldata,hashtable)
    # writeLog([initialConditionValue)
    dSPoints = getDYPosPoints(index,globaldata,hashtable)
    # writeLog([index,initialConditionValue)
    if(initialConditionValue > threshold):
        # Point Failed Threshold. Let's try balancing it.
        oldnbhs = getNeighbours(index,globaldata)
        # Get Neighbour of Neighbours
        newnbhs = []
        for itm in oldnbhs:
            nbhofnbh = getNeighbours(getIndexOf(itm,hashtable),globaldata)
            # Removes original point and its neighbours. We only want new neighbours
            newnbhs = newnbhs + list(set(nbhofnbh) - set([getPoint(index,globaldata)]) - set(oldnbhs) - set(newnbhs))
        # We got a new list of points to be tested against lets find the points.
        _,_,_,_,newdxpospoints = deltaNeighbourCalculation(newnbhs,getPoint(index,globaldata),False,False)
        if(len(newdxpospoints)==0):
            writeLog(["We tried finding neighbour of neighbours but none satisfy the delta ypos condition for",getPoint(index,globaldata)])
        else:
            finalList = []
            nothresList = []
            for newitm in newdxpospoints:
                if(not isNonAeroDynamic(index,newitm,globaldata,wallpoints)):
                    tempnbh = []
                    tempnbh = dSPoints
                    tempnbh = tempnbh + [newitm]
                    conditionVal = conditionValueForSetOfPoints(index,globaldata,tempnbh)
                    nothresList.append([newitm,conditionVal])
                    if(conditionVal < threshold):
                        finalList.append([newitm,conditionVal])
                else:
                    writeLog(["Found non aero point skipping."])
            if(len(finalList) == 0 or finalList is None):
                writeLog(["We tried finding points to reduce threshold value to",threshold,"but couldn't find any for index",index])
                writeLog(["It's condition value for dy pos is",initialConditionValue])
                nothresList.sort(key=lambda x: x[1])
                if(len(nothresList) != 0):
                    writeLog(["The least we can reduce it to is",nothresList[0][1]])
                    if(float(nothresList[0][1]) < float(initialConditionValue)):
                        pointToBeAdded = nothresList[0][0]
                        appendNeighbours([pointToBeAdded],index,globaldata)
                        initialConditionValue = getInteriorConditionValueofYPos(index,globaldata,hashtable)
                        writeLog(["We will be running again to reduce further"])
                        if(control <= 0):
                            conditionValueFixForYPos(index,globaldata,hashtable,threshold,wallpoints,control+1)
                    else:
                        writeLog(["We don't want to worsen the condition value so we are not gonna do anything else"])
                else:
                    writeLog(["We couldn't find a single point to reduce it to."])
            else:
                finalList.sort(key=lambda x: x[1])
                pointToBeAdded = finalList[0][0]
                appendNeighbours([pointToBeAdded],index,globaldata)
                initialConditionValue = getInteriorConditionValueofYPos(index,globaldata,hashtable)
                # writeLog([index,initialConditionValue)

def conditionValueFixForYNeg(index,globaldata,hashtable,threshold,wallpoints,control):
    initialConditionValue = getInteriorConditionValueofYNeg(index,globaldata,hashtable)
    dSPoints = getDYNegPoints(index,globaldata,hashtable)
    # writeLog([index,initialConditionValue)
    if(initialConditionValue > threshold):
        # Point Failed Threshold. Let's try balancing it.
        oldnbhs = getNeighbours(index,globaldata)
        # Get Neighbour of Neighbours
        newnbhs = []
        for itm in oldnbhs:
            nbhofnbh = getNeighbours(getIndexOf(itm,hashtable),globaldata)
            # Removes original point and its neighbours. We only want new neighbours
            newnbhs = newnbhs + list(set(nbhofnbh) - set([getPoint(index,globaldata)]) - set(oldnbhs) - set(newnbhs))
        # We got a new list of points to be tested against lets find the points.
        _,_,_,_,newdxpospoints = deltaNeighbourCalculation(newnbhs,getPoint(index,globaldata),False,True)
        if(len(newdxpospoints)==0):
            writeLog(["We tried finding neighbour of neighbours but none satisfy the delta yneg condition for",getPoint(index,globaldata)])
        else:
            finalList = []
            nothresList = []
            for newitm in newdxpospoints:
                if(not isNonAeroDynamic(index,newitm,globaldata,wallpoints)):
                    tempnbh = []
                    tempnbh = dSPoints
                    tempnbh = tempnbh + [newitm]
                    conditionVal = conditionValueForSetOfPoints(index,globaldata,tempnbh)
                    nothresList.append([newitm,conditionVal])
                    if(conditionVal < threshold):
                        finalList.append([newitm,conditionVal])
                else:
                    writeLog(["Found non aero point skipping."])
            if(len(finalList) == 0 or finalList is None):
                writeLog(["We tried finding points to reduce threshold value to",threshold,"but couldn't find any for index",index])
                writeLog(["It's condition value for dy neg is",initialConditionValue])
                nothresList.sort(key=lambda x: x[1])
                if(len(nothresList) != 0):
                    writeLog(["The least we can reduce it to is",nothresList[0][1]])
                    if(float(nothresList[0][1]) < initialConditionValue):
                        pointToBeAdded = nothresList[0][0]
                        appendNeighbours([pointToBeAdded],index,globaldata)
                        initialConditionValue = getInteriorConditionValueofYNeg(index,globaldata,hashtable)
                        writeLog(["We will be running again to reduce further"])
                        if(control <= 0):                        
                            conditionValueFixForYNeg(index,globaldata,hashtable,threshold,wallpoints, control + 1)
                    else:
                        writeLog(["We don't want to worsen the condition value so we are not gonna do anything else"])
                else:
                    writeLog(["We couldn't find a single point to reduce it to."])
            else:
                finalList.sort(key=lambda x: x[1])
                pointToBeAdded = finalList[0][0]
                appendNeighbours([pointToBeAdded],index,globaldata)
                initialConditionValue = getInteriorConditionValueofYNeg(index,globaldata,hashtable)
                # writeLog([index,initialConditionValue)

def printPosDeltaConditions(index,globaldata,hashtable,threshold):
    initialConditionValueXPos = getInteriorConditionValueofXPos(index,globaldata,hashtable)
    dSPointXPos = getDXPosPoints(index,globaldata,hashtable)
    initialConditionValueXNeg = getInteriorConditionValueofXNeg(index,globaldata,hashtable)
    dSPointXNeg = getDXNegPoints(index,globaldata,hashtable)
    initialConditionValueYPos = getInteriorConditionValueofYPos(index,globaldata,hashtable)
    dSPointYPos = getDYPosPoints(index,globaldata,hashtable)
    initialConditionValueYNeg = getInteriorConditionValueofYNeg(index,globaldata,hashtable)
    dSPointYNeg = getDYNegPoints(index,globaldata,hashtable)
    # if(len(dSPointXPos) < threshold or len(dSPointXNeg) < threshold or len(dSPointYPos) < threshold or len(dSPointYNeg) > threshold):
    #     print(index,len(dSPointXPos),initialConditionValueXPos,len(dSPointXNeg),initialConditionValueXNeg,len(dSPointYPos),initialConditionValueYPos,len(dSPointYNeg),initialConditionValueYNeg)
    #     writeLog([index,len(dSPointXPos),initialConditionValueXPos,len(dSPointXNeg),initialConditionValueXNeg,len(dSPointYPos),initialConditionValueYPos,len(dSPointYNeg),initialConditionValueYNeg])
    #     printPosDeltaConditions2(index,globaldata,hashtable)
    if(initialConditionValueXNeg > threshold or initialConditionValueXPos > threshold or initialConditionValueYPos > threshold or initialConditionValueYNeg > threshold):
        print(index,len(dSPointXPos),initialConditionValueXPos,len(dSPointXNeg),initialConditionValueXNeg,len(dSPointYPos),initialConditionValueYPos,len(dSPointYNeg),initialConditionValueYNeg)
        writeLog([index,len(dSPointXPos),initialConditionValueXPos,len(dSPointXNeg),initialConditionValueXNeg,len(dSPointYPos),initialConditionValueYPos,len(dSPointYNeg),initialConditionValueYNeg])
        printPosDeltaConditions2(index,globaldata,hashtable)

def printPosDeltaConditions2(index,globaldata,hashtable):
    initialConditionValueXPos = getInteriorConditionValueofXPos2(index,globaldata,hashtable)
    dSPointXPos = getDXPosPoints(index,globaldata,hashtable)
    initialConditionValueXNeg = getInteriorConditionValueofXNeg2(index,globaldata,hashtable)
    dSPointXNeg = getDXNegPoints(index,globaldata,hashtable)
    initialConditionValueYPos = getInteriorConditionValueofYPos2(index,globaldata,hashtable)
    dSPointYPos = getDYPosPoints(index,globaldata,hashtable)
    initialConditionValueYNeg = getInteriorConditionValueofYNeg2(index,globaldata,hashtable)
    dSPointYNeg = getDYNegPoints(index,globaldata,hashtable)
    # print(index,len(dSPointXPos),initialConditionValueXPos,len(dSPointXNeg),initialConditionValueXNeg,len(dSPointYPos),initialConditionValueYPos,len(dSPointYNeg),initialConditionValueYNeg)
    writeLog([index,len(dSPointXPos),initialConditionValueXPos,len(dSPointXNeg),initialConditionValueXNeg,len(dSPointYPos),initialConditionValueYPos,len(dSPointYNeg),initialConditionValueYNeg])


def printPosDeltaPointConditions(index,globaldata,hashtable,threshold):
    initialConditionValueXPos = getInteriorConditionValueofXPos(index,globaldata,hashtable)
    dSPointXPos = getDXPosPoints(index,globaldata,hashtable)
    initialConditionValueXNeg = getInteriorConditionValueofXNeg(index,globaldata,hashtable)
    dSPointXNeg = getDXNegPoints(index,globaldata,hashtable)
    initialConditionValueYPos = getInteriorConditionValueofYPos(index,globaldata,hashtable)
    dSPointYPos = getDYPosPoints(index,globaldata,hashtable)
    initialConditionValueYNeg = getInteriorConditionValueofYNeg(index,globaldata,hashtable)
    dSPointYNeg = getDYNegPoints(index,globaldata,hashtable)
    if(initialConditionValueXPos > threshold or initialConditionValueXNeg > threshold or initialConditionValueYPos > threshold or initialConditionValueYNeg > threshold):
        print(index,len(dSPointXPos),initialConditionValueXPos,len(dSPointXNeg),initialConditionValueXNeg,len(dSPointYPos),initialConditionValueYPos,len(dSPointYNeg),initialConditionValueYNeg)
        writeLog([index,len(dSPointXPos),initialConditionValueXPos,len(dSPointXNeg),initialConditionValueXNeg,len(dSPointYPos),initialConditionValueYPos,len(dSPointYNeg),initialConditionValueYNeg])

def setPosDeltaFlags(index,globaldata,hashtable,threshold):
    initialConditionValueXPos = getInteriorConditionValueofXPos(index,globaldata,hashtable)
    initialConditionValueXNeg = getInteriorConditionValueofXNeg(index,globaldata,hashtable)
    initialConditionValueYPos = getInteriorConditionValueofYPos(index,globaldata,hashtable)
    initialConditionValueYNeg = getInteriorConditionValueofYNeg(index,globaldata,hashtable)
    if(initialConditionValueXPos > threshold or math.isnan(initialConditionValueXPos)):
        globaldata = setFlagValue(index,7,0,globaldata)
        writeLog([index,"Full Stencil Condition Value",conditionValueOfPointFull(index,globaldata)])
    if(initialConditionValueXNeg > threshold or math.isnan(initialConditionValueXNeg)):
        globaldata = setFlagValue(index,8,0,globaldata)
        writeLog([index,"Full Stencil Condition Value",conditionValueOfPointFull(index,globaldata)])
    if(initialConditionValueYPos > threshold or math.isnan(initialConditionValueYPos)):
        globaldata = setFlagValue(index,9,0,globaldata)    
        writeLog([index,"Full Stencil Condition Value",conditionValueOfPointFull(index,globaldata)])
    if(initialConditionValueYNeg > threshold or math.isnan(initialConditionValueYNeg)):
        globaldata = setFlagValue(index,10,0,globaldata)
        writeLog([index,"Full Stencil Condition Value",conditionValueOfPointFull(index,globaldata)])
    return globaldata


def fixPsuedoWallPoints(index,globaldata,hashtable,wallpoints,threshold):
    main_point = getPoint(index,globaldata)
    main_pointx = float(main_point.split(",")[0])
    main_pointy = float(main_point.split(",")[1])
    mainpt = shapely.geometry.Point([main_pointx,main_pointy])
    for wallpointset in wallpoints:
        for idx,_ in enumerate(wallpointset):
            pta = idx
            ptb = idx + 1
            if(idx==len(wallpointset)-1):
                ptb = 0
            ptax = float(wallpointset[pta].split(",")[0])
            ptay = float(wallpointset[pta].split(",")[1])
            ptbx = float(wallpointset[ptb].split(",")[0])
            ptby = float(wallpointset[ptb].split(",")[1])
            ptapt = shapely.geometry.Point([ptax,ptay])
            ptbpt = shapely.geometry.Point([ptbx,ptby])
            wallline = shapely.geometry.LineString([[ptax,ptay],[ptbx,ptby]])
            distance = perpendicularDistance(wallpointset[pta],wallpointset[ptb],main_point)
            # distance = mainpt.distance(wallline)
            if(distance <= threshold):
                writeLog(["Found a psuedo wall point",index])
                dist1 = ptapt.distance(mainpt)
                dist2 = ptbpt.distance(mainpt)
                closestwallpointnbh = pta
                if(dist2>dist1):
                    closestwallpointnbh = ptb
                writeLog(["Closest Wall Point Selected",closestwallpointnbh])
                nbhpt = getPoint(getIndexOf(wallpointset[closestwallpointnbh],hashtable),globaldata)
                for index, individualitem in enumerate(globaldata):
                    globaldata[index] = [nbhpt if x==str(main_point) else x for x in individualitem]
                return globaldata
    return globaldata

def addNearestWallPoints(index,globaldata,hashtable,wallpoints):
    main_point = getPoint(index,globaldata)
    main_pointx = float(main_point.split(",")[0])
    main_pointy = float(main_point.split(",")[1])
    mainpt = shapely.geometry.Point([main_pointx,main_pointy])
    walldist = []
    for wallpointset in wallpoints:
        for idx,_ in enumerate(wallpointset):
            pta = idx
            ptb = idx + 1
            if(idx==len(wallpointset)-1):
                ptb = 0
            distance = perpendicularDistance(wallpointset[pta],wallpointset[ptb],main_point)
            walldist.append([distance,wallpointset[pta],wallpointset[ptb]])
    walldist.sort(key=lambda x: x[0])
    nbh1 = walldist[0][1]
    nbh2 = walldist[0][2]
    appendNeighbours([nbh1,nbh2],index,globaldata)

def calculateAverageWallPointDistance(globaldata,wallpoints):
    alldistances = []
    for wallpointset in wallpoints:
        for idx,_ in enumerate(wallpointset):
            pta = idx
            ptb = idx + 1
            if(idx==len(wallpointset)-1):
                ptb = 0  
            ptax = float(wallpointset[pta].split(",")[0])
            ptay = float(wallpointset[pta].split(",")[1])
            ptbx = float(wallpointset[ptb].split(",")[0])
            ptby = float(wallpointset[ptb].split(",")[1])
            ptapt = shapely.geometry.Point([ptax,ptay])
            ptbpt = shapely.geometry.Point([ptbx,ptby])
            alldistances.append(ptapt.distance(ptbpt))
    return min(float(s) for s in alldistances)



            
            



        
        