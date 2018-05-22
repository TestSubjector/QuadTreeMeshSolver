import math
import numpy as np
from numpy import linalg as LA
import argparse

def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    if iteration == total: 
        print()

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
    return xpos,ypos,xneg,xneg,temp

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

def deltaWallNeighbourCalculation(index,currentneighbours,currentcord,nx,ny,giveposdelta,globaldata):
    deltaspos,deltasneg,deltaszero = 0,0,0
    nx = float(nx)
    ny = float(ny)
    tx = float(ny)
    ty = -float(nx)
    xcord = float(currentcord.split(",")[0])
    ycord = float(currentcord.split(",")[1])
    output = []
    for item in currentneighbours:
        itemx = float(item.split(",")[0])
        itemy = float(item.split(",")[1])
        deltas = (tx * (itemx - xcord)) + (ty * (itemy - ycord))
        # if(index==730):
        #     print(deltas)
        if(deltas <= 0):
            if(giveposdelta):
                output.append(item)
            deltaspos = deltaspos + 1
        if(deltas >= 0):
            if(not giveposdelta):
                output.append(item)
            deltasneg = deltasneg + 1
        if(deltas == 0):
            deltaszero = deltaszero + 1
    if(getFlag(index,globaldata)==2):
        None
        # print(index,len(currentneighbours),deltaspos,deltasneg,deltaszero)
    return deltaspos,deltasneg,deltaszero,output

def normalCalculation(index,cord,hashtable,globaldata,wallpoint):
    nx = 0
    ny = 0
    cordx = float(cord.split(",")[0])
    cordy = float(cord.split(",")[1])
    val = hashtable.index(cord)
    pointdata = globaldata[val - 1]
    if(wallpoint):
        leftpoint = hashtable[pointdata[3]]
        rightpoint = hashtable[pointdata[4]]
    else:
        leftpoint = pointdata[3]
        rightpoint = pointdata[4]
    leftpointx = float(leftpoint.split(",")[0])
    leftpointy = float(leftpoint.split(",")[1])
    rightpointx = float(rightpoint.split(",")[0])
    rightpointy = float(rightpoint.split(",")[1])
    nx1 = cordy - leftpointy
    nx2 = rightpointy - cordy
    ny1 = cordx - leftpointx
    ny2 = rightpointx - cordx
    nx = (nx1+nx2)/2
    ny = (ny1+ny2)/2
    det = math.sqrt((nx*nx) + (ny*ny))
    if(not wallpoint):
        nx = -nx/det
    else:
        nx = (-nx)/det
    ny = ny/det
    return nx,ny

def minDistance(neighbours,cord):
    dists = []
    for item in neighbours:
        dists.append(euclideanDistance(item,cord))
    dists.sort(key=takeFirst)
    dists2 = []
    for item in dists:
        dists2.append(item[1])
    return dists2
    
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

def conditionCheck(index,globaldata,cord):
        item = cord
        mainptx = float(item.split(",")[0])
        mainpty = float(item.split(",")[1])
        nbh = getNeighbours(index,globaldata)
        deltaSumX = 0
        deltaSumY = 0
        deltaSumXY = 0
        data = []
        for nbhitem in nbh:
            nbhitemX = float(nbhitem.split(",")[0])
            nbhitemY = float(nbhitem.split(",")[1])
            deltaSumX = deltaSumX + (nbhitemX-mainptx)**2
            deltaSumY = deltaSumY + (nbhitemY-mainpty)**2
            deltaSumXY = deltaSumXY + (nbhitemX-mainptx)*(nbhitemY-mainpty)
        data.append(deltaSumX)
        data.append(deltaSumXY)
        data.append(deltaSumXY)
        data.append(deltaSumY)
        random = np.array(data)
        shape = (2,2)
        random = random.reshape(shape)
        w,v = LA.eig(random)
        w = max(w)/min(w)
        s = np.linalg.svd(random,full_matrices=False,compute_uv=False)
        s = max(s)/min(s)
        return w,s
    
