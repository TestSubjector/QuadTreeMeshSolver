import numpy as np

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

def convertIndexToPoints(indexarray,globaldata):
    ptlist = []
    for item in indexarray:
        item = int(item)
        ptx,pty = getPoint(item,globaldata)
        ptlist.append((str(ptx) + "," + str(pty)))
    return ptlist

def appendNeighbours(index,globaldata,newpts):
    pt = getIndexFromPoint(newpts,globaldata)
    nbhs = getNeighbours(index,globaldata)
    nbhs = nbhs + [pt]
    nbhs = list(set(nbhs))
    globaldata[int(index)][12:] = nbhs
    globaldata[int(index)][11] = len(nbhs)
    return globaldata

def getIndexFromPoint(pt,globaldata):
    ptx = float(pt.split(",")[0])
    pty = float(pt.split(",")[1])
    for itm in globaldata:
        if(itm[1]==str(ptx) and itm[2]==str(pty)):
            return int(itm[0])

def conditionValueForSetOfPoints(index,globaldata,points):
    index = int(index)
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

def getInteriorConditionValueofXPos(index,globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPointxy(index,globaldata),True,False)
    return conditionValueForSetOfPoints(index,globaldata,mypoints)

def getInteriorConditionValueofXNeg(index,globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPointxy(index,globaldata),True,True)
    return conditionValueForSetOfPoints(index,globaldata,mypoints)

def getInteriorConditionValueofYPos(index,globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPointxy(index,globaldata),False,False)
    return conditionValueForSetOfPoints(index,globaldata,mypoints)

