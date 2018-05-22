from progress import *
import math

def cleanNeighbours(globaldata):
    print("Beginning Duplicate Neighbour Detection")
    for i in range(len(globaldata)):
        printProgressBar(i, len(globaldata) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        noneighours = int(globaldata[i][7])
        cordneighbours = globaldata[i][-noneighours:]
        cordneighbours = [str(float(i.split(",")[0])) + "," + str(float(i.split(",")[1])) for i in cordneighbours]
        cordneighbours = dict.fromkeys(cordneighbours).keys()
        noneighours = len(cordneighbours)
        globaldata[i] = globaldata[i][:7] + [noneighours] + list(cordneighbours)
    print("Duplicate Neighbours Removed")
    return globaldata

def getNeighbours(indexval,list):
    val = []
    pointdata = list[indexval]
    numbneigh = int(pointdata[7])
    try:
        for i in range(numbneigh):
            val = val + [str(pointdata[i+8])]
    except Exception:
        pass
    return val

def getFlag(indexval,list):
    return list[indexval][5]

def updateLeft(indexval,list,leftpoint):
    list[indexval][3] = leftpoint
    return list

def updateRight(indexval,list,rightpoint):
    list[indexval][4] = rightpoint
    return list

def updateFlag(indexval,list,newflag):
    list[indexval][5] = newflag
    return list

def getYCordNeighbours(list):
    stuff = []
    for item in list:
        stuff.append(float(item.split(",")[1]))
    return stuff

def getXCordNeighbours(list):
    stuff = []
    for item in list:
        stuff.append(float(item.split(",")[0]))
    return stuff

def isPositive(val):
    if(float(val)>=0): return True
    else: return False

def getBiggestXBiggestY(list):
    newlist = []
    for item in list:
        if(isPositive(float(item.split(",")[0])) == True and isPositive(float(item.split(",")[1])) == True):
            newlist.append(item)
    getBiggestX = max(getXCordNeighbours(newlist))
    templist = []
    for item in newlist:
        if(float((item.split(",")[0]))==getBiggestX):
            templist.append(item)
    getBiggestY = max(getYCordNeighbours(templist))
    return str(getBiggestX) + "," + str(getBiggestY)    

def getSmallestXBiggestY(list):
    newlist = []
    for item in list:
        if(isPositive(float(item.split(",")[0])) == False and isPositive(float(item.split(",")[1])) == True):
            newlist.append(item)
    getSmallestX = min(getXCordNeighbours(newlist))
    templist = []
    for item in newlist:
        if(float((item.split(",")[0]))==getSmallestX):
            templist.append(item)
    getBiggestY = max(getYCordNeighbours(templist))
    return str(getSmallestX) + "," + str(getBiggestY)

def getBiggestXSmallestY(list):
    newlist = []
    for item in list:
        if(isPositive(float(item.split(",")[0])) == True and isPositive(float(item.split(",")[1])) == False):
            newlist.append(item)
    getBiggestX = max(getXCordNeighbours(newlist))
    templist = []
    for item in newlist:
        if(float((item.split(",")[0]))==getBiggestX):
            templist.append(item)
    getSmallestY = min(getYCordNeighbours(templist))
    return str(getBiggestX) + "," + str(getSmallestY)

def getSmallestXSmallestY(list):
    newlist = []
    for item in list:
        if(isPositive(float(item.split(",")[0])) == False and isPositive(float(item.split(",")[1])) == False):
            newlist.append(item)
    getBiggestX = min(getXCordNeighbours(newlist))
    templist = []
    for item in newlist:
        if(float((item.split(",")[0]))==getBiggestX):
            templist.append(item)
    getSmallestY = min(getYCordNeighbours(templist))
    return str(getBiggestX) + "," + str(getSmallestY)

def getNeighboursDirectional(direction,maincord,list):
    finallist = []
    xcord = float(maincord.split(",")[0])
    ycord = float(maincord.split(",")[1])
    if(direction==1):
        ## All points towards left of X
        finallist = [x for x in list if float(x.split(",")[0]) <= xcord]
    elif(direction==2):
        ## All points towards bottom of Y
        finallist = [x for x in list if float(x.split(",")[1]) <= ycord]
    elif(direction==3):
        ## All points towards right of X
        finallist = [x for x in list if float(x.split(",")[0]) >= xcord]
    elif(direction==4):
        ## All points towar s top of Y
        finallist = [x for x in list if float(x.split(",")[1]) >= ycord]
    return finallist

def getLeftPoint(cord,globaldata,hashtable):
    val = hashtable.index(cord)
    leftpt = globaldata[val - 1][3]
    if(isinstance(leftpt,int)):
        return hashtable[leftpt]
    else:
        return hashtable.index(leftpt)

def getRightPoint(cord,globaldata,hashtable):
    val = hashtable.index(cord)
    rightpt = globaldata[val - 1][4]
    if(isinstance(rightpt,int)):
        return hashtable[rightpt]
    else:
        return hashtable.index(rightpt)

def takeFirst(elem):
    return elem[0]

def euclideanDistance(a,b):
    ax = float(a.split(",")[0])
    ay = float(a.split(",")[1])
    bx = float(b.split(",")[0])
    by = float(b.split(",")[1])
    return (float(math.sqrt(((bx-ax)**2)+((by-ay)**2))),a)

def appendNeighbours(neighbours,index,globaldata):
    nbhcount = int(globaldata[index][7])
    nbhs = globaldata[index][-nbhcount:]
    nbhs = nbhs + neighbours
    nbhcount = nbhcount + len(neighbours)
    globaldata[index][7] = nbhcount
    globaldata[index] = globaldata[index][:8] + nbhs
    return "Done"

def cleanWallPoints(neighbours,wallpoint):
    return list(set(neighbours) - set(wallpoint))

def generateReplacement(hashtable,globaldata):
    print("Beginning Replacement")
    for index2,item in enumerate(hashtable):
        printProgressBar(index2, len(hashtable) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        for index, individualitem in enumerate(globaldata):
            globaldata[index] = [hashtable.index(x) if x==str(item) else x for x in individualitem]
    print("Replacement Done")
    return globaldata
