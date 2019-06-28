import argparse
import re
from shapely.ops import triangulate, cascaded_union
from shapely.geometry import MultiPoint
from shapely.geometry import Polygon as Polygon2
import copy
import numpy as np
import itertools
from tqdm import tqdm
import sys
import os
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    parser.add_argument("-a", "--adapt", const=str, nargs="?")
    args = parser.parse_args()

    log.info("Loading Data")

    file1 = open(args.input or "preprocessorfile_rechecker.txt", "r")
    data = file1.read()
    globaldata = ["start"]
    adaptdata = []
    adaptwall = []
    derefine = []
    splitdata = data.split("\n")
    splitdata = splitdata[:-1]

    core.silentRemove("pseudopoints.txt")

    configData = core.getConfig()

    for idx, itm in enumerate(tqdm(splitdata)):
        itm = itm.split(" ")
        itm.pop(-1)
        entry = itm
        globaldata.append(entry)

    wallPoints = core.adaptGetWallPointArray(globaldata)
    wallPointsFlatten = core.flattenList(wallPoints)
    

    # for idx, itm in enumerate(splitdata):
    #     itm = itm.split(" ")
    #     itm.pop(-1)
    #     entry = itm
    #     globaldata_main.append(entry)
    #     generalpts = []
    #     generalpts.extend(range(1,len(globaldata_main) + 1))

    # wallpts = adaptGetWallPointArray(globaldata_main)
    # for itm in wallpts:
    #     pseudopts.extend(nonAdaptWallPolygon(globaldata_main, itm, float(configData["global"]["nonAdaptRegion"]), generalpts))

    # edgePts = tuple(configData["global"]["edgePoints"])

    # pseudopts.extend(createEdgeCircle(globaldata_main,edgePts,configData["global"]["nonAdaptEdgePointRadius"],generalpts))

    # print("Freeze Points",len(pseudopts))
    log.info("Processed Pre-Processor File")
    # print(len(pseudopts))
    # print(pseudopts)

    file2 = open(args.adapt or "sensor_flag.dat")
    data2 = file2.read()
    data2 = re.sub(" +", " ", data2)
    data2 = data2.split("\n")
    data2 = data2[:-1]
    if len(data2) + 1 != len(globaldata):
        log.error("Sensor File Length is not equal to Preprocessor File Length")
        exit()

    log.info("Reading Adaptation File")

    for idx2, itm2 in enumerate(tqdm(data2)):
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
                    wallidx = core.getIndexFromPoint(xycord,globaldata)
                    walldepth = core.getDepth(wallidx,globaldata)
                    WALL_LIMIT = int(configData["adapter"]["minWallAdaptDepth"])
                    if walldepth >= WALL_LIMIT:
                        adaptwall.append([xcord, ycord])
                    else:
                        adaptdata.append([xcord, ycord])
        elif int(adaptpoint[1]) == 2:
                xcord = globaldata[int(adaptpoint[0])][1]
                ycord = globaldata[int(adaptpoint[0])][2]
                derefine.append([xcord, ycord])

    log.info("Interior Points being adapted: {}".format(len(adaptdata)))
    log.info("Wall Points being adapted: {}".format(len(adaptwall)))
    log.info("Points being derefined: {}".format(len(derefine)))

    # perPndList = []

    # print("Finding mini quadrants")

    # for idax,itm in enumerate(tqdm(adaptwall)):
    #     idx = core.getIndexFromPoint(str(itm[0] + "," + str(itm[1])), globaldata)
    #     perList = core.getPerpendicularPointsFromQuadrants(idx,globaldata)
    #     for itm in perList:
    #         if core.quadrantContains(itm[1],itm[0]):
    #             perPndList.append(itm)
    #         else:
    #             print("Warning Quadrant Point Mismatch")
    #             print(itm)

    # perPndList = list(set(perPndList))

    # splineList = []

    # for itm in perPndList:
    #     wallPointCord = itm[2]
    #     wallPointCurrent = core.getIndexFromPointTuple(wallPointCord, globaldata)
    #     leftRight = core.convertIndexToPoints(core.getLeftandRightPointIndex(wallPointCurrent,globaldata),globaldata)
    #     leftRight.insert(1,str(wallPointCord[0]) + "," + str(wallPointCord[1]))
    #     # print(leftRight)
    #     # nbhPts = findNearestNeighbourWallPointsManual(itm[0],globaldata,wallPointsFlatten,wallPoints)
        
    #     splineData = core.feederData(leftRight,wallPoints)
    #     print(itm)
    #     # print(splineData)
    #     splineList.append(splineData)

    # try:
    #     writingDict = dict(core.load_obj("wall"))
    # except IOError:
    #     writingDict = {}
    # # print(writingDict)
    # print("Bsplining", len(perPndList), "points.")
    # bsplineArray = []
    # additionPts = []

    # for itm in wallPoints:
    #     bsplineData = np.array(core.undelimitXY(itm))
    #     bsplineArray.append(bsplineData)
    # print("Starting BSpline")
    # for idx,itm in enumerate(tqdm(perPndList)): 
    #     data = splineList[idx]
    #     newpts = core.generateBSplineBetween(bsplineArray[int(data[3])],data[0],data[1],int(configData["bspline"]["pointControl"]))
    #     newpts = core.convertToSuperNicePoints(perPndList[idx],newpts)
    #     newpts = core.findNearestPoint(perPndList[idx][0],newpts)
    #     if newpts != False:
    #         if core.quadrantContains(perPndList[idx][1],newpts):
    #             None
    #         try:
    #             writingDict[data[4]] = writingDict[data[4]] + [newpts]
    #         except KeyError:
    #             writingDict[data[4]] = [newpts]
    #         additionPts.append([newpts])
    #     else:
    #         data = splineList[idx]
    #         newpts = core.generateBSplineBetween(bsplineArray[int(data[3])],data[1],data[2],int(configData["bspline"]["pointControl"]))
    #         newpts = core.convertToSuperNicePoints(perPndList[idx],newpts)
    #         newpts = core.findNearestPoint(perPndList[idx][0],newpts)
    #         if newpts != False:
    #             if core.quadrantContains(perPndList[idx][1],newpts):
    #                 None
    #             try:
    #                 writingDict[data[5]] = writingDict[data[5]] + [newpts]
    #             except KeyError:
    #                 writingDict[data[5]] = [newpts]
    #             additionPts.append([newpts])
    # additionPts = list(itertools.chain.from_iterable(additionPts))
    # core.save_obj(writingDict,"wall")

    log.info("Writing adapted text")

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
        for item1 in adaptwall:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")
        text_file.writelines("1000 1000\n")
        # text_file.writelines("2000 2000\n")
        # for item1 in additionPts:
        #     text_file.writelines(["%s " % item for item in item1])
        #     text_file.writelines("\n")
        # text_file.writelines("1000 1000\n")
    log.info("Done")


    
if __name__ == "__main__":
    import logging
    import os
    import json
    import logging.config
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    from core import core

    default_path='logging.json'
    path = default_path
    level = core.getConfig()["global"]["logger"]["level"]

    if level == "DEBUG":
        level = logging.DEBUG
    elif level == "INFO":
        level = logging.INFO
    elif level == "WARNING":
        level = logging.WARNING
    elif level == "ERROR":
        level = logging.ERROR
    else:
        level = logging.WARNING

    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=level,filename=core.getConfig()["global"]["logger"]["logPath"],format="%(asctime)s %(name)s %(levelname)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
    main()