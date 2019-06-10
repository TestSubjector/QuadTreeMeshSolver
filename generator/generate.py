import argparse
from load import *
from boundary import *

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--neighbour", const=str, nargs="?")
    parser.add_argument("-w", "--wall", nargs="+")
    args = parser.parse_args()
    log.info("Loading Data")
    log.debug("Arguments Set")
    log.debug(args)

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

    # if not args.neighbour:
    #     log.critical("Cannot find neighbor file")
    #     exit()

    core.setPrefix()

    wallarg = args.wall
    wallpoints = []
    hashtable = ["start"]
    globaldata = []

    log.info("Found " + str(len(wallarg)) + " wall geometry files.")
    try:
        bsplineWallData = dict(load_obj("wall"))
    except IOError:
        bsplineWallData = "None"
    for idx,itm in enumerate(wallarg):
        log.info("Loading Geometry " + str(itm))
        file2 = open(str(itm) or "airfoil_160.txt", "r")
        geometrydata = file2.read()
        file2.close()
        geometrydata = geometrydata.split("\n")
        geometrydataOrg = wallFloat(geometrydata)
        # print(geometrydata)
        if bsplineWallData != "None":
            insertionKeys = list(bsplineWallData.keys())
            for itm in insertionKeys:
                postInsert = True
                itm2 = itm
                if "pre" in itm2:
                    itm2 = itm2.replace("pre","")
                    postInsert = False
                itmx = float(itm2.split(",")[0])
                itmy = float(itm2.split(",")[1])
                itmCheck = str(itmx) +"\t" + str(itmy)
                resultMan,insertionidx = checkIfInside(itmx,itmy,geometrydata,geometrydataOrg,bsplineWallData)
                if resultMan:
                    ptsToBeAdded = getItem(bsplineWallData,itm)
                    ptsToBeAdded = sorted(ptsToBeAdded,key = lambda point: distance_squared(itmx,itmy,point[0],point[1]),reverse=postInsert)
                    for ptCordItm in ptsToBeAdded:
                        dataInsert = str(ptCordItm[0]) + "\t" + str(ptCordItm[1])
                        if postInsert == True:
                            geometrydata.insert(insertionidx + 1,dataInsert)
                        else:
                            geometrydata.insert(insertionidx,dataInsert)
        hashtable, wallpointsdata, globaldata = loadWall(geometrydata,hashtable,globaldata,idx + 1)
        wallpoints.append(wallpointsdata)

    log.info("Loading Interior and Outer Points")
    hashtable, globaldata = loadInterior(data, hashtable, globaldata, len(hashtable))
    globaldata = cleanNeighbours(globaldata)
    hashtable, globaldata = detectOuter(hashtable, globaldata)

    globaldata = cleanNeighbours(globaldata)
    globaldata = generateReplacement(hashtable, globaldata)

    core.setKeyVal("globaldata",globaldata)

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
