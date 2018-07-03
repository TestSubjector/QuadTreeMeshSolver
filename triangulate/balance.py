from core import *
from progress import printProgressBar
import inspect
import collections
from config import getConfig

def triangleBalance(globaldata,polygonData,wallpoints):
    for idx,_ in enumerate(globaldata):
        printProgressBar(
            idx, len(globaldata) - 1, prefix="Progress:", suffix="Complete", length=50
        )
        if idx > 0:
            flag = int(getFlag(idx,globaldata))
            xposf,xnegf,yposf,ynegf = getFlags(idx,globaldata)
            WALL_OUTER_THRESHOLD = int(getConfig()["triangulate"]["wallandOuterThreshold"])
            INTERIOR_THRESHOLD = int(getConfig()["triangulate"]["interiorThreshold"])
            AGGRESSIVE_MAX_NEIGHBOURS = -int(getConfig()["triangulate"]["aggressiveMaxNeighbours"])
            NORMAL_MAX_NEIGHBOURS = -int(getConfig()["triangulate"]["normalMaxNeighbours"])
            ## Interior Points
            if flag == 1:
                if xposf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXpos(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,False,polygonData,wallpoints)
                elif xposf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXpos(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,True,polygonData,wallpoints)
                if xnegf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXneg(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,False,polygonData,wallpoints)
                elif xnegf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXneg(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,True,polygonData,wallpoints)
                if yposf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixYpos(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,False,polygonData,wallpoints)
                elif yposf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixYpos(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,True,polygonData,wallpoints)
                if ynegf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixYneg(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,False,polygonData,wallpoints)
                elif ynegf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixYneg(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,True,polygonData,wallpoints)
            # Wall Points
            elif flag == 0:
                if xposf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXpos(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints)
                elif xposf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXpos(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints)
                if xnegf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXneg(idx,globaldata,nbhs,-1,30,False,polygonData,wallpoints)
                elif xnegf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXneg(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints)
            elif flag == 2:
                if xposf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData) 
                    globaldata = fixXpos(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,WALL_OUTER_THRESHOLD,False,polygonData,wallpoints)
                elif xposf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)    
                    globaldata = fixXpos(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,WALL_OUTER_THRESHOLD,True,polygonData,wallpoints)
                if xnegf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXneg(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,WALL_OUTER_THRESHOLD,False,polygonData,wallpoints)
                elif xnegf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData) 
                    globaldata = fixXneg(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,WALL_OUTER_THRESHOLD,True,polygonData,wallpoints)
    return globaldata

def triangleBalance2(globaldata,polygonData,wallpoints):
    for idx,_ in enumerate(globaldata):
        printProgressBar(
            idx, len(globaldata) - 1, prefix="Progress:", suffix="Complete", length=50
        )
        if idx > 0:
            flag = int(getFlag(idx,globaldata))
            xposf,xnegf,yposf,ynegf = getFlags(idx,globaldata)
            ## Wall Points
            if flag == 0:
                if xposf == 1 or xposf == 2:
                    nbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
                    nbhs = nbhs + getLeftandRightPoint(idx, globaldata)
                    nbhs = list(set(nbhs))
                    globaldata = fixWXpos2(idx,globaldata,nbhs,-2,100,True,polygonData,wallpoints)
                if xnegf == 1 or xnegf == 2:
                    nbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
                    nbhs = nbhs + getLeftandRightPoint(idx, globaldata)
                    nbhs = list(set(nbhs))
                    globaldata = fixWXneg2(idx,globaldata,nbhs,-2,100,True,polygonData,wallpoints)
    return globaldata

