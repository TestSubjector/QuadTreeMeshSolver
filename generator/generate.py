import argparse
from load import *
from boundary import *
from interior import *
from balance import *
from wall import *
from outer import *
from progress import *
from logger import *

def main():
    
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--neighbour",const=str, nargs="?")
    parser.add_argument("-w","--wall",const=str, nargs="?")
    args = parser.parse_args()
    print("Loading Data")

    CONDITIONTHRESHOLD = 2000
    
    # Opening the Neighbourhood file
    file1 = open(args.neighbour or "neighbour.txt","r")
    data = file1.read()
    file1.close()
    data = data.replace("\t"," ")
    data = data.split("\n")
    data.pop(0) # Pops the first blank line

    file2 = open(args.wall or "airfoil_160.txt","r")
    geometrydata = file2.read()
    file2.close()
    geometrydata = geometrydata.split("\n")
    
    print("Loaded Data")
    silentRemove("log.txt")
    wallpoints = []

    interiorPointsCount = 0
    outerPointsCount = 0

    hashtable,wallpointsdata,globaldata = loadWall(geometrydata)
    wallpoints.append(wallpointsdata)
    hashtable,globaldata = loadInterior(data,hashtable,globaldata,len(hashtable))
    globaldata = cleanNeighbours(globaldata)
    hashtable,globaldata = detectOuter(hashtable, globaldata)

    PSUEDODETECTION = calculateAverageWallPointDistance(globaldata,wallpoints)/20
    writeLog(["Auto set PSUEDODETECTION TO",PSUEDODETECTION])

    # printL("***********************************")
    # printL("Checking for Non Aerodynamic points")
    # printL("***********************************")

    # for index,item in enumerate(hashtable[1:]):
    #     printProgressBar(index,len(hashtable[1:])-1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #     if(getFlag(index,globaldata)==1):
    #         nonAeroCheck(index,globaldata,wallpoints)

    # printL("***********************************")
    
    # fixPsuedoWallPoints(2295,globaldata,hashtable,wallpoints,PSUEDODETECTION)
    # fixPsuedoWallPoints(2296,globaldata,hashtable,wallpoints,PSUEDODETECTION)
    # fixPsuedoWallPoints(2297,globaldata,hashtable,wallpoints,PSUEDODETECTION)
    # fixPsuedoWallPoints(2298,globaldata,hashtable,wallpoints,PSUEDODETECTION)
    # fixPsuedoWallPoints(2299,globaldata,hashtable,wallpoints,PSUEDODETECTION)

    # exit()


    printL("****************************************")
    printL("Adding Wall Points")
    printL("****************************************")

    # for index,item in enumerate(hashtable[1:]):
    #     if(getFlag(index,globaldata)==1):
    #         initialConditionValueXPos = getInteriorConditionValueofXPos(index,globaldata,hashtable)
    #         initialConditionValueXNeg = getInteriorConditionValueofXNeg(index,globaldata,hashtable)
    #         initialConditionValueYPos = getInteriorConditionValueofYPos(index,globaldata,hashtable)
    #         initialConditionValueYNeg = getInteriorConditionValueofYNeg(index,globaldata,hashtable)
    #         if(math.isinf(initialConditionValueXNeg)):
    #             addNearestWallPoints(index,globaldata,hashtable,wallpoints)
    #         elif(math.isinf(initialConditionValueXPos)):
    #             addNearestWallPoints(index,globaldata,hashtable,wallpoints)
    #         elif(math.isinf(initialConditionValueYNeg)):
    #             addNearestWallPoints(index,globaldata,hashtable,wallpoints)
    #         elif(math.isinf(initialConditionValueYPos)):
    #             addNearestWallPoints(index,globaldata,hashtable,wallpoints)

    printL("***********************************")

    globaldata = cleanNeighbours(globaldata)

    for index,_ in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1 or getFlag(index,globaldata)==3):
            interiorPointsCount = interiorPointsCount + 1
            printPosDeltaConditions(index,globaldata,hashtable,15)
    
    printL("***********************************")

    # for index,_ in enumerate(hashtable[1:]):
    #     if(getFlag(index,globaldata)==1 or getFlag(index,globaldata)==3):
    #         printWeighedPosDeltaConditions(index,globaldata,hashtable,15)

    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==0):
            printWallConditionValue(index,globaldata,hashtable)
            printWallConditionValue(index,globaldata,hashtable)
            printWallConditionValue(index,globaldata,hashtable)
            writeLog([index,"Condition Value Wall Point",conditionValueOfPointFull(index,globaldata)])

    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==2):
            outerPointsCount = outerPointsCount + 1
            printOuterConditionValue(index,globaldata,hashtable)
            printOuterConditionValue(index,globaldata,hashtable)
            printOuterConditionValue(index,globaldata,hashtable)

    printL("***********************************")
    printL("Setting Pre Balancing Flags for Interior Points")
    printL("***********************************")

    problempts = []

    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1):
            globaldata = setPosDeltaFlags(index,globaldata,hashtable,100, problempts,1) #Threshold for Flag 3 - 6

    printL("***********************************")
    printL("Writing Removal Points To File")
    printL("***********************************")

    problempts = [x+1 for x in problempts]
    with open("removal_points.txt", "w") as text_file:
        for item1 in problempts:
            text_file.writelines(["%s " % item1])
            text_file.writelines("\n")
    
    # print(problempts)

    printL("***********************************")
    printL("Fixing Interior Points")
    printL("***********************************")

    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1 or getFlag(index,globaldata)==3):
            conditionValueFixForYPos(index,globaldata,hashtable,15,wallpoints,-1, 1)
    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1 or getFlag(index,globaldata)==3):
            conditionValueFixForYNeg(index,globaldata,hashtable,15,wallpoints, -1, 1)
    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1 or getFlag(index,globaldata)==3):
            conditionValueFixForXPos(index,globaldata,hashtable,15,wallpoints, -1, 1)
    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1 or getFlag(index,globaldata)==3):
            conditionValueFixForXNeg(index,globaldata,hashtable,15,wallpoints, -1, 1)

    # # for index, item in enumerate(hashtable[1:]):
    # #     if(getFlag(index,globaldata)==1):
    # #         globaldata = setPosDeltaFlags(index,globaldata,hashtable,400) #Threshold for Flag 3 - 6

    # printL("****************************************")
    # printL("Printing Delta Conditions for Interior Points")
    # printL("****************************************")

    # for index,item in enumerate(hashtable[1:]):
    #     if(getFlag(index,globaldata)==1 or getFlag(index,globaldata)==3):
    #         printPosDeltaConditions(index,globaldata,hashtable,15)

    printL("***********************************")

    for index,item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1 or getFlag(index,globaldata)==3):
            printWeighedPosDeltaConditions(index,globaldata,hashtable,15)
            
    # printL("Checking for Points to Nuke")
    # printL("***********************************")
    
    # for index,_ in enumerate(hashtable[1:]):
    #     if(getFlag(index,globaldata)==1):
    #         globaldata = fixPsuedoWallPoints(index,globaldata,hashtable,wallpoints,CONDITIONTHRESHOLD)

    # printL("****************************************")
    # printL("Printing Delta Neighbour Conditions for Interior Points")
    # printL("****************************************")
    
    # for index,item in enumerate(hashtable[1:]):
    #     if(getFlag(index,globaldata)==1):
    #         printPosDeltaPointConditions(index,globaldata,hashtable,3)

    printL("****************************************")
    print("Interior Points are " + str(interiorPointsCount))
    print("Outer Points are " + str(outerPointsCount))
    printL("****************************************")

    globaldata = cleanNeighbours(globaldata)
    globaldata = generateReplacement(hashtable,globaldata)

    with open("preprocessorfile.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")

if __name__ == "__main__":
    main()