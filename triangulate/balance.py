import inspect
import collections
from tqdm import tqdm
import sys, os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def triangleBalance(globaldata, polygonData, wallpoints, configData, badPoints):
    for _,idx in enumerate(tqdm(badPoints)):
        if idx > 0:
            flag = int(core.getFlag(idx,globaldata))
            xposf,xnegf,yposf,ynegf = core.getFlags(idx,globaldata)
            WALL_OUTER_THRESHOLD = int(configData["triangulate"]["triangle"]["wallandOuterThreshold"])
            INTERIOR_THRESHOLD = int(configData["triangulate"]["triangle"]["interiorThreshold"])
            AGGRESSIVE_MAX_NEIGHBOURS = -int(configData["triangulate"]["triangle"]["aggressiveMaxNeighbours"])
            NORMAL_MAX_NEIGHBOURS = -int(configData["triangulate"]["triangle"]["normalMaxNeighbours"])
            ## Interior Points
            if flag == 1:
                if xposf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXpos(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,False,polygonData,wallpoints, configData)
                elif xposf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXpos(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,True,polygonData,wallpoints, configData)
                if xnegf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXneg(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,False,polygonData,wallpoints, configData)
                elif xnegf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXneg(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,True,polygonData,wallpoints, configData)
                if yposf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixYpos(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,False,polygonData,wallpoints, configData)
                elif yposf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixYpos(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,True,polygonData,wallpoints, configData)
                if ynegf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixYneg(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,False,polygonData,wallpoints, configData)
                elif ynegf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixYneg(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,INTERIOR_THRESHOLD,True,polygonData,wallpoints, configData)
            # Wall Points
            elif flag == 0:
                if xposf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXpos(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints, configData)
                elif xposf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXpos(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints, configData)
                if xnegf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXneg(idx,globaldata,nbhs,-1,30,False,polygonData,wallpoints, configData)
                elif xnegf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXneg(idx,globaldata,nbhs,-2,30,True,polygonData,wallpoints, configData)
            elif flag == 2:
                if xposf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData) 
                    globaldata = fixXpos(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,WALL_OUTER_THRESHOLD,False,polygonData,wallpoints, configData)
                elif xposf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)    
                    globaldata = fixXpos(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,WALL_OUTER_THRESHOLD,True,polygonData,wallpoints, configData)
                if xnegf == 2:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                    globaldata = fixXneg(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,WALL_OUTER_THRESHOLD,False,polygonData,wallpoints, configData)
                elif xnegf == 1:
                    nbhs = getNeighboursFromTriangle(idx,globaldata,polygonData) 
                    globaldata = fixXneg(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,WALL_OUTER_THRESHOLD,True,polygonData,wallpoints, configData)
    return globaldata

def triangleBalance2(globaldata, wallpoints, configData, badPoints):
    WALL_THRESHOLD = int(configData["triangulate"]["leftright"]["wallThreshold"])
    AGGRESSIVE_MAX_NEIGHBOURS = -int(configData["triangulate"]["leftright"]["aggressiveMaxNeighbours"])
    NORMAL_MAX_NEIGHBOURS = -int(configData["triangulate"]["leftright"]["normalMaxNeighbours"])
    for _,idx in enumerate(tqdm(badPoints)):
        if idx > 0:
            flag = int(core.getFlag(idx,globaldata))
            xposf,xnegf,yposf,ynegf = core.getFlags(idx,globaldata)
            ## Wall Points
            if flag == 0:
                if xposf == 1:
                    nbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
                    if idx not in core.getWallEndPoints(globaldata):
                        nbhs = nbhs + core.getLeftandRightPoint(idx, globaldata)
                    nbhs = list(set(nbhs))
                    globaldata = fixWXpos2(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,WALL_THRESHOLD,True,wallpoints, configData)
                elif xposf == 2:
                    nbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
                    if idx not in core.getWallEndPoints(globaldata):
                        nbhs = nbhs + core.getLeftandRightPoint(idx, globaldata)
                    nbhs = list(set(nbhs))
                    globaldata = fixWXpos2(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,WALL_THRESHOLD,False,wallpoints, configData)
                if xnegf == 1:
                    nbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
                    if idx not in core.getWallEndPoints(globaldata):
                        nbhs = nbhs + core.getLeftandRightPoint(idx, globaldata)
                    nbhs = list(set(nbhs))
                    globaldata = fixWXneg2(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,WALL_THRESHOLD,True,wallpoints, configData)
                elif xnegf == 2:
                    nbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
                    if idx not in core.getWallEndPoints(globaldata):
                        nbhs = nbhs + core.getLeftandRightPoint(idx, globaldata)
                    nbhs = list(set(nbhs))
                    globaldata = fixWXneg2(idx,globaldata,nbhs,NORMAL_MAX_NEIGHBOURS,WALL_THRESHOLD,False,wallpoints, configData)
    return globaldata

