from progress import *

def loadWall(geometrydata):
    print("Beginning Wall Point Processing")
    hashtable = ["start"]
    wallpoint = []
    firstxcord = 0
    firstycord = 0
    lastxcord = 0
    lastycord = 0
    index=1
    globaldata = []
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
    return hashtable,wallpoint,globaldata

def loadInterior(data,hashtable,globaldata,index):
    print("Beginning Interior Point and Wall Point Neighbour Processing")
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
    return hashtable,globaldata