def getNeighbours(indexval,list):
    val = []
    pointdata = list[indexval]
    numbneigh = int(pointdata[7])
    for i in range(numbneigh):
        val = val + [str(pointdata[i+8])]
    return val

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
        stuff.append(item.split(",")[1])
    return stuff

def getXCordNeighbours(list):
    stuff = []
    for item in list:
        stuff.append(item.split(",")[0])
    return stuff

def isPositive(val):
    if(float(val)>=0): return True
    else: return False

def getSmallestXBiggestY(list):
    newlist = []
    for item in list:
        if(isPositive(float(item.split(",")[0])) == False and isPositive(float(item.split(",")[1])) == True):
            newlist.append(item)
    getSmallestX = min(getXCordNeighbours(newlist))
    templist = []
    for item in newlist:
        if((item.split(",")[0])==getSmallestX):
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
        if((item.split(",")[0])==getBiggestX):
            templist.append(item)
    getSmallestY = min(getYCordNeighbours(templist))
    return str(getBiggestX) + "," + str(getSmallestY)

def getNeighboursDirectional(direction,maincord,list):
    finallist = []
    xcord = float(maincord.split(",")[0])
    ycord = float(maincord.split(",")[1])
    if(direction==1):
        ## All points towards left of X
        finallist = [x for x in list if float(x.split(",")[0]) < xcord]
    elif(direction==2):
        ## All points towards bottom of Y
        finallist = [x for x in list if float(x.split(",")[1]) < ycord]
    elif(direction==3):
        ## All points towards right of X
        finallist = [x for x in list if float(x.split(",")[0]) > xcord]
    elif(direction==4):
        ## All points towards top of Y
        finallist = [x for x in list if float(x.split(",")[1]) > xcord]
    return finallist

def main():
    file1 = open("neighbour.txt","r")
    data = file1.read()
    data = data.replace("\t"," ")
    data = data.split("\n")
    data.pop(0)
    hashtable = ["start"]
    data[len(data)-1] = data[len(data)-1][:-1]
    # Wall Point
    file2 = open("input.txt","r")
    geometrydata = file2.read()
    geometrydata = geometrydata.split("\n")
    firstxcord = 0
    firstycord = 0
    lastxcord = 0
    lastycord = 0
    index=1
    globaldata = []
    for i in range(len(geometrydata)):
        xcord = geometrydata[i].split(" ")[0]
        # print(len(geometrydata[i].split(" ")))
        # print(geometrydata[i].split(" ")[1])
        ycord = geometrydata[i].split(" ")[1]
        hashtable.append(xcord+','+ycord)
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
            walldata.insert(3,1)
            walldata.insert(4,len(geometrydata)-1)
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

    # Interior and Outer Point
    for i in range(len(data)):
        cleandata = str(data[i]).split(" ")
        cord = cleandata[1]
        try:
            val = hashtable.index(cord)
            cleandata.pop(0)
            cleandata.pop(-1)
            cleandata.pop(-2)
            cleandata.pop(0)
            cleandata.insert(0,cleandata[len(cleandata)-1])
            cleandata.pop(-1)
            globaldata[val-1] = globaldata[val-1] + cleandata
        except Exception as err:
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

    # Outer Point scan
    biggestxy = max(hashtable[1:])
    smallestxy = min(hashtable[1:])
    smallestxbiggesty = getSmallestXBiggestY(hashtable[1:])
    biggestxsmallesty = getBiggestXSmallestY(hashtable[1:])
    startindex = hashtable.index(biggestxy) - 1
    currentstatus = 1
    currentcord = biggestxy
    previouscord = biggestxy

    ## Going Left (+x to -x)
    while True:
        currentneighbours = getNeighbours(hashtable.index(currentcord) - 1,globaldata)
        # print(currentneighbours)
        # print(currentcord)
        if(currentstatus == 1):
            currentneighbours = getNeighboursDirectional(1,currentcord,currentneighbours)
            currentYCords = getYCordNeighbours(currentneighbours)
            try:
                leftcord = currentneighbours[currentYCords.index(max(currentYCords))]
            except Exception:
                None
            if(currentcord == smallestxbiggesty):
                currentstatus += 1
                ## Switch Direction to bottom
            startindex = hashtable.index(currentcord) - 1
        elif(currentstatus == 2):
            currentneighbours = getNeighboursDirectional(2,currentcord,currentneighbours)
            currentXCords = getXCordNeighbours(currentneighbours)
            try:
                leftcord = currentneighbours[currentXCords.index(min(currentXCords))]
            except Exception:
                None
            if(currentcord == smallestxy):
                currentstatus += 1
                ## Switch Direction to bottom
            startindex = hashtable.index(currentcord) - 1
        elif(currentstatus == 3):
            currentneighbours = getNeighboursDirectional(3,currentcord,currentneighbours)
            currentYCords = getYCordNeighbours(currentneighbours)
            try:
                leftcord = currentneighbours[currentYCords.index(min(currentYCords))]
            except Exception:
                None
            if(currentcord == biggestxsmallesty):
                currentstatus += 1
                ## Switch Direction to bottom
            startindex = hashtable.index(currentcord) - 1
        elif(currentstatus == 4):
            currentneighbours = getNeighboursDirectional(4,currentcord,currentneighbours)
            currentXCords = getXCordNeighbours(currentneighbours)
            try:
                leftcord = currentneighbours[currentXCords.index(max(currentXCords))]
            except Exception:
                None
            if(currentcord == biggestxy):
                globaldata = updateRight(hashtable.index(biggestxy) - 1,globaldata,previouscord)
                break
                ## Switch Direction to bottom
            startindex = hashtable.index(currentcord) - 1
        globaldata = updateRight(startindex,globaldata,previouscord)
        globaldata = updateFlag(startindex,globaldata,2)
        globaldata = updateLeft(startindex,globaldata,leftcord)
        previouscord = currentcord
        currentcord = leftcord

    ## Replacer Code
    for item in hashtable:
        for index, individualitem in enumerate(globaldata):
            globaldata[index] = [hashtable.index(x) if x==str(item) else x for x in individualitem]
    
    with open("output.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")

if __name__ == "__main__":
    main()