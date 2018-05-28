import argparse
from load import *
from boundary import *
from interior import *
from balance import *
from wall import *
from outer import *
# import progress

def main():
    
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--neighbour",const=str, nargs="?")
    parser.add_argument("-w","--wall",const=str, nargs="?")
    args = parser.parse_args()
    print("Loading Data")
    
    # Opening the Neighbourhood file
    file1 = open(args.neighbour or "neighbour.txt","r")
    data = file1.read()
    file1.close()
    data = data.replace("\t"," ")
    data = data.split("\n")
    data.pop(0) # Pops the first blank line

    file2 = open(args.wall or "airfoil_160.txt","r")
    geometrydata = file2.read()
    geometrydata = geometrydata.split("\n")
    
    print("Loaded Data")

    hashtable,wallpoint,globaldata = loadWall(geometrydata)
    hashtable,globaldata = loadInterior(data,hashtable,globaldata,len(hashtable))
    globaldata = cleanNeighbours(globaldata)
    hashtable,globaldata = detectOuter(hashtable, globaldata)

    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==0):
            printWallConditionValue(index,globaldata,hashtable)
            printWallConditionValue(index,globaldata,hashtable)
            printWallConditionValue(index,globaldata,hashtable)

    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==2):
            printOuterConditionValue(index,globaldata,hashtable)
            printOuterConditionValue(index,globaldata,hashtable)
            printOuterConditionValue(index,globaldata,hashtable)

    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1):
            globaldata = setPosDeltaFlags(index,globaldata,hashtable,100) #Threshold for Flag 3 - 6

    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1):
            conditionValueFixForYPos(index,globaldata,hashtable,15)
    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1):
            conditionValueFixForYNeg(index,globaldata,hashtable,15)
    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1):
            conditionValueFixForXPos(index,globaldata,hashtable,15)
    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1):
            conditionValueFixForXNeg(index,globaldata,hashtable,15)

    # print("****************************************")
    # print("Rechecking after XPos and XNeg")
    # print("****************************************")
    
    # for index, item in enumerate(hashtable[1:]):
    #     if(getFlag(index,globaldata)==1):
    #         conditionValueFixForYPos(index,globaldata,hashtable,15)
    # for index, item in enumerate(hashtable[1:]):
    #     if(getFlag(index,globaldata)==1):
    #         conditionValueFixForYNeg(index,globaldata,hashtable,15)
    # for index, item in enumerate(hashtable[1:]):
    #     if(getFlag(index,globaldata)==1):
    #         printPosDeltaConditions(index,globaldata,hashtable,15)
    # print("****************************************")

    globaldata = cleanNeighbours(globaldata)
    globaldata = generateReplacement(hashtable,globaldata)

    with open("preprocessorfile.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")

if __name__ == "__main__":
    main()