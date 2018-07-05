import argparse
from progress import printProgressBar
from core import *
from connectivity import *
from balance import *
import temp
import logging
from shapely.geometry import MultiPoint
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()

    log.info("Loading Data")
    log.debug("Arguments")
    log.debug(args)

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

    globaldata = cleanNeighbours(globaldata)

    wallpts = getWallPointArray(globaldata)

    log.info("Triangulating")

    interiorpts = []
    interiorpts.extend(range(1, len(globaldata)))
    interiorpts = convertPointToShapelyPoint(convertIndexToPoints(interiorpts,globaldata))
    interiorpts = MultiPoint(interiorpts)
    interiortriangles = triangulate(interiorpts)

    # Removes Traces of Wall Points from the last wallpoint neighbours

    lastWallPoints = getWallEndPoints(globaldata)
    globaldata = cleanWallPointsSelectivity(globaldata, lastWallPoints)

    # temp.writeNormalsToText(globaldata)

    log.info("Detected " + str(len(wallpts)) + " geometry(s).")
    log.info("Generated " + str(len(interiortriangles)) + " triangle(s).")
    polydata = getPolygon(interiortriangles)
    log.info("Generating Wall Polygons for Aerochecks")
    wallpts = generateWallPolygons(wallpts)
    log.info("Wall Polygon Generation Complete")
    log.info("Running Connectivity Check")
    globaldata = connectivityCheck(globaldata)
    log.info("Connectivity Check Done")
    log.info("Running Triangulation Balancing using Nischay's Triangle Neighbours")
    globaldata = triangleBalance(globaldata,polydata,wallpts)
    log.info("Triangle Balancing Done")
    log.info("Running Connectivity Recheck")
    globaldata = connectivityCheck(globaldata)
    log.info("Connectivity Recheck Done")
    log.info("Running Triangulation Balancing using Kumar's Neighbours (Left and Right Mode)")
    globaldata = triangleBalance2(globaldata,polydata,wallpts)
    log.info("Running Connectivity Recheck")
    globaldata = connectivityCheck(globaldata)
    log.info("Running Triangulation Balancing using Kumar's Neighbours (General)")
    globaldata = triangleBalance3(globaldata,polydata,wallpts)
    log.info("Running Connectivity Recheck")
    globaldata = connectivityCheck(globaldata)
    log.info("Writing Deletion Points")
    problempts = findDeletionPoints(globaldata)
    
    globaldata = cleanNeighbours(globaldata)

    temp.writeConditionValuesForWall(globaldata)

    globaldata.pop(0)

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