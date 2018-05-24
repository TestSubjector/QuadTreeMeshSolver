import argparse
from load import *
from boundary import *
from interior import *
from balance import *
from wall import *
from outer import *
import progress

def main():
    
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--neighbour",const=str, nargs="?")
    parser.add_argument("-w","--wall",const=str, nargs="?")
    args = parser.parse_args()
    print("Loading Data")
    
    # Opening the Neighbourhood file
    file1 = open(args.neighbour or "neighbour.txt","r")
    file11 = open("neighbour_copy.txt","r")
    data = file1.read()
    data_copy = file11.read()
    file1.close()
    file11.close()
    assert(data == data_copy),"ERROR - Input file changed"
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
    
    # print("Wall Points")

    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==0):
            printWallConditionValue(index,globaldata,hashtable)
            printWallConditionValue(index,globaldata,hashtable)
            printWallConditionValue(index,globaldata,hashtable)
            
    # print("****************************************")

    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==0):
            printWall(index,globaldata,hashtable)

    # print("Outer Points")

    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==2):
            printOuterConditionValue(index,globaldata,hashtable)
            printOuterConditionValue(index,globaldata,hashtable)
            printOuterConditionValue(index,globaldata,hashtable)

    for index, item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==2):
            printOuter(index,globaldata,hashtable)

    # print("****************************************")

    # printOuterConditionValue(160,globaldata,hashtable)
    # printOuter(160,globaldata,hashtable)

    globaldata = cleanNeighbours(globaldata)
    globaldata = generateReplacement(hashtable,globaldata)

    with open("preprocessorfile.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")

if __name__ == "__main__":
    main()