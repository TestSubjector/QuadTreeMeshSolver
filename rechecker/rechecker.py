import argparse
from progress import printProgressBar
from core import *
import copy


def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()

    print("Loading Data")

    file1 = open(args.input or "preprocessorfile_pointremoval.txt", "r")
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

    globaldata = cleanNeighbours(globaldata)

    wallpoints = getWallPointArray(globaldata[1:])

    print("Deleting Unneeded Wall Points (Except Left and Right Points)")
    globaldata = cleanWallPoints(globaldata)

    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 1:
            checkConditionNumber(idx, globaldata, 30)

    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 0:
            checkConditionNumberWall(idx, globaldata, 30)

    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 1:
            globaldata = fixXPosMain(idx, globaldata, 30, wallpoints, -1)
    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 1:
            globaldata = fixXNegMain(idx, globaldata, 30, wallpoints, -1)
    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 1:
            globaldata = fixYPosMain(idx, globaldata, 30, wallpoints, -1)
    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 1:
            globaldata = fixYNegMain(idx, globaldata, 30, wallpoints, -1)
            
    print("New")

    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 1:
            checkConditionNumber(idx, globaldata, 30)

    # print("Set Flag")

    # for idx,itm in enumerate(globaldata):
    #     if(idx > 0 and getFlag(idx,globaldata) == 1):
    #         globaldata = setFlags(idx,globaldata,60)

    globaldata = cleanNeighbours(globaldata)

    globaldata.pop(0)

    with open("preprocessorfile_rechecker.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")

    print("Data Converted")


if __name__ == "__main__":
    main()
