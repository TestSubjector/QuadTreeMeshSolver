from balance import *
from misc import *
from logger import writeLog
import numpy as np

def deltaX(xcord,orgxcord):
    return float(xcord - orgxcord)

def deltaY(ycord,orgycord):
    return float(ycord - orgycord)

def deltaNeighbourCalculation(currentneighbours,currentcord,isxcord,isnegative):
    xpos,xneg,ypos,yneg = 0,0,0,0
    temp = []
    for item in currentneighbours:
        if((deltaX(float(currentcord.split(",")[0]), float(item.split(",")[0]))) <= 0):
            if(isxcord and not isnegative):
                temp.append(item)
            xpos = xpos + 1
        if((deltaX(float(currentcord.split(",")[0]), float(item.split(",")[0]))) >= 0):
            if(isxcord and isnegative):
                temp.append(item)
            xneg = xneg + 1
        if((deltaY(float(currentcord.split(",")[1]), float(item.split(",")[1]))) <= 0):
            if(not isxcord and not isnegative):
                temp.append(item)
            ypos = ypos + 1
        if((deltaY(float(currentcord.split(",")[1]), float(item.split(",")[1]))) >= 0):
            if(not isxcord and isnegative):
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


def conditionValueFixForXPos(index,globaldata,hashtable,threshold):
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
                tempnbh = []
                tempnbh = dSPoints
                tempnbh = tempnbh + [newitm]
                conditionVal = conditionValueForSetOfPoints(index,globaldata,tempnbh)
                nothresList.append([newitm,conditionVal])
                if(conditionVal < threshold):
                    finalList.append([newitm,conditionVal])
            if(len(finalList) == 0 or finalList is None):
                writeLog(["We tried finding points to reduce threshold value to",threshold,"but couldn't find any for index",index])
                writeLog(["It's condition value for dx pos is",initialConditionValue])
                nothresList.sort(key=lambda x: x[1])
                writeLog(["The least we can reduce it to is",nothresList[0][1]])
                if(float(nothresList[0][1]) < initialConditionValue):
                    pointToBeAdded = nothresList[0][0]
                    appendNeighbours([pointToBeAdded],index,globaldata)
                    initialConditionValue = getInteriorConditionValueofXPos(index,globaldata,hashtable)
                    writeLog(["We will be running again to reduce further"])
                    conditionValueFixForXPos(index,globaldata,hashtable,threshold)
                else:
                    writeLog(["We don't want to worsen the condition value so we are not gonna do anything else"])
            else:
                finalList.sort(key=lambda x: x[1])
                pointToBeAdded = finalList[0][0]
                appendNeighbours([pointToBeAdded],index,globaldata)
                initialConditionValue = getInteriorConditionValueofXPos(index,globaldata,hashtable)
                # writeLog([index,initialConditionValue)

def conditionValueFixForXNeg(index,globaldata,hashtable,threshold):
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
                tempnbh = []
                tempnbh = dSPoints
                tempnbh = tempnbh + [newitm]
                conditionVal = conditionValueForSetOfPoints(index,globaldata,tempnbh)
                nothresList.append([newitm,conditionVal])
                if(conditionVal < threshold):
                    finalList.append([newitm,conditionVal])
            if(len(finalList) == 0 or finalList is None):
                writeLog(["We tried finding points to reduce threshold value to",threshold,"but couldn't find any for index",index])
                writeLog(["It's condition value for dx neg is",initialConditionValue])
                nothresList.sort(key=lambda x: x[1])
                writeLog(["The least we can reduce it to is",nothresList[0][1]])
                if(float(nothresList[0][1]) < initialConditionValue):
                    pointToBeAdded = nothresList[0][0]
                    appendNeighbours([pointToBeAdded],index,globaldata)
                    initialConditionValue = getInteriorConditionValueofXNeg(index,globaldata,hashtable)
                    writeLog(["We will be running again to reduce further"])
                    conditionValueFixForXNeg(index,globaldata,hashtable,threshold)
                else:
                    writeLog(["We don't want to worsen the condition value so we are not gonna do anything else"])
            else:
                finalList.sort(key=lambda x: x[1])
                pointToBeAdded = finalList[0][0]
                appendNeighbours([pointToBeAdded],index,globaldata)
                initialConditionValue = getInteriorConditionValueofXNeg(index,globaldata,hashtable)
                # writeLog([index,initialConditionValue)
    