def conditionCheckWithNeighbours(index,globaldata,cord,nbh):
        item = cord
        mainptx = float(item.split(",")[0])
        mainpty = float(item.split(",")[1])
        deltaSumX = 0
        deltaSumY = 0
        deltaSumXY = 0
        data = []
        for nbhitem in nbh:
            nbhitemX = float(nbhitem.split(",")[0])
            nbhitemY = float(nbhitem.split(",")[1])
            deltaSumX = deltaSumX + (nbhitemX-mainptx)**2
            deltaSumY = deltaSumY + (nbhitemY-mainpty)**2
            deltaSumXY = deltaSumXY + (nbhitemX-mainptx)*(nbhitemY-mainpty)
        data.append(deltaSumX)
        data.append(deltaSumXY)
        data.append(deltaSumXY)
        data.append(deltaSumY)
        random = np.array(data)
        shape = (2,2)
        random = random.reshape(shape)
        s = np.linalg.svd(random,full_matrices=False,compute_uv=False)
        s = max(s)/min(s)
        return s

def minConditionValue(index,globaldata,cord,nbhs):
        item = cord
        mainptx = float(item.split(",")[0])
        mainpty = float(item.split(",")[1])
        nbh = getNeighbours(index,globaldata)
        nbh = nbh + nbhs
        deltaSumX = 0
        deltaSumY = 0
        deltaSumXY = 0
        data = []
        for nbhitem in nbh:
            nbhitemX = float(nbhitem.split(",")[0])
            nbhitemY = float(nbhitem.split(",")[1])
            deltaSumX = deltaSumX + (nbhitemX-mainptx)**2
            deltaSumY = deltaSumY + (nbhitemY-mainpty)**2
            deltaSumXY = deltaSumXY + (nbhitemX-mainptx)*(nbhitemY-mainpty)
        data.append(deltaSumX)
        data.append(deltaSumXY)
        data.append(deltaSumXY)
        data.append(deltaSumY)
        random = np.array(data)
        shape = (2,2)
        random = random.reshape(shape)
        w,v = LA.eig(random)
        w = max(w)/min(w)
        return w

def minCondition(index,globaldata,cord,nbs,threshold):
    nbsMin = []
    for index,item in enumerate(nbs):
        w = minConditionValue(index,globaldata,cord,nbs)
        if(w < threshold):
            nbsMin.append([item,index,w])
        nbsMin.sort(key=lambda x: x[2])
        nbsFinalList = []
        for item in nbsMin:
            nbsFinalList.append(item[0])
        return nbsFinalList

def wallBalance(index,globaldata,hashtable,itemda,control,wallpoint):
    # print(index,item,control)
    currentneighbours = getNeighbours(index,globaldata)
    currentcord = itemda
    nx,ny = normalCalculation(index,currentcord,hashtable,globaldata,True)
    deltaspos,deltasneg,deltaszero,temp = deltaWallNeighbourCalculation(index,currentneighbours,currentcord,nx,ny,False,globaldata)
    if(deltaspos < control or deltasneg < control):
        newset = []
        posdiff = deltaspos
        negdiff = deltasneg
        for item in currentneighbours:
            itemnb = getNeighbours(hashtable.index(item) - 1,globaldata)
            newset = newset + itemnb
        # Filter 1
        newset = list(set(newset) - set(currentneighbours))
        newset = list(set(newset) - set([currentcord]))
        if(deltasneg < control):
            _,_,_,temp = deltaWallNeighbourCalculation(index,newset,currentcord,nx,ny,False,globaldata)
            temp = cleanWallPoints(temp,wallpoint)
            # w,_ = conditionCheck(index,globaldata,item)
            # shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
            shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(control-negdiff)],index,globaldata)
        if(deltaspos < control):
            _,_,_,temp = deltaWallNeighbourCalculation(index,newset,currentcord,nx,ny,True,globaldata)
            temp = cleanWallPoints(temp,wallpoint)
            # w,_ = conditionCheck(index,globaldata,item)
            # shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
            shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(control-posdiff)],index,globaldata)
        w,s = conditionCheck(index,globaldata,item)
        if(w >= 3 or s >= 3):
            if(control==6):
                print("Shit Man")
            else:
                # print(index,itemda)
                control = control + 1
                wallBalance(hashtable.index(itemda) - 1,globaldata,hashtable,itemda,control,wallpoint)

