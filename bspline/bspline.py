import argparse
import copy
import logging
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
    parser.add_argument("-d", "--dry-run", nargs="?")
    args = parser.parse_args()
    np.seterr(divide='ignore')

    configData = core.getConfig()

    dryRun = False
    if args.dry_run:
        dryRun = core.ConvertStringToBool(args.dry_run)

    normalApproach = False
    if args.normal:
        normalApproach = core.ConvertStringToBool(args.normal)

    cache = True
    if args.cache:
        cache = core.ConvertStringToBool(args.cache)

    forcemidpointspline = False
    if args.forcemidpointspline:
        forcemidpointspline = core.ConvertStringToBool(args.forcemidpointspline)

    quadrantcheck = True
    if args.checkquadrant:
        quadrantcheck = core.ConvertStringToBool(args.checkquadrant)

    pseudocheck = False
    if args.pseudocheck:
        pseudocheck = core.ConvertStringToBool(args.pseudocheck)

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

    if dryRun:
        log.info("Info: Dry Run has been enabled. No point will actually be saved.")

    if pseudocheck:
        log.info("Info: Pseudo Points are being checked and fixed.")
        log.info("Pseudo Distance is set to {}" .format(configData['bspline']['pseudoDist']))

    if configData["bspline"]["polygon"] == True:
        log.info("Info: Polygon Mode has been enabled. Bspline will be disabled.")

    if cache:
        globaldata = core.getKeyVal("globaldata")
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
                if data[0] == 1 and data[1] == 0:
                    newpts = core.generateBSplineBetween(bsplineArray[data[2]],data[1],data[0],POINT_CONTROL)
                    switch = True
                else:
                    newpts = core.generateBSplineBetween(bsplineArray[data[2]],data[0],data[1],POINT_CONTROL)
            else:
                switch = True
                if data[1] == 0 and data[0] == 1:
                    newpts = core.generateBSplineBetween(bsplineArray[data[2]],data[1],data[0],POINT_CONTROL)
                    switch = True
                elif data[1] == 0 and data[0] != 1:
                    newpts = core.generateBSplineBetween(bsplineArray[data[2]],data[0],data[1],POINT_CONTROL)
                    switch = False
                elif data[0] == 0 and data[1] != 1:
                    newpts = core.generateBSplineBetween(bsplineArray[data[2]],data[1],data[0],POINT_CONTROL)
                    switch = True
                else:
                    newpts = core.generateBSplineBetween(bsplineArray[data[2]],data[0],data[1],POINT_CONTROL)
                    switch = False
            if quadrantcheck:
                newpts = core.getPointsOnlyInQuadrant(newpts, badpts[idx], globaldata)
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
            if configData["global"]["wallPointOrientation"] == "ccw":
                if data[0] == 1 and data[1] == 0:
                    switch = True
                else:
                    switch = False
            else:
                switch = True
                if data[1] == 0 and data[0] == 1:
                    switch = True
                elif data[1] == 0 and data[0] != 1:
                    switch = False
                elif data[0] == 0 and data[1] != 1:
                    switch = True
                else:
                    switch = False
            if quadrantcheck:
                newpts = core.getPointsOnlyInQuadrant([newpts], badpts[idx], globaldata)
                if len(newpts) == 0:
                    if not pseudocheck:
                        log.error("Error: Quadrant Check failed. No point exist.")
                        log.error("Problem point is {}".format(badpts[idx]))
                        continue
                    else: 
                        log.warn("Warn: Quadrant Check failed. No point exists. Ignored since Pseudo Check is enabled.")
                        continue
                newpts = list(newpts[0])
            print(newpts)
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
    if not dryRun:
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