def triangleBalance3(globaldata,polygonData,wallpoints):
    for idx,_ in enumerate(globaldata):
        printProgressBar(
            idx, len(globaldata) - 1, prefix="Progress:", suffix="Complete", length=50
        )
        if idx > 0:
            flag = int(getFlag(idx,globaldata))
            xposf,xnegf,yposf,ynegf = getFlags(idx,globaldata)
            ## Wall Points
            if flag == 0:
                if xposf == 1 or xposf == 2:
                    nbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
                    nbhs = nbhs + getLeftandRightPoint(idx, globaldata)
                    nbhs = list(set(nbhs))
                    globaldata = fixWXpos3(idx,globaldata,nbhs,-2,100,True,polygonData,wallpoints)
                if xnegf == 1 or xnegf == 2:
                    nbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
                    nbhs = nbhs + getLeftandRightPoint(idx, globaldata)
                    nbhs = list(set(nbhs))
                    globaldata = fixWXneg3(idx,globaldata,nbhs,-2,100,True,polygonData,wallpoints)
    return globaldata

def convertTupleToCord(tupledata):
    data = []
    for itm in tupledata:
        data.append(str(itm[0]) + "," + str(itm[1]))
    return data

def getNeighboursFromTriangle(index,globaldata,polygonData):
    cordx,cordy = getPoint(index,globaldata)
    return convertTupleToCord(polygonData[(float(cordx),float(cordy))])

def getPolygon(polygonData):
    polygon = collections.defaultdict(set)
    polygon['key'].add('mykey')
    for itm in polygonData:
        tri = set(itm.exterior.coords)
        for itm in tri.copy():
            temptri = tri
            temptri.remove(itm)
            polygon[itm] = polygon[itm].union(temptri)
    return polygon

