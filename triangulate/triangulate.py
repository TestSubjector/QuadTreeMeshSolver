import argparse
from progress import printProgressBar
from core import *
from connectivity import *
from balance import *
import temp
import logging
from shapely.geometry import MultiPoint
from shapely.ops import triangulate
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
import pyximport; pyximport.install(pyimport = True)

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    parser.add_argument("-a", "--algorithm", nargs="+")
    args = parser.parse_args()

    log.info("Loading Data")
    log.debug("Arguments")
    log.debug(args)

    globaldata = config.getKeyVal("globaldata")

    if globaldata == None:

        file1 = open(args.input or "preprocessorfile.txt", "r")
        data = file1.read()
        globaldata = ["start"]
        splitdata = data.split("\n")
        splitdata = splitdata[:-1]

        log.info("Processed Pre-Processor File")
        log.info("Converting to readable format")

        for idx, itm in enumerate(splitdata):
            printProgressBar(
                idx, len(splitdata) - 1, prefix="Progress:", suffix="Complete", length=50
            )
            itm = itm.split(" ")
            itm.pop(-1)
            entry = itm
            globaldata.append(entry)

    else:
        globaldata.insert(0,"start")

    globaldata = cleanNeighbours(globaldata)

    wallpts = getWallPointArray(globaldata)

    algo1,algo2,algo3 = True,True,True

    if len(args.algorithm) == 3:
        algo = list(map(str_to_bool,args.algorithm))
        algo1 = algo[0]
        algo2 = algo[1]
        algo3 = algo[2]

    # Removes Traces of Wall Points from the last wallpoint neighbours

    lastWallPoints = getWallEndPoints(globaldata)
    globaldata = cleanWallPointsSelectivity(globaldata, lastWallPoints)

    log.info("Generating Wall Polygons for Aerochecks")
    wallpts = generateWallPolygons(wallpts)
    log.info("Detected " + str(len(wallpts)) + " geometry(s).")
    log.info("Wall Polygon Generation Complete")
    print("Deleting Unneeded Wall Points (Except Left and Right Points)")
    globaldata = cleanWallPoints(globaldata)
    badPoints = []

    if algo1 == True:

        log.info("Triangulating")

        interiorpts = []
        interiorpts.extend(range(1, len(globaldata)))
        interiorpts = convertPointToShapelyPoint(convertIndexToPoints(interiorpts,globaldata))
        interiorpts = MultiPoint(interiorpts)
        interiortriangles = triangulate(interiorpts)

        log.info("Generated " + str(len(interiortriangles)) + " triangle(s).")
        polydata = getPolygon(interiortriangles)
        log.info("Running Connectivity Check")
        globaldata,badPoints = connectivityCheck(globaldata,badPoints)
        log.info("Connectivity Check Done")
        log.info("Running Triangulation Balancing using Nischay's Triangle Neighbours")
        globaldata = triangleBalance(globaldata,polydata,wallpts)
        log.info("Triangle Balancing Done")
    if algo2 == True:
        log.info("Running Connectivity Check")
        globaldata,badPoints = connectivityCheck(globaldata,badPoints)
        log.info("Connectivity Recheck Done")
        log.info("Running Triangulation Balancing using Kumar's Neighbours (Left and Right Mode)")
        globaldata = triangleBalance2(globaldata,wallpts)
    if algo3 == True:
        log.info("Running Connectivity Check")
        globaldata,badPoints = connectivityCheck(globaldata,badPoints)
        log.info("Running Triangulation Balancing using Kumar's Neighbours (General)")
        globaldata = triangleBalance3(globaldata,wallpts)
    log.info("Running Connectivity Recheck")
    globaldata,badPoints = connectivityCheck(globaldata,badPoints)
    log.info("Writing Deletion Points")
    problempts = findDeletionPoints(globaldata)
    
    globaldata = cleanNeighbours(globaldata)

    temp.writeConditionValuesForWall(globaldata)

    globaldata.pop(0)

    config.setKeyVal("globaldata",globaldata)

    with open("removal_points.txt", "w") as text_file:
        for item1 in problempts:
            text_file.writelines(["%s " % item1])
            text_file.writelines("\n")

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