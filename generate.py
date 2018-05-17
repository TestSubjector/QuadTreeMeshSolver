def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
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

def deltaNeighbourCalculation(currentneighbours,currentcord):
    xpos,xneg,ypos,yneg = 0,0,0,0
    for item in currentneighbours:
        if((deltaX(float(currentcord.split(",")[0]), float(item.split(",")[0]))) <= 0):
            xpos = xpos + 1
        if((deltaX(float(currentcord.split(",")[0]), float(item.split(",")[0]))) >= 0):
            xneg = xneg + 1
        if((deltaY(float(currentcord.split(",")[1]), float(item.split(",")[1]))) <= 0):
            ypos = ypos + 1
        if((deltaY(float(currentcord.split(",")[1]), float(item.split(",")[1]))) >= 0):
            yneg = yneg + 1
    return xpos,ypos,xneg,xneg

def main():
    print("Hello World")
    print("Loading Data")
    file1 = open("neighbour.txt","r")
    data = file1.read()
    data = data.replace("\t"," ")
    data = data.split("\n")
    data.pop(0)
    hashtable = ["start"]
    # data[len(data)-1] = data[len(data)-1][:-1]
    # Wall Point
    file2 = open("airfoil2.txt","r")
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
        xcord = geometrydata[i].split()[0]
        # print(len(geometrydata[i].split(" ")))
        # print(geometrydata[i].split(" ")[1])
        ycord = geometrydata[i].split()[1]
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
    print("Wall Point Processed")
    print("Beginning Interior and Outer Point Processing")
    # Interior and Outer Point
    for i in range(len(data)):
        printProgressBar(i, len(data) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        cleandata = str(data[i]).split(" ")
        cord = cleandata[1]
        try:
            if(i!=len(data)-1):
                val = hashtable.index(cord)
                cleandata.pop(0)
                cleandata.pop(-1)
                cleandata.pop(-2)
                cleandata.pop(0)
                cleandata.insert(0,cleandata[len(cleandata)-1])
                cleandata.pop(-1)
                globaldata[val-1] = globaldata[val-1] + cleandata
            else:
                val = hashtable.index(cord)
                cleandata.pop(0)
                cleandata.pop(-2)
                cleandata.pop(0)
                cleandata.insert(0,cleandata[len(cleandata)-1])
                cleandata.pop(-1)
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
    print("Interior Point and Wall Points Processed")
    print("Beginning Left and Right Detection of Wall Points")
    # Outer Point scan
    biggestxy = max(hashtable[1:])
    smallestxy = getSmallestXSmallestY(hashtable[1:])
    smallestxbiggesty = getSmallestXBiggestY(hashtable[1:])
    biggestxsmallesty = getBiggestXSmallestY(hashtable[1:])
    startindex = hashtable.index(biggestxy) - 1
    currentstatus = 1
    currentcord = biggestxy
    previouscord = biggestxy
    ## Going Left (+x to -x)sm
    while True:
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
            # print(currentcord,currentneighbours)
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
    print("Wall Points Left and Right Detection Complete")

    ## Interior Point Validation
    print("Beginning Interior Point Delta Calculation")
    total,detect,detect2 = 0,0,0
    for index,item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1):
            total = total + 1
            currentneighbours = getNeighbours(index,globaldata)
            currentcord = item
            xpos,ypos,xneg,yneg = deltaNeighbourCalculation(currentneighbours,currentcord)
            if(xpos < 3 or ypos < 3 or xneg < 3 or yneg < 3):
                detect = detect + 1
                currentnewneighbours = []
                print("Old")
                print(xpos,ypos,xneg,yneg)
                for item in currentneighbours:
                    itemsneighbours = getNeighbours(hashtable.index(item),globaldata)
                    currentnewneighbours = currentnewneighbours + list(set(itemsneighbours) - set(currentneighbours) - set(currentnewneighbours))
                xpos,ypos,xneg,yneg = deltaNeighbourCalculation(currentnewneighbours,currentcord)
                if(xpos < 3 or ypos < 3 or xneg < 3 or yneg < 3):
                    detect2 = detect2 + 1
                print("New")
                print(xpos,ypos,xneg,yneg)
    print(total,detect,detect2)
    print("Interior Points Delta Calculated and Balanced")

    ## Replacer Code
    print("Beginning Replacement")
    for index2,item in enumerate(hashtable):
        printProgressBar(index2, len(hashtable) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        for index, individualitem in enumerate(globaldata):
            globaldata[index] = [hashtable.index(x) if x==str(item) else x for x in individualitem]
    
    with open("output.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")

if __name__ == "__main__":
    main()