def triangleBalance3(globaldata, wallpoints, configData, badPoints):
    WALL_THRESHOLD = int(configData["triangulate"]["leftright"]["wallThreshold"])
    AGGRESSIVE_MAX_NEIGHBOURS = -int(configData["triangulate"]["leftright"]["aggressiveMaxNeighbours"])
    for _,idx in enumerate(tqdm(badPoints)):
        if idx > 0:
            flag = int(core.getFlag(idx,globaldata))
            xposf,xnegf,yposf,ynegf = core.getFlags(idx,globaldata)
            ## Wall Points
            if flag == 0:
                if xposf == 1 or xposf == 2:
                    nbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
                    if idx not in core.getWallEndPoints(globaldata):
                        nbhs = nbhs + core.getLeftandRightPoint(idx, globaldata)
                    nbhs = list(set(nbhs))
                    globaldata = fixWXpos3(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,WALL_THRESHOLD,True,wallpoints, configData)
                if xnegf == 1 or xnegf == 2:
                    nbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
                    if idx not in core.getWallEndPoints(globaldata):
                        nbhs = nbhs + core.getLeftandRightPoint(idx, globaldata)
                    nbhs = list(set(nbhs))
                    globaldata = fixWXneg3(idx,globaldata,nbhs,AGGRESSIVE_MAX_NEIGHBOURS,WALL_THRESHOLD,True,wallpoints, configData)
    return globaldata

def convertTupleToCord(tupledata):
    data = []
    for itm in tupledata:
        data.append(str(itm[0]) + "," + str(itm[1]))
    return data

def getNeighboursFromTriangle(index,globaldata,polygonData):
    cordx,cordy = core.getPoint(index,globaldata)
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

def fixXpos(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints, configData):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = core.getDXPosPointsFromSetRaw(idx,globaldata,mynbhs)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = core.getDXPosPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = core.weightedConditionValueForSetOfPoints(idx,globaldata,checkset, configData)
            if newcheck < conditionNumber:
                if not core.isNonAeroDynamicBetter(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = core.appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixXpos(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints, configData)
        else:
            if aggressive == True:
                directnbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                nbhofnbh = []
                for itm in directnbhs:
                    itm_real = core.getIndexFromPoint(itm, globaldata)
                    layernbhs = getNeighboursFromTriangle(itm_real,globaldata,polygonData)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh))
                fixXpos(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints, configData)
            else:
                return globaldata
    return globaldata

def fixXneg(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints, configData):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = core.getDXNegPointsFromSetRaw(idx,globaldata,mynbhs)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = core.getDXNegPointsFromSetRaw(idx,globaldata,finalnbhs)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = core.weightedConditionValueForSetOfPoints(idx,globaldata,checkset, configData)
            if newcheck < conditionNumber:
                if not core.isNonAeroDynamicBetter(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = core.appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixXneg(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints, configData)
        else:
            if aggressive == True:
                directnbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                nbhofnbh = []
                for itm in directnbhs:
                    itm_real = core.getIndexFromPoint(itm, globaldata)
                    layernbhs = getNeighboursFromTriangle(itm_real,globaldata,polygonData)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh))
                fixXneg(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints, configData)
            else:
                return globaldata
    return globaldata
        
def fixYpos(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints, configData):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = core.getDYPosPointsFromSetRaw(idx,globaldata,mynbhs, configData)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = core.getDYPosPointsFromSetRaw(idx,globaldata,finalnbhs, configData)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = core.weightedConditionValueForSetOfPoints(idx,globaldata,checkset, configData)
            if newcheck < conditionNumber:
                if not core.isNonAeroDynamicBetter(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = core.appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixYpos(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints, configData)
        else:
            if aggressive == True:
                directnbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                nbhofnbh = []
                for itm in directnbhs:
                    itm_real = core.getIndexFromPoint(itm, globaldata)
                    layernbhs = getNeighboursFromTriangle(itm_real,globaldata,polygonData)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh))
                fixYpos(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints, configData)
            else:
                return globaldata
    return globaldata