def outerBalance(index,globaldata,hashtable,item):
    currentneighbours = getNeighbours(index,globaldata)
    currentcord = item
    nx,ny = normalCalculation(index,currentcord,hashtable,globaldata,False)
    deltaspos,deltasneg,deltaszero,temp = deltaWallNeighbourCalculation(index,currentneighbours,currentcord,nx,ny,False,globaldata)
    # if(item=="8.75,8.75"):
    # print(index,len(currentneighbours),deltaspos,deltasneg,deltaszero,nx,ny,currentneighbours)
    if(deltaspos < 4 or deltasneg < 4):
        newset = []
        posdiff = deltaspos
        negdiff = deltasneg
        for item in currentneighbours:
            itemnb = getNeighbours(hashtable.index(item) - 1,globaldata)
            newset = newset + itemnb
        # Filter 1
        newset = list(set(newset) - set(currentneighbours))
        newset = list(set(newset) - set([currentcord]))
        if(deltasneg < 4):
            _,_,_,temp = deltaWallNeighbourCalculation(index,newset,currentcord,nx,ny,False,globaldata)
            shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(4-negdiff)],index,globaldata)
        if(deltaspos < 4):
            _,_,_,temp = deltaWallNeighbourCalculation(index,newset,currentcord,nx,ny,True,globaldata)
            shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(4-posdiff)],index,globaldata)

