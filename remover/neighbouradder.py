from trialfunctions import *

def getIndexFromPoint(pt,globaldata):
    ptx = float(pt.split(",")[0])
    pty = float(pt.split(",")[1])
    for itm in globaldata:
        if(itm[1]==str(ptx) and itm[2]==str(pty)):
            return int(itm[0])

def appendNeighbours(index,globaldata,newpts):
    pt = getIndexFromPoint(newpts,globaldata)
    nbhs = getNeighbours(index,globaldata)
    nbhs = nbhs + [pt]
    nbhs = list(set(nbhs))
    globaldata[int(index)][12:] = nbhs
    globaldata[int(index)][11] = len(nbhs)
    return globaldata

def pointsAffectedFromDeletion(index,globaldata):
    pts = []
    for itm in globaldata:
        ptindex = itm[0]
        itm = itm[12:]
        if str(index) in itm:
            itm.remove(str(index))
            globaldata[int(ptindex)][12:] = itm
            globaldata[int(ptindex)][11] = len(itm)
            pts.append(ptindex)
        
    return pts,globaldata

def fixXPos(index,globaldata,pts,flag):
    dxpos = getDXPosPoints(index,globaldata)
    # if(len(dxpos)<3):
    # print("Not enough points - adding")
    if(len(pts) == 0):
        # print("No points available")
        return globaldata
    else:
        if(flag == 0):
            initialval = weightedConditionValueForSetOfPoints(index,globaldata,dxpos)
        else:
            initialval = weightedConditionValueForSetOfPoints(index,globaldata,dxpos)
        conditionSet = []
        for itm in pts:
            checkset = [itm] + dxpos
            checkset = list(set(checkset))
            if(flag == 0):
                newcheck = weightedConditionValueForSetOfPoints(index,globaldata,dxpos)
            else:
                newcheck = weightedConditionValueForSetOfPoints(index,globaldata,dxpos)
            if(newcheck <= initialval):
                conditionSet.append([itm,newcheck])
        if(len(conditionSet) > 0):
            # print("Added")
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(index,globaldata,conditionSet[0][0])
            pts.remove(conditionSet[0][0])
            fixXPos(index,globaldata,pts, flag)
        else:
            None
            # print("No Points Available")
    return globaldata

def fixXNeg(index,globaldata,pts,flag):
    dxneg = getDXNegPoints(index,globaldata)
    # if(len(dxneg)<3):
    # print("Not enough points - adding")
    # if(int(index) == 1091):
    #     print("Hello2")
    #     print("dxneg is ", dxneg)
    #     print("pts is ", pts)
    if(len(pts) == 0):
        # print("No points available")
        return globaldata
    else:
        initialval = weightedConditionValueForSetOfPoints(index,globaldata,dxneg)
        conditionSet = []
        for itm in pts:
            checkset = [itm] + dxneg
            checkset = list(set(checkset))
            newcheck = weightedConditionValueForSetOfPoints(index,globaldata,dxneg)
            # if(int(index) == 1091):
            #     print(itm)
            #     print(checkset)
            if(newcheck <= initialval):
                conditionSet.append([itm,newcheck])
                # if(int(index) == 1091):
                #     print(itm)
                #     print(checkset)
        if(len(conditionSet)>0):
            # print("Added")
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(index,globaldata,conditionSet[0][0])
            pts.remove(conditionSet[0][0])
            fixXNeg(index,globaldata,pts,flag)
        else:
            None
            # print("No Points Available")
    return globaldata

def fixYPos(index,globaldata,pts,flag):
    dypos = getDXPosPoints(index,globaldata)
    # if(len(dypos)<3):
        # print("Not enough points - adding")
    if(len(pts) == 0):
        # print("No points available")
        return globaldata
    else:
        if(flag == 0):
            initialval = weightedConditionValueForSetOfPoints(index,globaldata,dypos)
        else:
            initialval = weightedConditionValueForSetOfPoints(index,globaldata,dypos)
        conditionSet = []
        for itm in pts:
            checkset = [itm] + dypos
            checkset = list(set(checkset))
            if(flag == 0):
                newcheck = weightedConditionValueForSetOfPoints(index,globaldata,dypos)
            else:
                newcheck = weightedConditionValueForSetOfPoints(index,globaldata,dypos)
            if(newcheck <= initialval):
                conditionSet.append([itm,newcheck])
        if(len(conditionSet)>0):
            # print("Added")
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(index,globaldata,conditionSet[0][0])
            pts.remove(conditionSet[0][0])
            fixYPos(index,globaldata,pts,flag)
        else:
            None
            # print("No Points Available")
    return globaldata

