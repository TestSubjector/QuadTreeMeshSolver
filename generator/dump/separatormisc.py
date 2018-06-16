import numpy as np
import math


def getNeighbours(index, globaldata):
    index = int(index)
    ptdata = globaldata[index]
    ptdata = ptdata[12:]
    return ptdata


def getPoint(index, globaldata):
    index = int(index)
    ptdata = globaldata[index]
    ptx = float(ptdata[1])
    pty = float(ptdata[2])
    return ptx, pty


def getPointxy(index, globaldata):
    index = int(index)
    ptx, pty = getPoint(index, globaldata)
    return str(ptx) + "," + str(pty)


def pointsAffectedFromDeletion(index, globaldata):
    pts = []
    for itm in globaldata:
        ptindex = itm[0]
        itm = itm[12:]
        if str(index) in itm:
            itm.remove(str(index))
            globaldata[int(ptindex)][12:] = itm
            globaldata[int(ptindex)][11] = len(itm)
            pts.append(ptindex)

    return pts, globaldata


def convertIndexToPoints(indexarray, globaldata):
    ptlist = []
    for item in indexarray:
        item = int(item)
        ptx, pty = getPoint(item, globaldata)
        ptlist.append((str(ptx) + "," + str(pty)))
    return ptlist


def appendNeighbours(index, globaldata, newpts):
    pt = getIndexFromPoint(newpts, globaldata)
    nbhs = getNeighbours(index, globaldata)
    nbhs = nbhs + [pt]
    nbhs = list(set(nbhs))
    globaldata[int(index)][12:] = nbhs
    globaldata[int(index)][11] = len(nbhs)
    return globaldata


def getIndexFromPoint(pt, globaldata):
    ptx = float(pt.split(",")[0])
    pty = float(pt.split(",")[1])
    for itm in globaldata:
        if(itm[1] == str(ptx) and itm[2] == str(pty)):
            return int(itm[0])


def conditionValueForSetOfPoints(index, globaldata, points):
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


def weightedConditionValueForSetOfPoints(index, globaldata, points):
    index = int(index)
    mainptx = float(globaldata[index][1])
    mainpty = float(globaldata[index][2])

    nbhs = points
    shape = (len(nbhs), 2)
    storage = np.zeros(shape)
    count = 0
    for nbhitem in nbhs:
        nbhitemX = float(nbhitem.split(",")[0])
        nbhitemY = float(nbhitem.split(",")[1])
        deltaSumX = nbhitemX - mainptx
        deltaSumY = nbhitemY - mainpty
        d = math.sqrt(deltaSumX**2 + deltaSumY**2)
        power = -2
        if(d != 0):
            w = d ** power
        else:
            w = 0
        storage[count, 0] = w * deltaSumX
        storage[count, 1] = w * deltaSumY
        count = count + 1
    s = np.linalg.svd(storage, full_matrices=False, compute_uv=False)
    if(len(s) == 1):
        s = float("inf")
    else:
        s = max(s) / min(s)
    return s


def deltaX(xcord, orgxcord):
    return float(orgxcord - xcord)


def deltaY(ycord, orgycord):
    return float(orgycord - ycord)


def deltaNeighbourCalculation(
        currentneighbours, currentcord, isxcord, isnegative):
    xpos, xneg, ypos, yneg = 0, 0, 0, 0
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
    return xpos, ypos, xneg, yneg, temp


def getInteriorConditionValueofXPos(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, False)
    return conditionValueForSetOfPoints(index, globaldata, mypoints)


def getInteriorConditionValueofXNeg(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, True)
    return conditionValueForSetOfPoints(index, globaldata, mypoints)


def getInteriorConditionValueofYPos(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, False)
    return conditionValueForSetOfPoints(index, globaldata, mypoints)


def getInteriorConditionValueofYNeg(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, True)
    return conditionValueForSetOfPoints(index, globaldata, mypoints)


def getWeightedInteriorConditionValueofXPos(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, False)
    return weightedConditionValueForSetOfPoints(index, globaldata, mypoints)


def getWeightedInteriorConditionValueofXNeg(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, True)
    return weightedConditionValueForSetOfPoints(index, globaldata, mypoints)