def interiorBalance(index,globaldata,hashtable,item):
    currentneighbours = getNeighbours(index,globaldata)
    currentcord = item
    _,_,_,_,xposvals = deltaNeighbourCalculation(currentneighbours,currentcord,True,False)
    _,_,_,_,xnegvals = deltaNeighbourCalculation(currentneighbours,currentcord,True,True)
    _,_,_,_,yposvals = deltaNeighbourCalculation(currentneighbours,currentcord,False,False)
    _,_,_,_,ynegvals = deltaNeighbourCalculation(currentneighbours,currentcord,False,True)
    xposw = conditionCheckWithNeighbours(index,globaldata,item,xposvals)
    xnegw = conditionCheckWithNeighbours(index,globaldata,item,xnegvals)
    yposw = conditionCheckWithNeighbours(index,globaldata,item,yposvals)
    ynegw = conditionCheckWithNeighbours(index,globaldata,item,ynegvals)
    try:
        if(xposw >= 20 or xnegw >= 20 or yposw >= 20 or ynegw >= 20):
            if(xposw >= 20):
                totalnbhs = []
                for itm in xposvals:
                    totalnbhs = totalnbhs + getNeighbours(hashtable.index(itm),globaldata)
                totalnbhs = list(set(totalnbhs) - set([item]) - set(xposvals))
                _,_,_,_,newxposvals = deltaNeighbourCalculation(totalnbhs,currentcord,True,False)
                newxposvals = minCondition(index,globaldata,currentcord,newxposvals,20)
                if(len(newxposvals) != 0):
                    appendNeighbours(newxposvals[:1],index,globaldata)
                else:
                    newxposvals = minCondition(index,globaldata,currentcord,newxposvals,xposw)
                    appendNeighbours(newxposvals[:1],index,globaldata)
                    print(currentcord,index)
            if(xnegw >= 20):
                totalnbhs = []
                for itm in xnegvals:
                    totalnbhs = totalnbhs + getNeighbours(hashtable.index(itm),globaldata)
                totalnbhs = list(set(totalnbhs) - set([item]) - set(xnegvals))
                _,_,_,_,newxnegvals = deltaNeighbourCalculation(totalnbhs,currentcord,True,True)
                newxnegvals = minCondition(index,globaldata,currentcord,newxposvals,20)
                if(len(newxnegvals) != 0):
                    appendNeighbours(newxnegvals[:1],index,globaldata)
                else:
                    newxnegvals = minCondition(index,globaldata,currentcord,newxnegvals,xposw)
                    appendNeighbours(newxnegvals[:1],index,globaldata)
            if(yposw >= 20):
                totalnbhs = []
                for itm in yposvals:
                    totalnbhs = totalnbhs + getNeighbours(hashtable.index(itm),globaldata)
                totalnbhs = list(set(totalnbhs) - set([item]) - set(xposvals))
                _,_,_,_,newyposvals = deltaNeighbourCalculation(totalnbhs,currentcord,True,False)
                newyposvals = minCondition(index,globaldata,currentcord,newyposvals,20)
                if(len(newyposvals) != 0):
                    appendNeighbours(newyposvals[:1],index,globaldata)
                else:
                    newyposvals = minCondition(index,globaldata,currentcord,newyposvals,xposw)
                    appendNeighbours(newyposvals[:1],index,globaldata)
            if(ynegw >= 20):
                totalnbhs = []
                for itm in ynegvals:
                    totalnbhs = totalnbhs + getNeighbours(hashtable.index(itm),globaldata)
                totalnbhs = list(set(totalnbhs) - set([item]) - set(ynegvals))
                _,_,_,_,newynegvals = deltaNeighbourCalculation(totalnbhs,currentcord,True,True)
                newynegvals = minCondition(index,globaldata,currentcord,newynegvals,20)
                if(len(newynegvals) != 0):
                    appendNeighbours(newynegvals[:1],index,globaldata)
                else:
                    newynegvals = minCondition(index,globaldata,currentcord,newynegvals,xposw)
                    appendNeighbours(newynegvals[:1],index,globaldata)
    except TypeError:
        pass
    # print(xpos,ypos,xneg,yneg)
    xpos,ypos,xneg,yneg,_ = deltaNeighbourCalculation(currentneighbours,currentcord,False,False)
    if(xpos < 4 or ypos < 4 or xneg < 4 or yneg < 4):
        currentnewneighbours = []
        # print("Old")
        # print(xpos,ypos,xneg,yneg)
        for item in currentneighbours:
            itemsneighbours = getNeighbours(hashtable.index(item),globaldata)
            currentnewneighbours = currentnewneighbours + list(set(itemsneighbours) - set(currentneighbours) - set(currentnewneighbours) - set([currentcord]))
        currentnewneighbours = currentnewneighbours
        if(xpos < 4):
            _,_,_,_,temp = deltaNeighbourCalculation(currentnewneighbours,currentcord,True,False)
            w,_ = conditionCheck(index,globaldata,currentcord)
            shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
            # shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(4-xpos)],index,globaldata)
        if(xneg < 4):
            _,_,_,_,temp = deltaNeighbourCalculation(currentnewneighbours,currentcord,True,True)
            w,_ = conditionCheck(index,globaldata,currentcord)
            shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
            # shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(4-xneg)],index,globaldata)
        if(ypos < 4):
            _,_,_,_,temp = deltaNeighbourCalculation(currentnewneighbours,currentcord,True,False)
            w,_ = conditionCheck(index,globaldata,currentcord) 
            shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
            # shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(4-ypos)],index,globaldata)
        if(yneg < 4):
            _,_,_,_,temp = deltaNeighbourCalculation(currentnewneighbours,currentcord,True,True)
            w,_ = conditionCheck(index,globaldata,currentcord)
            shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
            # shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(4-yneg)],index,globaldata)
        xpos,ypos,xneg,yneg,_ = deltaNeighbourCalculation(getNeighbours(hashtable.index(item),globaldata),currentcord,False,False)
        if(xpos < 4 or ypos < 4 or xneg < 4 or yneg < 4):
            None
            # print(getNeighbours(hashtable.index(item),globaldata))
            # print("No")
        # print("New")
        # print(xpos,ypos,xneg,yneg)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--neighbour",const=str, nargs="?")
    parser.add_argument("-w","--wall",const=str, nargs="?")
    args = parser.parse_args()
    print(args.neighbour)

    print("Loading Data")
    file1 = open(args.neighbour or "neighbour.txt","r")
    data = file1.read()
    data = data.replace("\t"," ")
    data = data.split("\n")
    data.pop(0)
    hashtable = ["start"]
    wallpoint = []
    # data[len(data)-1] = data[len(data)-1][:-1]
    # Wall Point