def fixYneg(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints, configData):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = core.getDYNegPointsFromSetRaw(idx,globaldata,mynbhs, configData)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = core.getDYNegPointsFromSetRaw(idx,globaldata,finalnbhs, configData)
        finalnbhs = core.getAeroPointsFromSet(idx,finalnbhs,globaldata,wallpoints)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = core.weightedConditionValueForSetOfPoints(idx,globaldata,checkset, configData)
            if newcheck < conditionNumber:
                if not core.isNonAeroDynamicBetter(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = core.appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixYneg(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints, configData)
        else:
            if aggressive == True:
                directnbhs = getNeighboursFromTriangle(idx,globaldata,polygonData)
                nbhofnbh = []
                for itm in directnbhs:
                    itm_real = core.getIndexFromPoint(itm, globaldata)
                    layernbhs = getNeighboursFromTriangle(itm_real,globaldata,polygonData)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh))
                fixYneg(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints, configData)
            else:
                return globaldata
    return globaldata

def fixWXpos(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints, configData):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = core.getDWallXPosPointsFromSetRaw(idx,globaldata,mynbhs, configData)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = core.getDWallXPosPointsFromSetRaw(idx,globaldata,finalnbhs, configData)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = core.weightedConditionValueForSetOfPointsNormal(idx,globaldata,checkset, configData)
            if newcheck < conditionNumber:
                if not core.isNonAeroDynamicBetter(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = core.appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixWXpos(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints, configData)
        else:
            if aggressive == True:
                leftright = core.getLeftandRightPoint(idx,globaldata)
                nbhofnbh = []
                for itm in leftright:
                    itm_real = core.getIndexFromPoint(itm, globaldata)
                    layernbhs = core.convertIndexToPoints(getNeighboursFromTriangle(itm_real,globaldata,polygonData),globaldata)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh) - set([core.getPointxy(idx,globaldata)]))
                fixWXpos(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints, configData)
            else:
                return globaldata
    return globaldata

def fixWXneg(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints, configData):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = core.getDWallXNegPointsFromSetRaw(idx,globaldata,mynbhs, configData)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = core.getDWallXNegPointsFromSetRaw(idx,globaldata,finalnbhs, configData)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = core.weightedConditionValueForSetOfPointsNormal(idx,globaldata,checkset, configData)
            if newcheck < conditionNumber:
                if not core.isNonAeroDynamicBetter(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = core.appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixWXneg(idx,globaldata,nbhs,control,conditionNumber,aggressive,polygonData,wallpoints, configData)
        else:
            if aggressive == True:
                leftright = core.getLeftandRightPoint(idx,globaldata)
                nbhofnbh = []
                for itm in leftright:
                    itm_real = core.getIndexFromPoint(itm, globaldata)
                    layernbhs = core.convertIndexToPoints(getNeighboursFromTriangle(itm_real,globaldata,polygonData),globaldata)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh) - set([core.getPointxy(idx,globaldata)]))
                fixWXneg(idx,globaldata,nbhofnbh,control,conditionNumber,False,polygonData,wallpoints, configData)
            else:
                return globaldata
    return globaldata

def fixWXpos2(idx,globaldata,nbhs,control,conditionNumber,aggressive,wallpoints, configData):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = core.getDWallXPosPointsFromSetRaw(idx,globaldata,mynbhs, configData)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = core.getDWallXPosPointsFromSetRaw(idx,globaldata,finalnbhs, configData)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = core.weightedConditionValueForSetOfPointsNormal(idx,globaldata,checkset, configData)
            if newcheck < conditionNumber:
                if not core.isNonAeroDynamicBetter(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = core.appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixWXpos2(idx,globaldata,nbhs,control,conditionNumber,aggressive,wallpoints, configData)
        else:
            if aggressive == True:
                leftright = core.getLeftandRightPoint(idx,globaldata)
                nbhofnbh = []
                for itm in leftright:
                    itm_real = core.getIndexFromPoint(itm, globaldata)
                    layernbhs = core.convertIndexToPoints(core.getNeighbours(itm_real,globaldata),globaldata)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh) - set([core.getPointxy(idx,globaldata)]))
                fixWXpos2(idx,globaldata,nbhofnbh,control,conditionNumber,False,wallpoints, configData)
            else:
                return globaldata
    return globaldata