def getWeightedInteriorConditionValueofYPos(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, False)
    return weightedConditionValueForSetOfPoints(index, globaldata, mypoints)


def getWeightedInteriorConditionValueofYNeg(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, True)
    return weightedConditionValueForSetOfPoints(index, globaldata, mypoints)


def getDXPosPoints(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, False)
    return mypoints


def getDXNegPoints(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), True, True)
    return mypoints


def getDYPosPoints(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, False)
    return mypoints


def getDYNegPoints(index, globaldata):
    nbhs = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    _, _, _, _, mypoints = deltaNeighbourCalculation(
        nbhs, getPointxy(index, globaldata), False, True)
    return mypoints


def fixXPos(index, globaldata, pts, flag):
    itmnbh = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    dxpos = getDXPosPoints(index, globaldata)
    if(len(dxpos) < 3):
        # print("Not enough points - adding")
        if(len(pts) == 0):
            # print("No points available")
            return globaldata
        else:
            if(flag == 0):
                initialval = conditionValueForSetOfPoints(
                    index, globaldata, dxpos)
            else:
                initialval = weightedConditionValueForSetOfPoints(
                    index, globaldata, dxpos)
            conditionSet = []
            for itm in pts:
                checkset = [itm] + dxpos
                checkset = list(set(checkset))
                if(flag == 0):
                    newcheck = conditionValueForSetOfPoints(
                        index, globaldata, dxpos)
                else:
                    newcheck = weightedConditionValueForSetOfPoints(
                        index, globaldata, dxpos)
                if(newcheck <= initialval):
                    conditionSet.append([itm, newcheck])
            if(len(conditionSet) > 0):
                # print("Added")
                conditionSet.sort(key=lambda x: x[1])
                globaldata = appendNeighbours(
                    index, globaldata, conditionSet[0][0])
                pts.remove(conditionSet[0][0])
                fixXPos(index, globaldata, pts, flag)
            else:
                None
                # print("No Points Available")
    return globaldata


def fixXNeg(index, globaldata, pts, flag):
    itmnbh = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    dxneg = getDXNegPoints(index, globaldata)
    if(len(dxneg) < 3):
        # print("Not enough points - adding")
        if(len(pts) == 0):
            # print("No points available")
            return globaldata
        else:
            if(flag == 0):
                initialval = conditionValueForSetOfPoints(
                    index, globaldata, dxneg)
            else:
                initialval = weightedConditionValueForSetOfPoints(
                    index, globaldata, dxneg)
            conditionSet = []
            for itm in pts:
                checkset = [itm] + dxneg
                checkset = list(set(checkset))
                if(flag == 0):
                    newcheck = conditionValueForSetOfPoints(
                        index, globaldata, dxneg)
                else:
                    newcheck = weightedConditionValueForSetOfPoints(
                        index, globaldata, dxneg)
                if(newcheck <= initialval):
                    conditionSet.append([itm, newcheck])
            if(len(conditionSet) > 0):
                # print("Added")
                conditionSet.sort(key=lambda x: x[1])
                globaldata = appendNeighbours(
                    index, globaldata, conditionSet[0][0])
                pts.remove(conditionSet[0][0])
                fixXNeg(index, globaldata, pts, flag)
            else:
                None
                # print("No Points Available")
    return globaldata


def fixYPos(index, globaldata, pts, flag):
    itmnbh = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    dypos = getDXPosPoints(index, globaldata)
    if(len(dypos) < 3):
        # print("Not enough points - adding")
        if(len(pts) == 0):
            # print("No points available")
            return globaldata
        else:
            if(flag == 0):
                initialval = conditionValueForSetOfPoints(
                    index, globaldata, dypos)
            else:
                initialval = weightedConditionValueForSetOfPoints(
                    index, globaldata, dypos)
            conditionSet = []
            for itm in pts:
                checkset = [itm] + dypos
                checkset = list(set(checkset))
                if(flag == 0):
                    newcheck = conditionValueForSetOfPoints(
                        index, globaldata, dypos)
                else:
                    newcheck = weightedConditionValueForSetOfPoints(
                        index, globaldata, dypos)
                if(newcheck <= initialval):
                    conditionSet.append([itm, newcheck])
            if(len(conditionSet) > 0):
                # print("Added")
                conditionSet.sort(key=lambda x: x[1])
                globaldata = appendNeighbours(
                    index, globaldata, conditionSet[0][0])
                pts.remove(conditionSet[0][0])
                fixYPos(index, globaldata, pts, flag)
            else:
                None
                # print("No Points Available")
    return globaldata