<<<<<<< HEAD
    file2 = open("airfoil_160.txt","r")
=======
    file2 = open(args.wall or "airfoil_160.txt","r")
>>>>>>> 034f822fe715476bd20388a088ef9da9c357a6f7
    geometrydata = file2.read()
    geometrydata = geometrydata.split("\n")
    firstxcord = 0
    firstycord = 0
    lastxcord = 0
    lastycord = 0
    index=1
    globaldata = []
    print("Loaded Data")
    print("Beginning Wall Point Processing")
    for i in range(len(geometrydata)):
        printProgressBar(i, len(geometrydata) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        xcord = float(geometrydata[i].split()[0])
        # print(len(geometrydata[i].split(" ")))
        # print(geometrydata[i].split(" ")[1])
        ycord = float(geometrydata[i].split()[1])
        hashtable.append(str(xcord)+','+str(ycord))
        wallpoint.append(str(xcord)+','+str(ycord))
        if(i==0):
            firstxcord = xcord
            firstycord = ycord
        elif(i==len(geometrydata)-1):
            lastxcord = xcord
            lastycord = ycord
        walldata = []
        if(index==1):
            walldata.append(index)
            walldata.insert(1,xcord)
            walldata.insert(2,ycord)
            walldata.insert(3,len(geometrydata))
            walldata.insert(4,index+1)
            walldata.insert(5,0)
            walldata.insert(6,1)
            globaldata.append(walldata)
            index+=1
        elif(index==len(geometrydata)):
            walldata.append(index)
            walldata.insert(1,xcord)
            walldata.insert(2,ycord)
            walldata.insert(3,len(geometrydata)-1)
            walldata.insert(4,1)
            walldata.insert(5,0)
            walldata.insert(6,1)
            globaldata.append(walldata)
            index+=1
        else:
            walldata.append(index)
            walldata.insert(1,xcord)
            walldata.insert(2,ycord)
            walldata.insert(3,index-1)
            walldata.insert(4,index+1)
            walldata.insert(5,0)
            walldata.insert(6,1)
            globaldata.append(walldata)
            index+=1
    print("Wall Point Processed")

    #
    print("Beginning Interior Point and Wall Point Neighbour Processing")
    # Interior and Outer Point
    for i in range(len(data)):
        printProgressBar(i, len(data) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        cleandata = str(data[i]).split(" ")
        cord = str(float(cleandata[1].split(",")[0])) + "," + str(float(cleandata[1].split(",")[1]))
        try:
            if(i!=len(data)-1):
                val = hashtable.index(cord)
                cleandata.pop(0)
                cleandata.pop(-1)
                cleandata.pop(-2)
                cleandata.pop(0)
                cleandata.insert(0,str(int(cleandata[len(cleandata)-1]) + 2))
                cleandata.pop(-1)
                cleandata.append(str(float(hashtable[int(globaldata[val-1][3])].split(",")[0])) + "," + str(float(hashtable[int(globaldata[val-1][3])].split(",")[1])))
                cleandata.append(str(float(hashtable[int(globaldata[val-1][4])].split(",")[0])) + "," + str(float(hashtable[int(globaldata[val-1][4])].split(",")[1])))
                globaldata[val-1] = globaldata[val-1] + cleandata
            else:
                val = hashtable.index(cord)
                cleandata.pop(0)
                cleandata.pop(-2)
                cleandata.pop(0)
                cleandata.insert(0,str(int(cleandata[len(cleandata)-1]) + 2))
                cleandata.pop(-1)
                cleandata.append(str(float(hashtable[int(globaldata[val-1][3])].split(",")[0])) + "," + str(float(hashtable[int(globaldata[val-1][3])].split(",")[1])))
                cleandata.append(str(float(hashtable[int(globaldata[val-1][4])].split(",")[0])) + "," + str(float(hashtable[int(globaldata[val-1][4])].split(",")[1])))
                globaldata[val-1] = globaldata[val-1] + cleandata
        except Exception as err:
            if(i!=len(data)-1):
                hashtable.append(cord)
                cleandata.pop(0)
                cleandata.pop(-1)
                cleandata.pop(-2)
                cleandata.pop(0)        
                cleandata.insert(0,cleandata[len(cleandata)-1])
                cleandata.pop(-1)
                cleandata.insert(0,1)
                cleandata.insert(0,1)
                cleandata.insert(0,0)
                cleandata.insert(0,0)
                cleandata.insert(0,cord.split(",")[1])
                cleandata.insert(0,cord.split(",")[0])
                cleandata.insert(0,index)
                index+=1
                globaldata.append(cleandata)
            else:
                hashtable.append(cord)
                cleandata.pop(0)
                cleandata.pop(-2)
                cleandata.pop(0)        
                cleandata.insert(0,cleandata[len(cleandata)-1])
                cleandata.pop(-1)
                cleandata.insert(0,1)
                cleandata.insert(0,1)
                cleandata.insert(0,0)
                cleandata.insert(0,0)
                cleandata.insert(0,cord.split(",")[1])
                cleandata.insert(0,cord.split(",")[0])
                cleandata.insert(0,index)
                index+=1
                globaldata.append(cleandata)
    print("Interior Point and Wall Point Neighbour Processed")

    # Remove Duplicate Neighbours
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

    # Find Outer Points
    print("Beginning Left and Right Detection of Outer Points")
    # Outer Point scan
    biggestxy = getBiggestXBiggestY(hashtable[1:])
    smallestxy = getSmallestXSmallestY(hashtable[1:])
    smallestxbiggesty = getSmallestXBiggestY(hashtable[1:])
    biggestxsmallesty = getBiggestXSmallestY(hashtable[1:])
    startindex = hashtable.index(biggestxy) - 1
    currentstatus = 1
    currentcord = biggestxy
    previouscord = biggestxy
    count = 0
    ## Going Left (+x to -x)sm
    while True:
        count += 1
        printProgressBar(currentstatus, 5, prefix = 'Progress:', suffix = 'Complete', length = 50)
        currentneighbours = getNeighbours(hashtable.index(currentcord) - 1,globaldata)
        # print(currentcord,currentneighbours)
        # if(currentcord=='9.375,-1.875'):
        #     break
        # print(currentneighbours)
        # print(currentcord)
        if(currentstatus == 1):
            # print(currentcord)
            currentneighbours = getNeighboursDirectional(1,currentcord,currentneighbours)
            try:
                xvals = getXCordNeighbours(currentneighbours)
                currentnewneighbours = []
                for index,item in enumerate(xvals):
                    if(item==min(xvals)):
                        currentnewneighbours.append(currentneighbours[index])
                currentYCords = getYCordNeighbours(currentneighbours)
                leftcord = currentneighbours[currentYCords.index(max(currentYCords))]
                # print(leftcord)
            except Exception:
                None
            if(currentcord == smallestxbiggesty):
                currentstatus += 1
                ## Switch Direction to bottom
            startindex = hashtable.index(currentcord) - 1
        elif(currentstatus == 2):
            # print(currentcord,currentneighbours)
            currentneighbours = getNeighboursDirectional(2,currentcord,currentneighbours)
            try:
                yvals = getYCordNeighbours(currentneighbours)
                currentnewneighbours = []
                for index,item in enumerate(yvals):
                    if(item==min(yvals)):
                        currentnewneighbours.append(currentneighbours[index])
                currentXCords = getXCordNeighbours(currentneighbours)
                leftcord = currentneighbours[currentXCords.index(min(currentXCords))]
                # print(leftcord)
            except Exception:
                None
            if(currentcord == smallestxy):
                currentstatus += 1
                ## Switch Direction to bottom
            startindex = hashtable.index(currentcord) - 1
        elif(currentstatus == 3):
            # print(currentcord)
            currentneighbours = getNeighboursDirectional(3,currentcord,currentneighbours)
            try:
                xvals = getXCordNeighbours(currentneighbours)
                currentnewneighbours = []
                for index,item in enumerate(xvals):
                    if(item==max(xvals)):
                        currentnewneighbours.append(currentneighbours[index])
                currentYCords = getYCordNeighbours(currentnewneighbours)                
                leftcord = currentnewneighbours[currentYCords.index(min(currentYCords))]
                # print(leftcord)
            except Exception:
                None
            if(currentcord == biggestxsmallesty):
                currentstatus += 1
                ## Switch Direction to bottom
            startindex = hashtable.index(currentcord) - 1
        elif(currentstatus == 4):
            currentneighbours = getNeighboursDirectional(4,currentcord,currentneighbours)
            try:
                yvals = getYCordNeighbours(currentneighbours)
                currentnewneighbours = []
                for index,item in enumerate(yvals):
                    if(item==max(yvals)):
                        currentnewneighbours.append(currentneighbours[index])
                currentXCords = getXCordNeighbours(currentnewneighbours)
                leftcord = currentnewneighbours[currentXCords.index(max(currentXCords))]
                # print(leftcord)
            except Exception:
                None
            if(currentcord == biggestxy):
                globaldata = updateRight(hashtable.index(biggestxy) - 1,globaldata,previouscord)
                printProgressBar(5, 5, prefix = 'Progress:', suffix = 'Complete', length = 50)
                break
            startindex = hashtable.index(currentcord) - 1
        globaldata = updateRight(startindex,globaldata,previouscord)
        globaldata = updateFlag(startindex,globaldata,2)
        globaldata = updateLeft(startindex,globaldata,leftcord)
        previouscord = currentcord
        currentcord = leftcord
    print("Outer Points Left and Right Detection Complete")

    ## Point Validation
    print("Beginning Point Delta Calculation")
    for index,item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1):
            interiorBalance(index,globaldata,hashtable,item)
        elif(getFlag(index,globaldata)==0):
            wallBalance(index,globaldata,hashtable,item,3,wallpoint)
        elif(getFlag(index,globaldata)==2):
            outerBalance(index,globaldata,hashtable,item)
    print("Points Delta Calculated and Balanced")

    # Dup Neighbour Cleanup
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

    # Replacer Code
    print("Beginning Replacement")
    for index2,item in enumerate(hashtable):
        printProgressBar(index2, len(hashtable) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        for index, individualitem in enumerate(globaldata):
            globaldata[index] = [hashtable.index(x) if x==str(item) else x for x in individualitem]
    
    with open("preprocessorfile.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")
<<<<<<< HEAD
=======
    # deltaData = []
    # for index,item in enumerate(globaldata):
    #     mainptx = float(item[1])
    #     mainpty = float(item[2])
    #     nbh = getNeighbours(index,globaldata)
    #     deltaSumX = 0
    #     deltaSumY = 0
    #     deltaSumXY = 0
    #     data = []
    #     for nbhitem in nbh:
    #         nbhitemX = float(nbhitem.split(",")[0])
    #         nbhitemY = float(nbhitem.split(",")[1])
    #         deltaSumX = deltaSumX + (nbhitemX-mainptx)**2
    #         deltaSumY = deltaSumY + (nbhitemY-mainpty)**2
    #         deltaSumXY = deltaSumXY + (nbhitemX-mainptx)*(nbhitemY-mainpty)
    #     data.append(deltaSumX)
    #     data.append(deltaSumXY)
    #     data.append(deltaSumXY)
    #     data.append(deltaSumY)
    #     deltaData.append(data)
    #     random = np.array(deltaData[index])
    #     shape = (2,2)
    #     random = random.reshape(shape)
    #     w,v = LA.eig(random)
    #     w = max(w)/min(w)
    #     s = np.linalg.svd(random,full_matrices=False,compute_uv=False)
    #     s = max(s)/min(s)
    #     with open("eig.txt", "a+") as text_file:
    #         if(s >= 0):
    #             text_file.writelines([str(index)," ",str(w)," ", str(s)])
    #             text_file.writelines("\n")
        # print(max(w)/min(w))


            
    # print(deltaData)
>>>>>>> 034f822fe715476bd20388a088ef9da9c357a6f7

if __name__ == "__main__":
    main()