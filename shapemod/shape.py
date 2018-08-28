import argparse
from load import *
import config
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
import pyximport; pyximport.install(pyimport = True)

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--wall", nargs="+")
    args = parser.parse_args()
    log.info("Loading Data")
    log.debug("Arguments Set")
    log.debug(args)

    wallarg = args.wall
    wallpoints = []
    
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

        if bsplineWallData != "None":
            insertionKeys = list(bsplineWallData.keys())
            for itm in insertionKeys:
                itmx = float(itm.split(",")[0])
                itmy = float(itm.split(",")[1])
                itmCheck = str(itmx) +"\t" + str(itmy)
                resultMan,insertionidx = checkIfInside(itmx,itmy,geometrydata,geometrydataOrg,bsplineWallData)
                if resultMan:
                    ptsToBeAdded = getItem(bsplineWallData,itm)
                    ptsToBeAdded = sorted(ptsToBeAdded,key = lambda point: distance_squared(itmx,itmy,point[0],point[1]),reverse=True)
                    for ptCordItm in ptsToBeAdded:
                        dataInsert = str(ptCordItm[0]) + "\t" + str(ptCordItm[1])
                        geometrydata.insert(insertionidx + 1,dataInsert)
        wallpointsdata = loadWall(geometrydata)
        wallpoints.append(wallpointsdata)
    
    for idx,wallptarr in enumerate(wallpoints):
        wallptarr.append(wallptarr[0])
        wallpoints[idx] = wallptarr

    with open("shape_generated.txt", "w") as text_file:
        for item1 in wallpoints:
            text_file.writelines("0 0\n")
            for itm in item1:
                text_file.writelines(str(itm.split(",")[0]) + "\t" + str(itm.split(",")[1]))
                text_file.writelines("\n")
        text_file.writelines("0 0")

    log.info("Shape File Generated")
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