def fixYNeg(index, globaldata, pts, flag):
    itmnbh = convertIndexToPoints(getNeighbours(index, globaldata), globaldata)
    dyneg = getDYNegPoints(index, globaldata)
    if(len(dyneg) < 3):
        # print("Not enough points - adding")
        if(len(pts) == 0):
            # print("No points available")
            return globaldata
        else:
            if(flag == 0):
                initialval = conditionValueForSetOfPoints(
                    index, globaldata, dyneg)
            else:
                initialval = weightedConditionValueForSetOfPoints(
                    index, globaldata, dyneg)
            conditionSet = []
            for itm in pts:
                checkset = [itm] + dyneg
                checkset = list(set(checkset))
                if(flag == 0):
                    newcheck = conditionValueForSetOfPoints(
                        index, globaldata, dyneg)
                else:
                    newcheck = weightedConditionValueForSetOfPoints(
                        index, globaldata, dyneg)
                if(newcheck <= initialval):
                    conditionSet.append([itm, newcheck])
            if(len(conditionSet) > 0):
                # print("Added")
                conditionSet.sort(key=lambda x: x[1])
                globaldata = appendNeighbours(
                    index, globaldata, conditionSet[0][0])
                pts.remove(conditionSet[0][0])
                fixYNeg(index, globaldata, pts, flag)
            else:
                None
                # print("No Points Available")
    return globaldata


def getPointFlag(index, globaldata):
    index = int(index)
    ptdata = globaldata[index]
    return int(ptdata[5])


def getProblemPoints(globaldata, threshold, flag):
    # dxpos = getDXPosPoints(index,globaldata)
    # dxneg = getDXNegPoints(index,globaldata)
    # dypos = getDYPosPoints(index,globaldata)
    # dyneg = getDYNegPoints(index,globaldata)
    badpts = []
    for idx, itm in enumerate(globaldata):
        # printProgressBar(idx, len(globaldata) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        if(idx != 0):
            if(getPointFlag(idx, globaldata) == 1):
                if(flag == 0):
                    xpos = getInteriorConditionValueofXPos(idx, globaldata)
                    xneg = getInteriorConditionValueofXNeg(idx, globaldata)
                    ypos = getInteriorConditionValueofYPos(idx, globaldata)
                    yneg = getInteriorConditionValueofYNeg(idx, globaldata)
                else:
                    xpos = getWeightedInteriorConditionValueofXPos(
                        idx, globaldata)
                    xneg = getWeightedInteriorConditionValueofXNeg(
                        idx, globaldata)
                    ypos = getWeightedInteriorConditionValueofYPos(
                        idx, globaldata)
                    yneg = getWeightedInteriorConditionValueofYNeg(
                        idx, globaldata)
                if(xpos > threshold):
                    badpts.append(idx)
                elif(xneg > threshold):
                    badpts.append(idx)
                elif(ypos > threshold):
                    badpts.append(idx)
                elif(yneg > threshold):
                    badpts.append(idx)
    return badpts


def deletePoints(globaldata, indexarray):
    count = 0
    for itm in indexarray:
        # print(globaldata[itm + count][0])
        globaldata.pop(itm + count)
        count = count - 1
    return globaldata