def fixXpos(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = getDXPosPointsFromSetRaw(idx,globaldata,mynbhs)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDXPosPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = weightedConditionValueForSetOfPoints(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                if not isNonAeroDynamic(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixXpos(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints)
        else:
            if aggressive == True:
                directnbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                nbhofnbh = []
                for itm in directnbhs:
                    itm_real = getIndexFromPoint(itm, globaldata)
                    layernbhs = getNeighboursFromTriangle(itm_real,globaldata,polygonData)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh))
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
        mychecknbhs = getDXNegPointsFromSetRaw(idx,globaldata,mynbhs)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDXNegPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = weightedConditionValueForSetOfPoints(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                if not isNonAeroDynamic(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixXneg(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints)
        else:
            if aggressive == True:
                directnbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                nbhofnbh = []
                for itm in directnbhs:
                    itm_real = getIndexFromPoint(itm, globaldata)
                    layernbhs = getNeighboursFromTriangle(itm_real,globaldata,polygonData)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh))
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
        mychecknbhs = getDYPosPointsFromSetRaw(idx,globaldata,mynbhs)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDYPosPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = weightedConditionValueForSetOfPoints(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                if not isNonAeroDynamic(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixYpos(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints)
        else:
            if aggressive == True:
                directnbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                nbhofnbh = []
                for itm in directnbhs:
                    itm_real = getIndexFromPoint(itm, globaldata)
                    layernbhs = getNeighboursFromTriangle(itm_real,globaldata,polygonData)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh))
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
        mychecknbhs = getDYNegPointsFromSetRaw(idx,globaldata,mynbhs)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDYNegPointsFromSetRaw(idx,globaldata,finalnbhs)
        finalnbhs = getAeroPointsFromSet(idx,finalnbhs,globaldata,wallpoints)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = weightedConditionValueForSetOfPoints(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                if not isNonAeroDynamic(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixYneg(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints)
        else:
            if aggressive == True:
                directnbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                nbhofnbh = []
                for itm in directnbhs:
                    itm_real = getIndexFromPoint(itm, globaldata)
                    layernbhs = getNeighboursFromTriangle(itm_real,globaldata,polygonData)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh))
                fixYneg(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints)
            else:
                return globaldata
    return globaldata

def fixWXpos(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = getDWallXPosPointsFromSetRaw(idx,globaldata,mynbhs)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDWallXPosPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = weightedConditionValueForSetOfPointsNormal(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                if not isNonAeroDynamic(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixWXpos(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints)
        else:
            if aggressive == True:
                leftright = getLeftandRightPoint(idx,globaldata)
                nbhofnbh = []
                for itm in leftright:
                    itm_real = getIndexFromPoint(itm, globaldata)
                    layernbhs = convertIndexToPoints(getNeighboursFromTriangle(itm_real,globaldata,polygonData),globaldata)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh) - set([getPointxy(idx,globaldata)]))
                fixWXpos(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints)
            else:
                return globaldata
    return globaldata

def fixWXneg(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = getDWallXNegPointsFromSetRaw(idx,globaldata,mynbhs)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDWallXNegPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = weightedConditionValueForSetOfPointsNormal(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                if not isNonAeroDynamic(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixWXneg(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints)
        else:
            if aggressive == True:
                leftright = getLeftandRightPoint(idx,globaldata)
                nbhofnbh = []
                for itm in leftright:
                    itm_real = getIndexFromPoint(itm, globaldata)
                    layernbhs = convertIndexToPoints(getNeighboursFromTriangle(itm_real,globaldata,polygonData),globaldata)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh) - set([getPointxy(idx,globaldata)]))
                fixWXneg(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints)
            else:
                return globaldata
    return globaldata

def fixWXpos2(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = getDWallXPosPointsFromSetRaw(idx,globaldata,mynbhs)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDWallXPosPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = weightedConditionValueForSetOfPointsNormal(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                if not isNonAeroDynamic(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixWXpos2(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints)
        else:
            if aggressive == True:
                leftright = getLeftandRightPoint(idx,globaldata)
                nbhofnbh = []
                for itm in leftright:
                    itm_real = getIndexFromPoint(itm, globaldata)
                    layernbhs = convertIndexToPoints(getNeighbours(itm_real,globaldata),globaldata)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh) - set([getPointxy(idx,globaldata)]))
                fixWXpos2(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints)
            else:
                return globaldata
    return globaldata

def fixWXneg2(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = getDWallXNegPointsFromSetRaw(idx,globaldata,mynbhs)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDWallXNegPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = weightedConditionValueForSetOfPointsNormal(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                if not isNonAeroDynamic(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixWXneg2(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints)
        else:
            if aggressive == True:
                leftright = getLeftandRightPoint(idx,globaldata)
                nbhofnbh = []
                for itm in leftright:
                    itm_real = getIndexFromPoint(itm, globaldata)
                    layernbhs = convertIndexToPoints(getNeighbours(itm_real,globaldata),globaldata)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh) - set([getPointxy(idx,globaldata)]))
                fixWXneg2(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints)
            else:
                return globaldata
    return globaldata

def fixWXpos3(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = getDWallXPosPointsFromSetRaw(idx,globaldata,mynbhs)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDWallXPosPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = weightedConditionValueForSetOfPointsNormal(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                if not isNonAeroDynamic(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixWXpos3(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints)
        else:
            if aggressive == True:
                leftright = getLeftandRightPoint(idx,globaldata)
                currnbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
                nbhofnbh = []
                leftright = leftright + currnbhs
                for itm in leftright:
                    itm_real = getIndexFromPoint(itm, globaldata)
                    layernbhs = convertIndexToPoints(getNeighbours(itm_real,globaldata),globaldata)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh) - set([getPointxy(idx,globaldata)]))
                fixWXpos3(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints)
            else:
                return globaldata
    return globaldata

def fixWXneg3(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = getDWallXNegPointsFromSetRaw(idx,globaldata,mynbhs)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = getDWallXNegPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = weightedConditionValueForSetOfPointsNormal(idx,globaldata,checkset)
            if newcheck < conditionNumber:
                if not isNonAeroDynamic(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixWXneg3(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints)
        else:
            if aggressive == True:
                leftright = getLeftandRightPoint(idx,globaldata)
                currnbhs = convertIndexToPoints(getNeighbours(idx,globaldata),globaldata)
                nbhofnbh = []
                leftright = leftright + currnbhs
                for itm in leftright:
                    itm_real = getIndexFromPoint(itm, globaldata)
                    layernbhs = convertIndexToPoints(getNeighbours(itm_real,globaldata),globaldata)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh) - set([getPointxy(idx,globaldata)]))
                fixWXneg3(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints)
            else:
                return globaldata
    return globaldata