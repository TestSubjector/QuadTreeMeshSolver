import argparse
import sys
sys.path.append('../')
import core
import copy
import logging
import bsplinegen
import config
import numpy as np
import math
import itertools
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
from tqdm import tqdm

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    parser.add_argument("-b", "--bspline", nargs="+")
    parser.add_argument("-n", "--normal", nargs="?")
    parser.add_argument("-m", "--midpointspline", nargs="+")
    parser.add_argument("-p", "--forcemidpointspline", nargs="?")
    parser.add_argument("-q", "--checkquadrant", nargs="?")
    parser.add_argument("-c", "--cache", nargs="?")
    args = parser.parse_args()

    normalApproach = False
    if args.normal:
        normalApproach = core.str_to_bool(args.normal)

    cache = True
    if args.cache:
        cache = core.str_to_bool(args.cache)

    forcemidpointspline = False
    if args.forcemidpointspline:
        forcemidpointspline = core.str_to_bool(args.forcemidpointspline)

    quadrantcheck = True
    if args.checkquadrant:
        quadrantcheck = core.str_to_bool(args.checkquadrant)

    log.info("Loading Data")
    log.debug("Arguments")
    log.debug(args)
    if quadrantcheck == False:
        log.warn("Warning: Quadrant Check is disabled")
    
    if normalApproach == True:
        log.info("Info: Normal Bsplining is occuring")

    if forcemidpointspline == True:
        log.warn("Warning: Mid Point BSpline has been forced. Point Control set to 3")
        if normalApproach:
            log.warn("Warning: Normal BSpline has been disabled")
        normalApproach = False

    if cache:
        globaldata = config.getKeyVal("globaldata")
    else:
        globaldata = None

    if globaldata == None:

        file1 = open(args.input or "preprocessorfile_bspline.txt", "r")
        data = file1.read()
        globaldata = ["start"]
        splitdata = data.split("\n")
        splitdata = splitdata[:-1]

        log.info("Processed Pre-Processor File")
        log.info("Converting to readable format")

        for idx, itm in enumerate(tqdm(splitdata)):
            itm = itm.split(" ")
            itm.pop(-1)
            entry = itm
            globaldata.append(entry)

    else:
        globaldata.insert(0,"start")

    if not forcemidpointspline:
        POINT_CONTROL = int(config.getConfig()["bspline"]["pointControl"])
    else:
        POINT_CONTROL = 3

    globaldata = core.cleanNeighbours(globaldata)
    wallPts = core.getWallPointArray(globaldata)

    additionPts = []
    bsplineArray = []
    for itm in wallPts:
        bsplineData = np.array(core.undelimitXY(itm))
        bsplineArray.append(bsplineData)


    if args.midpointspline:
        log.info("Mid point bspling for {}".format(len(args.midpointspline)))
        midspline = list(map(int,args.midpointspline))
        # midspline[:] = [x - 1 for x in midspline]
        POINT_CONTROL = 3
    try:
        writingDict = dict(core.load_obj("wall"))
    except IOError:
        writingDict = {}
    # print(writingDict)
    if not args.midpointspline:
        problempts,perpendicularpts = core.checkPoints(globaldata,args.bspline,normalApproach)
        log.info("Bsplining {} points".format(len(problempts)))
        log.info("Starting BSpline")
        for idx,itm in enumerate(tqdm(problempts)): 
            data = core.feederData(itm,wallPts)
            if config.getConfig()["bspline"]["polygon"] == False:
                if config.getConfig()["global"]["wallPointOrientation"] == "ccw":
                    newpts = bsplinegen.generateBSplineBetween(bsplineArray[data[2]],data[0],data[1],POINT_CONTROL)
                else:
                    if data[0] == 1:
                        newpts = bsplinegen.generateBSplineBetween(bsplineArray[data[2]],data[1],data[0],POINT_CONTROL)
                    else:
                        newpts = bsplinegen.generateBSplineBetween(bsplineArray[data[2]],data[0],data[1],POINT_CONTROL)
                if quadrantcheck:
                    newpts = bsplinegen.getPointsOnlyInQuadrant(newpts,bsplineArray[data[2]][int(data[0])],bsplineArray[data[2]][int(data[1])],globaldata)
                newpts = core.findNearestPoint(perpendicularpts[idx],newpts)
                if newpts == False:
                    log.error("Error: Increase your Bspline Point Control Attribute")
                    exit()
            else:
                newpts = list(perpendicularpts[idx])
            try:
                writingDict[data[3]] = writingDict[data[3]] + [newpts]
            except KeyError:
                writingDict[data[3]] = [newpts]
            additionPts.append([newpts])
    else:
        for idx,itm in enumerate(tqdm(midspline)):
            wallData = core.getWallGeometry(bsplineArray, globaldata, itm)
            itmx, itmy = core.getPoint(itm, globaldata)
            pos = np.array(wallData).tolist().index([itmx, itmy])
            if pos == len(wallData) - 1:
                nextPt = 0
            else:
                nextPt = pos + 1
            if config.getConfig()["global"]["wallPointOrientation"] == "ccw":
                newpts = bsplinegen.generateBSplineBetween(wallData,pos, nextPt ,POINT_CONTROL)
            else:
                if itm == 1:
                    newpts = bsplinegen.generateBSplineBetween(wallData,nextPt,pos,POINT_CONTROL)
                else:
                    newpts = bsplinegen.generateBSplineBetween(wallData,pos,nextPt,POINT_CONTROL)
            itmxy = core.getPointxy(itm, globaldata)
            newpts = newpts[0]
            try:
                writingDict[itmxy] = writingDict[itmxy] + [newpts]
            except KeyError:
                writingDict[itmxy] = [newpts]
            additionPts.append([newpts])
        additionPts = list(itertools.chain.from_iterable(additionPts))
    with open("adapted.txt", "a+") as text_file:
        text_file.writelines("1000 1000\n2000 2000\n")
        for item1 in additionPts:
            text_file.writelines(["%s %s " % (item[0], item[1]) for item in item1])
            text_file.writelines("\n")
        text_file.writelines("1000 1000\n")
    core.save_obj(writingDict,"wall")
    
if __name__ == "__main__":
    import logging
    import os
    import json
    import logging.config
    import config

    default_path='logging.json'
    path = default_path
    level = config.getConfig()["global"]["logger"]["level"]

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
        logging.basicConfig(level=level,filename=config.getConfig()["global"]["logger"]["logPath"],format="%(asctime)s %(name)s %(levelname)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
    main()
