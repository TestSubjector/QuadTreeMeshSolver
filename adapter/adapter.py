import argparse
import re
from shapely.ops import triangulate, cascaded_union
from shapely.geometry import MultiPoint
from shapely.geometry import Polygon as Polygon2
import copy
from core import *
import numpy as np
import config
import bsplinegen
import itertools


def printProgressBar(
    iteration, total, prefix="", suffix="", decimals=1, length=100, fill="█"
):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print("\r%s |%s| %s%% %s" % (prefix, bar, percent, suffix), end="\r")
    if iteration == total:
        print()


def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    parser.add_argument("-a", "--adapt", const=str, nargs="?")
    args = parser.parse_args()

    print("Loading Data")

    file1 = open(args.input or "preprocessorfile_rechecker.txt", "r")
    data = file1.read()
    globaldata = ["start"]
    adaptdata = []
    adaptwall = []
    derefine = []
    splitdata = data.split("\n")
    splitdata = splitdata[:-1]
    outerpts = []
    interiorpts = []
    pseudopts = []
    globaldata_main = ["start"]

    silentRemove("pseudopoints.txt")

    for idx, itm in enumerate(splitdata):
        printProgressBar(
            idx, len(splitdata) - 1, prefix="Progress:", suffix="Complete", length=50
        )
        itm = itm.split(" ")
        itm.pop(-1)
        entry = itm
        globaldata.append(entry)

    wallPoints = adaptGetWallPointArray(globaldata)
    wallPointsFlatten = flattenList(wallPoints)
    

    # for idx, itm in enumerate(splitdata):
    #     printProgressBar(
    #         idx, len(splitdata) - 1, prefix="Progress:", suffix="Complete", length=50
    #     )
    #     itm = itm.split(" ")
    #     itm.pop(-1)
    #     entry = itm
    #     globaldata_main.append(entry)
    #     generalpts = []
    #     generalpts.extend(range(1,len(globaldata_main) + 1))

    # wallpts = adaptGetWallPointArray(globaldata_main)
    # for itm in wallpts:
    #     pseudopts.extend(nonAdaptWallPolygon(globaldata_main, itm, float(config.getConfig()["global"]["nonAdaptRegion"]), generalpts))

    # edgePts = tuple(config.getConfig()["global"]["edgePoints"])

    # pseudopts.extend(createEdgeCircle(globaldata_main,edgePts,config.getConfig()["global"]["nonAdaptEdgePointRadius"],generalpts))

    # print("Freeze Points",len(pseudopts))
    print("Processed Pre-Processor File")
    # print(len(pseudopts))
    # print(pseudopts)

    file2 = open(args.adapt or "sensor_flag.dat")
    data2 = file2.read()
    data2 = re.sub(" +", " ", data2)
    data2 = data2.split("\n")
    data2 = data2[:-1]
    if len(data2) + 1 != len(globaldata):
        print("Sensor File Length is not equal to Preprocessor File Length")
        exit()

    print("Reading Adaptation File")

    for idx2, itm2 in enumerate(data2):
        printProgressBar(
            idx2, len(data2) - 1, prefix="Progress:", suffix="Complete", length=50
        )
        adaptpoint = itm2.split(" ")
        adaptpoint.pop(0)
        if int(adaptpoint[1]) == 1:
            if int(idx2):
                xcord = globaldata[int(adaptpoint[0])][1]
                ycord = globaldata[int(adaptpoint[0])][2]
                xycord = str(xcord) + "," + str(ycord)
                if xycord not in wallPointsFlatten:
                    adaptdata.append([xcord, ycord])
                else:
                    adaptwall.append([xcord, ycord])
        elif int(adaptpoint[1]) == 2:
                xcord = globaldata[int(adaptpoint[0])][1]
                ycord = globaldata[int(adaptpoint[0])][2]
                derefine.append([xcord, ycord])

    print(len(adaptdata))
    print(len(adaptwall))
    print(len(derefine))

    perPndList = []

    print("Finding mini quadrants")

    for idax,itm in enumerate(adaptwall):
        printProgressBar(idax + 1, len(adaptwall), prefix="Progress:", suffix="Complete", length=50)
        idx = getIndexFromPoint(str(itm[0] + "," + str(itm[1])), globaldata)
        perList = getPerpendicularPointsFromQuadrants(idx,globaldata)
        for itm in perList:
            if quadrantContains(itm[1],itm[0]):
                perPndList.append(itm)
            else:
                print("Warning Quadrant Point Mismatch")
                print(itm)

    perPndList = list(set(perPndList))

    splineList = []

    for itm in perPndList:
        wallPointCord = itm[2]
        wallPointCurrent = getIndexFromPointTuple(wallPointCord, globaldata)
        leftRight = convertIndexToPoints(getLeftandRightPoint(wallPointCurrent,globaldata),globaldata)
        leftRight.insert(1,str(wallPointCord[0]) + "," + str(wallPointCord[1]))
        # print(leftRight)
        # nbhPts = findNearestNeighbourWallPointsManual(itm[0],globaldata,wallPointsFlatten,wallPoints)
        
        splineData = feederData(leftRight,wallPoints)
        print(itm)
        # print(splineData)
        splineList.append(splineData)

    try:
        writingDict = dict(load_obj("wall"))
    except IOError:
        writingDict = {}
    print(writingDict)
    print("Bsplining", len(perPndList), "points.")
    bsplineArray = []
    additionPts = []

    for itm in wallPoints:
        bsplineData = np.array(undelimitXY(itm))
        bsplineArray.append(bsplineData)
    print("Starting BSpline")
    for idx,itm in enumerate(perPndList): 
        data = splineList[idx]
        newpts = bsplinegen.generateBSplineBetween(bsplineArray[int(data[3])],data[0],data[1],int(config.getConfig()["bspline"]["pointControl"]))
        newpts = convertToSuperNicePoints(perPndList[idx],newpts)
        newpts = findNearestPoint(perPndList[idx][0],newpts)
        if newpts != False:
            if quadrantContains(perPndList[idx][1],newpts):
                None
            printProgressBar(idx + 1, len(perPndList), prefix="Progress:", suffix="Complete", length=50)
            try:
                writingDict[data[4]] = writingDict[data[4]] + [newpts]
            except KeyError:
                writingDict[data[4]] = [newpts]
            additionPts.append([newpts])
        else:
            data = splineList[idx]
            newpts = bsplinegen.generateBSplineBetween(bsplineArray[int(data[3])],data[1],data[2],int(config.getConfig()["bspline"]["pointControl"]))
            newpts = convertToSuperNicePoints(perPndList[idx],newpts)
            newpts = findNearestPoint(perPndList[idx][0],newpts)
            if newpts != False:
                if quadrantContains(perPndList[idx][1],newpts):
                    None
                printProgressBar(idx + 1, len(perPndList), prefix="Progress:", suffix="Complete", length=50)
                try:
                    writingDict[data[5]] = writingDict[data[5]] + [newpts]
                except KeyError:
                    writingDict[data[5]] = [newpts]
                additionPts.append([newpts])
    additionPts = list(itertools.chain.from_iterable(additionPts))
    save_obj(writingDict,"wall")

    print("Writing adapted text")

    with open("adapted.txt", "a+") as text_file:
        text_file.writelines("3000 3000\n")
        for item1 in derefine:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")
        text_file.writelines("3000 3000\n")
        text_file.writelines("1000 1000\n")
        for item1 in adaptdata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")
        text_file.writelines("1000 1000\n")
        text_file.writelines("2000 2000\n")
        for item1 in additionPts:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")
        text_file.writelines("1000 1000\n")
    print("Done")


if __name__ == "__main__":
    main()