def fixYNeg(index,globaldata,pts, flag):
    dyneg = getDYNegPoints(index,globaldata)
    # if(len(dyneg)<3):
    # print("Not enough points - adding")
    if(len(pts) == 0):
        # print("No points available")
        return globaldata
    else:
        if(flag == 0):
            initialval = weightedConditionValueForSetOfPoints(index,globaldata,dyneg)
        else:
            initialval = weightedConditionValueForSetOfPoints(index,globaldata,dyneg)
        conditionSet = []
        for itm in pts:
            checkset = [itm] + dyneg
            checkset = list(set(checkset))
            if(flag == 0):
                newcheck = weightedConditionValueForSetOfPoints(index,globaldata,dyneg)
            else:
                newcheck = weightedConditionValueForSetOfPoints(index,globaldata,dyneg)
            if(newcheck <= initialval):
                conditionSet.append([itm,newcheck])
        if(len(conditionSet)>0):
            # print("Added")
            conditionSet.sort(key=lambda x: x[1])
            globaldata = appendNeighbours(index,globaldata,conditionSet[0][0])
            pts.remove(conditionSet[0][0])
            fixYNeg(index,globaldata,pts,flag)
        else:
            None
            # print("No Points Available")
    return globaldata

def addNewPoints(globaldata,problempts,threshold,flag):
    # print(problempts)
    for itm in problempts:
        problemptnbhs = getNeighbours(itm,globaldata)
        # print(problemptnbhs)
        ptsaffected,globaldata = pointsAffectedFromDeletion(itm,globaldata) # Points that has this point as neighbour
        for ptitm in ptsaffected:
            xpos = getWeightedInteriorConditionValueofXPos(ptitm,globaldata)
            xneg = getWeightedInteriorConditionValueofXNeg(ptitm,globaldata)
            ypos = getWeightedInteriorConditionValueofYPos(ptitm,globaldata)
            yneg = getWeightedInteriorConditionValueofYNeg(ptitm,globaldata)
            dSPointXPos = getDXPosPoints(ptitm, globaldata)
            dSPointXNeg = getDXNegPoints(ptitm, globaldata)
            dSPointYPos = getDYPosPoints(ptitm, globaldata)
            dSPointYNeg = getDYNegPoints(ptitm, globaldata)
            if(ypos > threshold or len(dSPointYPos) <= 1):
                _,_,_,_,dyposfiltered = deltaNeighbourCalculation(convertIndexToPoints(problemptnbhs,globaldata),getPointxy(ptitm,globaldata),False,False)
                if(len(dyposfiltered) == 0):
                    None
                    # print("No Point can be added")
                else:
                    globaldata = fixYPos(ptitm,globaldata,dyposfiltered,flag)
            if(yneg > threshold or len(dSPointYNeg) <= 1):
                _,_,_,_,dynegfiltered = deltaNeighbourCalculation(convertIndexToPoints(problemptnbhs,globaldata),getPointxy(ptitm,globaldata),False,True)
                if(len(dynegfiltered) == 0):
                    None
                    # print("No Point can be added")
                else:
                    globaldata = fixYNeg(ptitm,globaldata,dynegfiltered,flag)    
            if(xpos > threshold or len(dSPointXPos) <= 1):
                _,_,_,_,dxposfiltered = deltaNeighbourCalculation(convertIndexToPoints(problemptnbhs,globaldata),getPointxy(ptitm,globaldata),True,False)
                if(len(dxposfiltered) == 0):
                    None
                    # print("No Point can be added")
                else:
                    globaldata = fixXPos(ptitm,globaldata,dxposfiltered,flag)
            if(xneg > threshold or len(dSPointXNeg) <= 1):
                _,_,_,_,dxnegfiltered = deltaNeighbourCalculation(convertIndexToPoints(problemptnbhs,globaldata),getPointxy(ptitm,globaldata),True,True)
                # if(int(ptitm) == 1091):
                #     print(getPointxy(itm, globaldata))
                #     print(problemptnbhs)
                #     print(convertIndexToPoints(problemptnbhs,globaldata))
                #     print("Check this ", dxnegfiltered)
                if(len(dxnegfiltered) == 0):
                    None
                    # print("No Point can be added")
                else:
                    # if(int(ptitm) == 1091):
                    #     print("Hello1")
                    globaldata = fixXNeg(ptitm,globaldata,dxnegfiltered,flag)
    return globaldata

def cleanNeighbours(globaldata): # Verified
    print("Beginning Duplicate Neighbour Detection")
    for i in range(len(globaldata)):
        # printProgressBar(i, len(globaldata) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        if(i==0):
            continue
        noneighours = int(globaldata[i][11]) # Number of neighbours
        cordneighbours = globaldata[i][-noneighours:]

        # TODO - Ask, why get the same thing as above?
        result = []
        for item in cordneighbours:
            if(int(item) == i):
                continue
            if str(item) not in result:
                result.append(str(item))
        cordneighbours = result

        noneighours = len(cordneighbours)
        globaldata[i] = globaldata[i][:11] + [noneighours] + list(cordneighbours)
        # with open("duplication_removal.txt", "w") as text_file:
        #     for item1 in globaldata:
        #         text_file.writelines(["%s " % item for item in item1])
        #         text_file.writelines("\n")
    print("Duplicate Neighbours Removed")
    return globaldata
