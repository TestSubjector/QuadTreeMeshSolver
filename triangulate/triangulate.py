import argparse
import balance
import logging
from shapely.geometry import MultiPoint
from shapely.ops import triangulate
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
from tqdm import tqdm
import sys, os
import numpy as np

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    parser.add_argument("-a", "--algorithm", nargs="+")
    args = parser.parse_args()

    log.info("Loading Data")
    log.debug("Arguments")
    log.debug(args)
    configData = core.getConfig()

    globaldata = core.getKeyVal("globaldata")
    hashtable = {}

    if globaldata == None:

        file1 = open(args.input or "preprocessorfile.txt", "r")
        data = file1.read()
        globaldata = ["start"]
        splitdata = data.split("\n")
        splitdata = splitdata[:-1]

        log.info("Processed Pre-Processor File")
        log.info("Converting to readable format")

        for _, itm in enumerate(tqdm(splitdata)):
            itm = itm.split(" ")
            itm.pop(-1)
            entry = itm
            hashtable["{},{}".format(entry[1], entry[2])] = int(entry[0])
            globaldata.append(entry)

    else:
        globaldata.insert(0,"start")
        hashtable = core.generateHashtable(globaldata)

    # globaldata = core.cleanNeighbours(globaldata)

    wallpts = core.getWallPointArray(globaldata)

    algo1,algo2,algo3 = True,True,True

    if len(args.algorithm) == 3:
        algo = list(map(core.ConvertStringToBool,args.algorithm))
        algo1 = algo[0]
        algo2 = algo[1]
        algo3 = algo[2]

    log.info("Generating Wall Polygons for Aerochecks")
    wallpts = core.generateWallPolygons(wallpts)
    log.info("Detected " + str(len(wallpts)) + " geometry(s).")
    log.info("Wall Polygon Generation Complete")
    log.info("Deleting Unneeded Wall Points (Except Left and Right Points)")

    globaldata = core.cleanWallPoints(globaldata)
    badPoints = []

    with np.errstate(divide='ignore', invalid='ignore'):
        if algo1 == True:
            log.info("Triangulating")
            interiorpts = []
            interiorpts.extend(range(1, len(globaldata)))
            interiorpts = core.convertPointToShapelyPoint(core.convertIndexToPoints(interiorpts,globaldata))
            interiorpts = MultiPoint(interiorpts)
            interiortriangles = triangulate(interiorpts)
            log.info("Generated " + str(len(interiortriangles)) + " triangle(s).")
            polydata = balance.getPolygon(interiortriangles)
            log.info("Running Connectivity Check")
            globaldata,badPoints = core.connectivityCheck(globaldata, badPoints, configData, quick=True)
            log.info("Connectivity Check Done")
            log.info("Running Triangulation Balancing using Nischay's Triangle Neighbours")
            globaldata = balance.triangleBalance(globaldata, polydata, wallpts, configData, badPoints)
            log.info("Triangle Balancing Done")
        if algo2 == True:
            log.info("Running Connectivity Check")
            globaldata,badPoints = core.connectivityCheck(globaldata, badPoints, configData, quick=True)
            log.info("Connectivity Recheck Done")
            log.info("Running Triangulation Balancing using Kumar's Neighbours (Left and Right Mode)")
            globaldata = balance.triangleBalance2(globaldata, wallpts, configData, badPoints, hashtable)
        if algo3 == True:
            log.info("Running Connectivity Check")
            globaldata,badPoints = core.connectivityCheck(globaldata, badPoints, configData, quick=True)
            log.info("Running Triangulation Balancing using Kumar's Neighbours (General)")
            globaldata = balance.triangleBalance3(globaldata, wallpts, configData, badPoints, hashtable)
        log.info("Running Connectivity Recheck")
        globaldata,badPoints = core.connectivityCheck(globaldata, badPoints, configData, quick=True)
    log.warning("Total Number of Points unable to be fixed: {}".format(len(badPoints)))
    # log.info("Writing Deletion Points")
    # problempts = findDeletionPoints(globaldata)
    
    # globaldata = core.cleanNeighbours(globaldata)

    # core.writeConditionValuesForWall(globaldata, configData)

    globaldata.pop(0)

    core.setKeyVal("globaldata",globaldata)

    # with open("removal_points.txt", "w") as text_file:
    #     for item1 in problempts:
    #         text_file.writelines(["%s " % item1])
    #         text_file.writelines("\n")

    log.info("Writing Preprocessor File")

    with open("preprocessorfile_triangulate.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")
    log.info("Done")

if __name__ == "__main__":
    import logging
    import os
    import json
    import logging.config
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    from core import core
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
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