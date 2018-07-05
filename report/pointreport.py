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
    wallpoints = core.getWallPointArray(globaldata[1:])
    wallpointsData = core.generateWallPolygons(wallpoints)

    ptidx = input("Which point do you want to check? ")
    ptidx = int(ptidx)

    print("Point Index:",ptidx)
    print("Point Co ordinate:",core.getPointxy(ptidx,globaldata))
    flag = core.getFlag(ptidx,globaldata)
    flag = int(flag)
    if flag == 0:
        flagd = "Wall Point"
    elif flag == 1:
        flagd = "Interior Point"
    else:
        flagd = "Outer Point"
    print("Point Type:",flagd)
    nbhs = core.getNeighbours(ptidx,globaldata)
    print("Total Number of Neighbours:",len(nbhs))
    print("Neighbour Array")
    print(nbhs)
    if(flag==0):
        print(core.getConditionNumberNormal(ptidx,globaldata))
        xpos = core.getDWallXPosPoints(ptidx,globaldata)
        xneg = core.getDWallXNegPoints(ptidx,globaldata)
        print("xpos",len(xpos),"xneg",len(xneg))
    else:
        print(core.getConditionNumber(ptidx,globaldata))
        xpos = core.getDXPosPoints(ptidx,globaldata)
        xneg = core.getDXNegPoints(ptidx,globaldata)
        ypos = core.getDYPosPoints(ptidx,globaldata)
        yneg = core.getDYNegPoints(ptidx,globaldata)
        print("xpos",len(xpos),"xneg",len(xneg),"ypos",len(ypos),"yneg",len(yneg))

if __name__ == "__main__":
    main()