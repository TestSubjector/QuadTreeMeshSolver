import argparse
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
from matplotlib import pyplot as plt
from shapely.geometry.polygon import LinearRing, Polygon
from tqdm import tqdm, trange
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()

    log.info("Loading Data")

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
        globaldata.append(entry)

    globaldata = core.cleanNeighbours(globaldata)
    wallpoints = core.getWallPointArray(globaldata)
    wallpointsData = core.generateWallPolygons(wallpoints)
    print(len(wallpointsData))
    x,y = wallpointsData[0].exterior.xy
    fig, axs = plt.subplots()
    axs.fill(x, y, alpha=0.5, fc='r', ec='none')
    plt.show() #if not interactive.

    log.info("Running Non Aero Checks")

    for idx in trange(1,len(globaldata)):  
        nbhs = core.getNeighbours(idx,globaldata)
        for itm in nbhs:
            cord = core.getPointxy(itm,globaldata)
            if core.isNonAeroDynamic(idx,cord,globaldata,wallpointsData):
                log.warning("Point %s has a non aero point with index %s",idx,itm)

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