from core import *
from progress import printProgressBar
import inspect

def triangleBalance(globaldata,polygonData,wallpoints):
    for idx,itm in enumerate(globaldata):
        printProgressBar(
            idx, len(globaldata) - 1, prefix="Progress:", suffix="Complete", length=50
        )
        if idx > 0:
            flag = int(getFlag(idx,globaldata))
            xposf,xnegf,yposf,ynegf = getFlags(idx,globaldata)
            ## Interior Points
            if flag == 1:
                if xposf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDXPosPointsFromSetRaw(idx,globaldata,nbhs)   
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixXpos(idx,globaldata,nbhs,-1,30,False,polygonData,wallpoints)
                elif xposf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDXPosPointsFromSetRaw(idx,globaldata,nbhs)       
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixXpos(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints)
                if xnegf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDXNegPointsFromSetRaw(idx,globaldata,nbhs)   
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixXneg(idx,globaldata,nbhs,-1,30,False,polygonData,wallpoints)
                elif xnegf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDXNegPointsFromSetRaw(idx,globaldata,nbhs)       
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixXneg(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints)
                if yposf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDYPosPointsFromSetRaw(idx,globaldata,nbhs)   
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixYpos(idx,globaldata,nbhs,-1,30,False,polygonData,wallpoints)
                elif yposf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDYPosPointsFromSetRaw(idx,globaldata,nbhs)       
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixYpos(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints)
                if ynegf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDYNegPointsFromSetRaw(idx,globaldata,nbhs)   
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixYneg(idx,globaldata,nbhs,-1,30,False,polygonData,wallpoints)
                elif ynegf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDYNegPointsFromSetRaw(idx,globaldata,nbhs)       
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixYneg(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints)
            elif flag == 0:
                if xposf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDXPosPointsFromSetRaw(idx,globaldata,nbhs)   
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixXpos(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints)
                elif xposf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDXPosPointsFromSetRaw(idx,globaldata,nbhs)       
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixXpos(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints)
                if xnegf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDXNegPointsFromSetRaw(idx,globaldata,nbhs)   
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixXneg(idx,globaldata,nbhs,-1,30,False,polygonData,wallpoints)
                elif xnegf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDXNegPointsFromSetRaw(idx,globaldata,nbhs)       
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixXneg(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints)
            elif flag == 2:
                if xposf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDXPosPointsFromSetRaw(idx,globaldata,nbhs)   
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixXpos(idx,globaldata,nbhs,-1,30,False,polygonData,wallpoints)
                elif xposf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDXPosPointsFromSetRaw(idx,globaldata,nbhs)       
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixXpos(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints)
                if xnegf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDXNegPointsFromSetRaw(idx,globaldata,nbhs)   
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixXneg(idx,globaldata,nbhs,-1,30,False,polygonData,wallpoints)
                elif xnegf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhs = getDXNegPointsFromSetRaw(idx,globaldata,nbhs)       
                    nbhs = getAeroPointsFromSet(idx,nbhs,globaldata,wallpoints)
                    globaldata = fixXneg(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints)
    return globaldata

def getNeighboursFromTriangle(index,globaldata,polygonData):
    nbhs = []
    for itm in polygonData:
        tri = list(itm.exterior.coords)
        cordx,cordy = getPoint(index,globaldata)
        cord = (float(cordx),float(cordy))
        if cord in tri:
            for itm2 in tri:
                if itm2 != cord:
                    nbhcordx = itm2[0]
                    nbhcordy = itm2[1]
                    nbhs.append(str(nbhcordx) + "," + str(nbhcordy))
    nbhs = list(set(nbhs))
    return nbhs

def fixXpos(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDXPosPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = finalnbhs + mynbhs
            newcheck = weightedConditionValueForSetOfPoints(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixXpos(idx,globaldata,nbhs,control,conditionNumber,False,polygonData,wallpoints)
        else:
            if aggressive == True:
                directnbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                nbhofnbh = []
                for itm in directnbhs:
                    layernbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh))
                control = control - 1
                fixXpos(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints)
            else:
                return globaldata
    return globaldata

def fixXneg(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDXNegPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = finalnbhs + mynbhs
            newcheck = weightedConditionValueForSetOfPoints(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixXneg(idx,globaldata,nbhs,control,conditionNumber,False,polygonData,wallpoints)
        else:
            if aggressive == True:
                directnbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                nbhofnbh = []
                for itm in directnbhs:
                    layernbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh))
                control = control - 1
                fixXneg(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints)
            else:
                return globaldata
    return globaldata
        
def fixYpos(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDYPosPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = finalnbhs + mynbhs
            newcheck = weightedConditionValueForSetOfPoints(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixYpos(idx,globaldata,nbhs,control,conditionNumber,False,polygonData,wallpoints)
        else:
            if aggressive == True:
                directnbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                nbhofnbh = []
                for itm in directnbhs:
                    layernbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh))
                control = control - 1
                fixYpos(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints)
            else:
                return globaldata
    return globaldata

def fixYneg(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDYNegPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = finalnbhs + mynbhs
            newcheck = weightedConditionValueForSetOfPoints(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixYneg(idx,globaldata,nbhs,control,conditionNumber,False,polygonData,wallpoints)
        else:
            if aggressive == True:
                directnbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                nbhofnbh = []
                for itm in directnbhs:
                    layernbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh))
                nbhofnbh = getAeroPointsFromSet(idx,nbhofnbh,globaldata,wallpoints)
                control = control - 1
                fixYneg(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints)
            else:
                return globaldata
    return globaldata