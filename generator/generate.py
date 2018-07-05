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
    parser.add_argument("-n", "--neighbour", const=str, nargs="?")
    parser.add_argument("-w", "--wall", nargs="+")
    args = parser.parse_args()
    print("Loading Data")

    CONDITIONTHRESHOLD = 2000

    # Opening the Neighbourhood file
    file1 = open(args.neighbour or "neighbour.txt", "r")
    data = file1.read()
    file1.close()
    data = data.replace("\t", " ")
    data = data.split("\n")
    data.pop(0)  # Pops the first blank line

    interiorPointsCount = 0
    outerPointsCount = 0

    wallarg = args.wall
    wallpoints = []
    hashtable = ["start"]
    globaldata = []

    silentRemove("log.txt")

    printL(str("Found " + str(len(wallarg)) + " wall geometry files."))
    for idx,itm in enumerate(wallarg):
        printL(str("Loading Geometry " + str(itm)))
        file2 = open(str(itm) or "airfoil_160.txt", "r")
        geometrydata = file2.read()
        file2.close()
        geometrydata = geometrydata.split("\n")
        hashtable, wallpointsdata, globaldata = loadWall(geometrydata,hashtable,globaldata,idx + 1)
        wallpoints.append(wallpointsdata)

    printL("Loading Interior and Outer Points")
    hashtable, globaldata = loadInterior(data, hashtable, globaldata, len(hashtable))
    globaldata = cleanNeighbours(globaldata)
    hashtable, globaldata = detectOuter(hashtable, globaldata)

    globaldata = cleanNeighbours(globaldata)
    globaldata = generateReplacement(hashtable, globaldata)

    with open("preprocessorfile.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")


if __name__ == "__main__":
    main()