def getInteriorConditionValueofYNeg(index,globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    _,_,_,_,mypoints = deltaNeighbourCalculation(nbhs,getPointxy(index,globaldata),False,True)
    return conditionValueForSetOfPoints(index,globaldata,mypoints)

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

def fixXPos(index,globaldata,pts):
    itmnbh = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    dxpos = getDXPosPoints(index,globaldata)
    if(len(dxpos)<3):
        print("Not enough points adding")
        if(len(pts) == 0):
            print("No points available")
            return globaldata
        else:
            initialval = conditionValueForSetOfPoints(index,globaldata,dxpos)
            conditionSet = []
            for itm in pts:
                checkset = [itm] + dxpos
                checkset = list(set(checkset))
                newcheck = conditionValueForSetOfPoints(index,globaldata,checkset)
                if(newcheck<initialval):
                    conditionSet.append([itm,newcheck])
            if(len(conditionSet)>0):
                conditionSet.sort(key=lambda x: x[1])
                globaldata = appendNeighbours(index,globaldata,conditionSet[0][0])
                pts.remove(conditionSet[0][0])
                fixXPos(index,globaldata,pts)
            else:
                print("No Points Available")
    return globaldata

def fixXNeg(index,globaldata,pts):
    itmnbh = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    dxneg = getDXNegPoints(index,globaldata)
    if(len(dxneg)<3):
        print("Not enough points adding")
        if(len(pts) == 0):
            print("No points available")
            return globaldata
        else:
            initialval = conditionValueForSetOfPoints(index,globaldata,dxneg)
            conditionSet = []
            for itm in pts:
                checkset = [itm] + dxneg
                checkset = list(set(checkset))
                newcheck = conditionValueForSetOfPoints(index,globaldata,checkset)
                if(newcheck<initialval):
                    conditionSet.append([itm,newcheck])
            if(len(conditionSet)>0):
                conditionSet.sort(key=lambda x: x[1])
                globaldata = appendNeighbours(index,globaldata,conditionSet[0][0])
                pts.remove(conditionSet[0][0])
                fixXNeg(index,globaldata,pts)
            else:
                print("No Points Available")
    return globaldata

def fixYPos(index,globaldata,pts):
    itmnbh = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    dypos = getDXPosPoints(index,globaldata)
    if(len(dypos)<3):
        print("Not enough points adding")
        if(len(pts) == 0):
            print("No points available")
            return globaldata
        else:
            initialval = conditionValueForSetOfPoints(index,globaldata,dypos)
            conditionSet = []
            for itm in pts:
                checkset = [itm] + dypos
                checkset = list(set(checkset))
                newcheck = conditionValueForSetOfPoints(index,globaldata,checkset)
                if(newcheck<initialval):
                    conditionSet.append([itm,newcheck])
            if(len(conditionSet)>0):
                conditionSet.sort(key=lambda x: x[1])
                globaldata = appendNeighbours(index,globaldata,conditionSet[0][0])
                pts.remove(conditionSet[0][0])
                fixYPos(index,globaldata,pts)
            else:
                print("No Points Available")
    return globaldata

def fixYNeg(index,globaldata,pts):
    itmnbh = convertIndexToPoints(getNeighbours(index,globaldata),globaldata)
    dyneg = getDYNegPoints(index,globaldata)
    if(len(dyneg)<3):
        print("Not enough points adding")
        if(len(pts) == 0):
            print("No points available")
            return globaldata
        else:
            initialval = conditionValueForSetOfPoints(index,globaldata,dyneg)
            conditionSet = []
            for itm in pts:
                checkset = [itm] + dyneg
                checkset = list(set(checkset))
                newcheck = conditionValueForSetOfPoints(index,globaldata,checkset)
                if(newcheck<initialval):
                    conditionSet.append([itm,newcheck])
            if(len(conditionSet)>0):
                conditionSet.sort(key=lambda x: x[1])
                globaldata = appendNeighbours(index,globaldata,conditionSet[0][0])
                pts.remove(conditionSet[0][0])
                fixYNeg(index,globaldata,pts)
            else:
                print("No Points Available")
    return globaldata

def getPointFlag(index,globaldata):
    index = int(index)
    ptdata = globaldata[index]
    return int(ptdata[5])


def getProblemPoints(globaldata,threshold):
    # dxpos = getDXPosPoints(index,globaldata)
    # dxneg = getDXNegPoints(index,globaldata)
    # dypos = getDYPosPoints(index,globaldata)
    # dyneg = getDYNegPoints(index,globaldata)
    badpts = []
    for idx,itm in enumerate(globaldata):
        # printProgressBar(idx, len(globaldata) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        if(idx!=0):
            if(getPointFlag(idx,globaldata)==1):
                xpos = getInteriorConditionValueofXPos(idx,globaldata)
                xneg = getInteriorConditionValueofXNeg(idx,globaldata)
                ypos = getInteriorConditionValueofYPos(idx,globaldata)
                yneg = getInteriorConditionValueofYNeg(idx,globaldata)
                if(xpos>threshold):
                    badpts.append(idx)
                elif(xneg>threshold):
                    badpts.append(idx)
                elif(ypos>threshold):
                    badpts.append(idx)
                elif(yneg>threshold):
                    badpts.append(idx)
    return badpts

def deletePoints(globaldata,indexarray):
    for itm in indexarray:
        globaldata.pop(itm)
    return globaldata


def nukePoints(globaldata,problempts,threshold):
    # print(problempts)
    for itm in problempts:
        problemptnbhs = getNeighbours(itm,globaldata)
        ptsaffected,globaldata = pointsAffectedFromDeletion(itm,globaldata)
        for ptitm in ptsaffected:
            xpos = getInteriorConditionValueofXPos(ptitm,globaldata)
            xneg = getInteriorConditionValueofXNeg(ptitm,globaldata)
            ypos = getInteriorConditionValueofYPos(ptitm,globaldata)
            yneg = getInteriorConditionValueofYNeg(ptitm,globaldata)
            if(xpos>threshold):
                _,_,_,_,dxposfiltered = deltaNeighbourCalculation(convertIndexToPoints(problemptnbhs,globaldata),getPointxy(ptitm,globaldata),True,False)
                if(len(dxposfiltered) == 0):
                    print("No Point can be added")
                else:
                    globaldata = fixXPos(ptitm,globaldata,dxposfiltered)
            elif(xneg>threshold):
                _,_,_,_,dxnegfiltered = deltaNeighbourCalculation(convertIndexToPoints(problemptnbhs,globaldata),getPointxy(ptitm,globaldata),True,True)
                if(len(dxnegfiltered) == 0):
                    print("No Point can be added")
                else:
                    globaldata = fixXNeg(ptitm,globaldata,dxnegfiltered)
            elif(ypos>threshold):
                _,_,_,_,dyposfiltered = deltaNeighbourCalculation(convertIndexToPoints(problemptnbhs,globaldata),getPointxy(ptitm,globaldata),False,False)
                if(len(dyposfiltered) == 0):
                    print("No Point can be added")
                else:
                    globaldata = fixYPos(ptitm,globaldata,dyposfiltered)
            elif(yneg>threshold):
                _,_,_,_,dynegfiltered = deltaNeighbourCalculation(convertIndexToPoints(problemptnbhs,globaldata),getPointxy(ptitm,globaldata),False,True)
                if(len(dynegfiltered) == 0):
                    print("No Point can be added")
                else:
                    globaldata = fixYNeg(ptitm,globaldata,dynegfiltered)
    return globaldata