def conditionValueFixForYPos(index,globaldata,hashtable,threshold):
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
                tempnbh = []
                tempnbh = dSPoints
                tempnbh = tempnbh + [newitm]
                conditionVal = conditionValueForSetOfPoints(index,globaldata,tempnbh)
                nothresList.append([newitm,conditionVal])
                if(conditionVal < threshold):
                    finalList.append([newitm,conditionVal])
            if(len(finalList) == 0 or finalList is None):
                writeLog(["We tried finding points to reduce threshold value to",threshold,"but couldn't find any for index",index])
                writeLog(["It's condition value for dy pos is",initialConditionValue])
                nothresList.sort(key=lambda x: x[1])
                writeLog(["The least we can reduce it to is",nothresList[0][1]])
                if(float(nothresList[0][1]) < initialConditionValue):
                    pointToBeAdded = nothresList[0][0]
                    appendNeighbours([pointToBeAdded],index,globaldata)
                    initialConditionValue = getInteriorConditionValueofYPos(index,globaldata,hashtable)
                    writeLog(["We will be running again to reduce further"])
                    conditionValueFixForYPos(index,globaldata,hashtable,threshold)
                else:
                    writeLog(["We don't want to worsen the condition value so we are not gonna do anything else"])
            else:
                finalList.sort(key=lambda x: x[1])
                pointToBeAdded = finalList[0][0]
                appendNeighbours([pointToBeAdded],index,globaldata)
                initialConditionValue = getInteriorConditionValueofYPos(index,globaldata,hashtable)
                # writeLog([index,initialConditionValue)

def conditionValueFixForYNeg(index,globaldata,hashtable,threshold):
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
                tempnbh = []
                tempnbh = dSPoints
                tempnbh = tempnbh + [newitm]
                conditionVal = conditionValueForSetOfPoints(index,globaldata,tempnbh)
                nothresList.append([newitm,conditionVal])
                if(conditionVal < threshold):
                    finalList.append([newitm,conditionVal])
            if(len(finalList) == 0 or finalList is None):
                writeLog(["We tried finding points to reduce threshold value to",threshold,"but couldn't find any for index",index])
                writeLog(["It's condition value for dy neg is",initialConditionValue])
                nothresList.sort(key=lambda x: x[1])
                writeLog(["The least we can reduce it to is",nothresList[0][1]])
                if(float(nothresList[0][1]) < initialConditionValue):
                    pointToBeAdded = nothresList[0][0]
                    appendNeighbours([pointToBeAdded],index,globaldata)
                    initialConditionValue = getInteriorConditionValueofYNeg(index,globaldata,hashtable)
                    writeLog(["We will be running again to reduce further"])
                    conditionValueFixForYNeg(index,globaldata,hashtable,threshold)
                else:
                    writeLog(["We don't want to worsen the condition value so we are not gonna do anything else"])
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
    if(initialConditionValueXNeg > threshold or initialConditionValueXPos > threshold or initialConditionValueYPos > threshold or initialConditionValueYNeg > threshold):
        print(index,len(dSPointXPos),initialConditionValueXPos,len(dSPointXNeg),initialConditionValueXNeg,len(dSPointYPos),initialConditionValueYPos,len(dSPointYNeg),initialConditionValueYNeg)

def setPosDeltaFlags(index,globaldata,hashtable,threshold):
    initialConditionValueXPos = getInteriorConditionValueofXPos(index,globaldata,hashtable)
    dSPointXPos = getDXPosPoints(index,globaldata,hashtable)
    initialConditionValueXNeg = getInteriorConditionValueofXNeg(index,globaldata,hashtable)
    dSPointXNeg = getDXNegPoints(index,globaldata,hashtable)
    initialConditionValueYPos = getInteriorConditionValueofYPos(index,globaldata,hashtable)
    dSPointYPos = getDYPosPoints(index,globaldata,hashtable)
    initialConditionValueYNeg = getInteriorConditionValueofYNeg(index,globaldata,hashtable)
    dSPointYNeg = getDYNegPoints(index,globaldata,hashtable)
    if(initialConditionValueXPos > threshold):
        globaldata = setFlagValue(index,7,1,globaldata)
    if(initialConditionValueXNeg > threshold):
        globaldata = setFlagValue(index,8,1,globaldata)
    if(initialConditionValueYPos > threshold):
        globaldata = setFlagValue(index,9,1,globaldata)    
    if(initialConditionValueYNeg > threshold):
        globaldata = setFlagValue(index,10,1,globaldata)
    return globaldata
        
        