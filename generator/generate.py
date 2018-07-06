import argparse
from load import *
from boundary import *
from interior import *
from balance import *
from wall import *
from outer import *
from progress import *
from logger import *
import config
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--neighbour", const=str, nargs="?")
    parser.add_argument("-w", "--wall", nargs="+")
    args = parser.parse_args()
    log.info("Loading Data")
    log.debug("Arguments Set")
    log.debug(args)

    CONDITIONTHRESHOLD = 2000

    # Opening the Neighbourhood file
    try:
        file1 = open(args.neighbour or "neighbour.txt", "r")
        data = file1.read()
        file1.close()
    except Exception as error:
        log.critical(error)
        exit()
    data = data.replace("\t", " ")
    data = data.split("\n")
    data.pop(0)  # Pops the first blank line

    interiorPointsCount = 0
    outerPointsCount = 0

    wallarg = args.wall
    wallpoints = []
    hashtable = ["start"]
    globaldata = []

    log.info("Found " + str(len(wallarg)) + " wall geometry files.")
    for idx,itm in enumerate(wallarg):
        log.info("Loading Geometry " + str(itm))
        file2 = open(str(itm) or "airfoil_160.txt", "r")
        geometrydata = file2.read()
        file2.close()
        geometrydata = geometrydata.split("\n")
        hashtable, wallpointsdata, globaldata = loadWall(geometrydata,hashtable,globaldata,idx + 1)
        wallpoints.append(wallpointsdata)

    log.info("Loading Interior and Outer Points")
    hashtable, globaldata = loadInterior(data, hashtable, globaldata, len(hashtable))
    globaldata = cleanNeighbours(globaldata)
    hashtable, globaldata = detectOuter(hashtable, globaldata)

    globaldata = cleanNeighbours(globaldata)
    globaldata = generateReplacement(hashtable, globaldata)

    with open("preprocessorfile.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")

    log.info("Preprocessor File Generated")
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
