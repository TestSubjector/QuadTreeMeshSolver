import core
from progress import printProgressBar
import argparse

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()

    print("Loading Data")

    file1 = open(args.input or "preprocessorfile.txt", "r")
    data = file1.read()
    globaldata = ["start"]
    splitdata = data.split("\n")
    splitdata = splitdata[:-1]

    print("Processed Pre-Processor File")
    print("Converting to readable format")

    for idx, itm in enumerate(splitdata):
        printProgressBar(
            idx, len(splitdata) - 1, prefix="Progress:", suffix="Complete", length=50
        )
        itm = itm.split(" ")
        itm.pop(-1)
        entry = itm
        globaldata.append(entry)

    globaldata = core.cleanNeighbours(globaldata)
    wallpoints = core.getWallPointArray(globaldata)
    wallpointsData = core.generateWallPolygons(wallpoints)

    print("Running Non Aero Checks")

    for idx in range(1,len(globaldata)):
        printProgressBar(idx, len(globaldata) - 1, prefix="Progress:", suffix="Complete", length=50)    
        nbhs = core.getNeighbours(idx,globaldata)
        for itm in nbhs:
            cord = core.getPointxy(itm,globaldata)
            if core.isNonAeroDynamic(idx,cord,globaldata,wallpointsData):
                print("Point",idx,"has a non aero point with index",itm)

    print("Done")

if __name__ == "__main__":
    main()