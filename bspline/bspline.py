import argparse
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
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core


def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    parser.add_argument("-b", "--bspline", nargs="+")
    parser.add_argument("-n", "--normal", nargs="?")
    parser.add_argument("-p", "--forcemidpointspline", nargs="?")
    parser.add_argument("-q", "--checkquadrant", nargs="?")
    parser.add_argument("-c", "--cache", nargs="?")
    parser.add_argument("-s", "--pseudocheck", nargs="?")
    parser.add_argument("-d", "--diagnose", nargs="?")
    args = parser.parse_args()
    np.seterr(divide='ignore')

    configData = config.getConfig()

    diagnose = False
    if args.diagnose:
        diagnose = core.str_to_bool(args.diagnose)

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

    pseudocheck = False
    if args.pseudocheck:
        pseudocheck = core.str_to_bool(args.pseudocheck)

    log.info("Loading Data")
    log.debug("Arguments")
    log.debug(args)
    if quadrantcheck == False:
        log.warn("Warning: Quadrant Check is disabled")
    
    if normalApproach == True:
        log.info("Info: Normal Bsplining is occuring with point control {}".format(configData['bspline']['pointControl']))
    else:
        log.info("Info: Mid Point BSplining is occuring with point control {}".format(configData['bspline']['pointControl']))

    if forcemidpointspline == True:
        log.warn("Warning: Mid Point BSpline has been forced. Point Control set to 3")
        if normalApproach:
            log.warn("Warning: Normal BSpline has been disabled")
        normalApproach = False

    if diagnose:
        log.info("Info: Diagnose has been enabled. No point will actually be saved.")

    if pseudocheck:
        log.info("Info: Pseudo Points are being checked and fixed.")
        log.info("Pseudo Distance is set to {}" .format(configData['bspline']['pseudoDist']))

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
        POINT_CONTROL = int(configData["bspline"]["pointControl"])
    else:
        POINT_CONTROL = 3

    globaldata = core.cleanNeighbours(globaldata)
    wallPts = core.getWallPointArray(globaldata)

    additionPts = []
    bsplineArray = []
    for itm in wallPts:
        bsplineData = np.array(core.undelimitXY(itm))
        bsplineArray.append(bsplineData)
    try:
        writingDict = dict(core.load_obj("wall"))
    except IOError:
        writingDict = {}
    log.info("Caching Wall Geometries")
    shapelyWallData = core.convertToShapely(wallPts)
    log.info("Searching for bad points")
    problempts,perpendicularpts, badpts = core.checkPoints(globaldata, args.bspline, normalApproach, configData, pseudocheck, shapelyWallData)
    log.info("Bsplining {} points".format(len(problempts)))
    log.info("Starting BSpline")
    for idx,itm in enumerate(tqdm(problempts)): 
        data = core.feederData(itm, wallPts)
        switch = False
        if configData["bspline"]["polygon"] == False:
            if configData["global"]["wallPointOrientation"] == "ccw":
                newpts = bsplinegen.generateBSplineBetween(bsplineArray[data[2]],data[0],data[1],POINT_CONTROL)
            else:
                # print(bsplineArray[data[2]][data[1]],bsplineArray[data[2]][data[0]])
                if data[0] == 0:
                    newpts = bsplinegen.generateBSplineBetween(bsplineArray[data[2]],data[1],data[0],POINT_CONTROL)
                    switch = True
                else:
                    newpts = bsplinegen.generateBSplineBetween(bsplineArray[data[2]],data[0],data[1],POINT_CONTROL)
            if quadrantcheck:
                newpts = bsplinegen.getPointsOnlyInQuadrant(newpts, badpts[idx], globaldata)
                if len(newpts) == 0:
                    if not pseudocheck:
                        log.error("Error: Quadrant Check failed. No point exist.")
                        log.error("Problem point is {}".format(badpts[idx]))
                        continue
                    else: 
                        log.warn("Warn: Quadrant Check failed. No point exists. Ignored since Pseudo Check is enabled.")
                        continue
            newpts = core.findNearestPoint(perpendicularpts[idx],newpts)
            print(newpts)
            if newpts == False:
                log.error("Error: Increase your Bspline Point Control Attribute")
                exit()
        else:
            newpts = list(perpendicularpts[idx])
        if switch:
            wallPtLocation = data[4]
        else:
            wallPtLocation = data[3]
        try:
            datum = list(writingDict[wallPtLocation])
            datum.append(newpts)
            writingDict[wallPtLocation] = datum
        except KeyError:
            writingDict[wallPtLocation] = [newpts]
        additionPts.append(newpts)
    if not diagnose:
        with open("adapted.txt", "a+") as text_file:
            text_file.writelines("1000 1000\n2000 2000\n")
            for item1 in additionPts:
                text_file.write("%s %s \n" % (item1[0], item1[1]))
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