def fixWXneg2(idx,globaldata,nbhs,control,conditionNumber,aggressive,wallpoints, configData):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = core.getDWallXNegPointsFromSetRaw(idx,globaldata,mynbhs, configData)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = core.getDWallXNegPointsFromSetRaw(idx,globaldata,finalnbhs, configData)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = core.weightedConditionValueForSetOfPointsNormal(idx,globaldata,checkset, configData)
            if newcheck < conditionNumber:
                if not core.isNonAeroDynamicBetter(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = core.appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixWXneg2(idx,globaldata,nbhs,control,conditionNumber,aggressive,wallpoints, configData)
        else:
            if aggressive == True:
                leftright = core.getLeftandRightPoint(idx,globaldata)
                nbhofnbh = []
                for itm in leftright:
                    itm_real = core.getIndexFromPoint(itm, globaldata)
                    layernbhs = core.convertIndexToPoints(core.getNeighbours(itm_real,globaldata),globaldata)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh) - set([core.getPointxy(idx,globaldata)]))
                fixWXneg2(idx,globaldata,nbhofnbh,control,conditionNumber,False,wallpoints, configData)
            else:
                return globaldata
    return globaldata

def fixWXpos3(idx,globaldata,nbhs,control,conditionNumber,aggressive,wallpoints, configData):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = core.getDWallXPosPointsFromSetRaw(idx,globaldata,mynbhs, configData)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = core.getDWallXPosPointsFromSetRaw(idx,globaldata,finalnbhs, configData)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = core.weightedConditionValueForSetOfPointsNormal(idx,globaldata,checkset, configData)
            if newcheck < conditionNumber:
                if not core.isNonAeroDynamicBetter(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = core.appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixWXpos3(idx,globaldata,nbhs,control,conditionNumber,aggressive,wallpoints, configData)
        else:
            if aggressive == True:
                leftright = core.getLeftandRightPoint(idx,globaldata)
                currnbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
                nbhofnbh = []
                leftright = leftright + currnbhs
                for itm in leftright:
                    itm_real = core.getIndexFromPoint(itm, globaldata)
                    layernbhs = core.convertIndexToPoints(core.getNeighbours(itm_real,globaldata),globaldata)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh) - set([core.getPointxy(idx,globaldata)]))
                fixWXpos3(idx,globaldata,nbhofnbh,control,conditionNumber,False,wallpoints, configData)
            else:
                return globaldata
    return globaldata

def fixWXneg3(idx,globaldata,nbhs,control,conditionNumber,aggressive,wallpoints, configData):
    if control > 0:
        return globaldata
    else:
        control = control + 1
        mynbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
        mychecknbhs = core.getDWallXNegPointsFromSetRaw(idx,globaldata,mynbhs, configData)
        finalnbhs = list(set(nbhs) - set(mynbhs))
        finalnbhs = core.getDWallXNegPointsFromSetRaw(idx,globaldata,finalnbhs, configData)
        # print(finalnbhs)
        conditionSet = []
        for itm in finalnbhs:
            checkset = [itm] + mychecknbhs
            newcheck = core.weightedConditionValueForSetOfPointsNormal(idx,globaldata,checkset, configData)
            if newcheck < conditionNumber:
                if not core.isNonAeroDynamicBetter(idx,itm,globaldata,wallpoints):
                    conditionSet.append([itm, newcheck])
        if len(conditionSet) > 0:
            conditionSet.sort(key=lambda x: x[1])
            globaldata = core.appendNeighbours(idx, globaldata, conditionSet[0][0])
            fixWXneg3(idx,globaldata,nbhs,control,conditionNumber,aggressive,wallpoints, configData)
        else:
            if aggressive == True:
                leftright = core.getLeftandRightPoint(idx,globaldata)
                currnbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
                nbhofnbh = []
                leftright = leftright + currnbhs
                for itm in leftright:
                    itm_real = core.getIndexFromPoint(itm, globaldata)
                    layernbhs = core.convertIndexToPoints(core.getNeighbours(itm_real,globaldata),globaldata)
                    nbhofnbh = nbhofnbh + layernbhs
                nbhofnbh = list(set(nbhofnbh) - set([core.getPointxy(idx,globaldata)]))
                fixWXneg3(idx,globaldata,nbhofnbh,control,conditionNumber,False,wallpoints, configData)
            else:
                return globaldata
    return globaldata