def nukePoints(globaldata, problempts, threshold, flag):
    # print(problempts)
    for itm in problempts:
        # print("ABC")
        # print(itm)
        problemptnbhs = getNeighbours(itm, globaldata)
        # print(problemptnbhs)
        ptsaffected, globaldata = pointsAffectedFromDeletion(
            itm, globaldata)  # Points that has this point as neighbour
        for ptitm in ptsaffected:
            if(flag == 0):
                xpos = getInteriorConditionValueofXPos(ptitm, globaldata)
                xneg = getInteriorConditionValueofXNeg(ptitm, globaldata)
                ypos = getInteriorConditionValueofYPos(ptitm, globaldata)
                yneg = getInteriorConditionValueofYNeg(ptitm, globaldata)
            else:
                xpos = getWeightedInteriorConditionValueofXPos(
                    ptitm, globaldata)
                xneg = getWeightedInteriorConditionValueofXNeg(
                    ptitm, globaldata)
                ypos = getWeightedInteriorConditionValueofYPos(
                    ptitm, globaldata)
                yneg = getWeightedInteriorConditionValueofYNeg(
                    ptitm, globaldata)
            dSPointXPos = getDXPosPoints(ptitm, globaldata)
            dSPointXNeg = getDXNegPoints(ptitm, globaldata)
            dSPointYPos = getDYPosPoints(ptitm, globaldata)
            dSPointYNeg = getDYNegPoints(ptitm, globaldata)
            if(int(ptitm) == 177):
                print(ptitm)
                print(itm)
                print(xpos)
                print(ypos)
                print(xneg)
                print(yneg)
                print(problemptnbhs)
            if(xpos > threshold or len(dSPointXPos) <= 1):
                _, _, _, _, dxposfiltered = deltaNeighbourCalculation(convertIndexToPoints(
                    problemptnbhs, globaldata), getPointxy(ptitm, globaldata), True, False)
                if(len(dxposfiltered) == 0):
                    None
                    # print("No Point can be added")
                else:
                    globaldata = fixXPos(
                        ptitm, globaldata, dxposfiltered, flag)
            elif(xneg > threshold or len(dSPointXNeg) <= 1):
                _, _, _, _, dxnegfiltered = deltaNeighbourCalculation(convertIndexToPoints(
                    problemptnbhs, globaldata), getPointxy(ptitm, globaldata), True, True)
                if(len(dxnegfiltered) == 0):
                    None
                    # print("No Point can be added")
                else:
                    globaldata = fixXNeg(
                        ptitm, globaldata, dxnegfiltered, flag)
            elif(ypos > threshold or len(dSPointYPos) <= 1):
                _, _, _, _, dyposfiltered = deltaNeighbourCalculation(convertIndexToPoints(
                    problemptnbhs, globaldata), getPointxy(ptitm, globaldata), False, False)
                if(len(dyposfiltered) == 0):
                    None
                    # print("No Point can be added")
                else:
                    globaldata = fixYPos(
                        ptitm, globaldata, dyposfiltered, flag)
            elif(yneg > threshold or len(dSPointYNeg) <= 1):
                _, _, _, _, dynegfiltered = deltaNeighbourCalculation(convertIndexToPoints(
                    problemptnbhs, globaldata), getPointxy(ptitm, globaldata), False, True)
                if(len(dynegfiltered) == 0):
                    None
                    # print("No Point can be added")
                else:
                    globaldata = fixYNeg(
                        ptitm, globaldata, dynegfiltered, flag)
    cleanNeighbours(globaldata)
    return globaldata


def cleanNeighbours(globaldata):  # Verified
    print("Beginning Duplicate Neighbour Detection")
    for i in range(len(globaldata)):
        # printProgressBar(i, len(globaldata) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        noneighours = int(globaldata[i][11])  # Number of neighbours
        cordneighbours = globaldata[i][-noneighours:]
        print(cordneighbours)
        # TODO - Ask, why get the same thing as above?
        cordneighbours = [str(float(j.split(",")[0])) + "," +
                          str(float(j.split(",")[1])) for j in cordneighbours]

        cordneighbours = dict.fromkeys(cordneighbours).keys()
        noneighours = len(cordneighbours)
        globaldata[i] = globaldata[i][:11] + \
            [noneighours] + list(cordneighbours)
        # with open("duplication_removal.txt", "w") as text_file:
        #     for item1 in globaldata:
        #         text_file.writelines(["%s " % item for item in item1])
        #         text_file.writelines("\n")
    print("Duplicate Neighbours Removed")
    return globaldata
