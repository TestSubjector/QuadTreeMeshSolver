from shapely.ops import triangulate, cascaded_union
from shapely.geometry import MultiPoint
from shapely.geometry import Polygon as Polygon2
import argparse
from progress import printProgressBar
import copy
import numpy as np

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
import pyximport; pyximport.install(pyimport = True)
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import *


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

    silentRemove("removal_points.txt")

    for idx, itm in enumerate(splitdata):
        printProgressBar(
            idx, len(splitdata) - 1, prefix="Progress:", suffix="Complete", length=50
        )
        itm = itm.split(" ")
        itm.pop(-1)
        entry = itm
        globaldata.append(entry)

    globaldata = cleanNeighbours(globaldata)

    outerpts = []
    interiorpts = []

    log.info("Point Classification")

    for idx, itm in enumerate(globaldata):
        printProgressBar(
            idx, len(globaldata) - 1, prefix="Progress:", suffix="Complete", length=50
        )
        if idx > 0 and getFlag(idx, globaldata) == 2:
            outerpts.append(idx)
        elif idx > 0 and getFlag(idx, globaldata) == 1:
            interiorpts.append(idx)

    wallpts = getWallPointArray(globaldata)
    for itm in wallpts:
        inflatedWallPolygon(globaldata, itm, float(core.getConfig()["pseudowall"]["inflatedPolygonDistance"]), interiorpts)
    # print("Triangulating")

    # interiorpts = convertPointToShapelyPoint(convertIndexToPoints(interiorpts,globaldata))
    # interiorpts = MultiPoint(interiorpts)
    # interiortriangles = triangulate(interiorpts)

    # wallpts = convertPointToShapelyPoint(convertIndexToPoints(wallpts,globaldata))
    # wallpts = Polygon2(wallpts)

    # print("Generating Model")
    # polygns = []
    # fig, ax = plt.subplots()
    # for idx,itm in enumerate(interiortriangles):
    #     printProgressBar(idx, len(interiortriangles) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #     itm = itm.difference(wallpts)
    #     try:
    #         theshit = list(zip(*itm.exterior.xy))
    #         polygns.append(Polygon(theshit, True))
    #     except AttributeError:
    #         pass
    # p = PatchCollection(polygns, cmap=matplotlib.cm.jet, alpha=0.4)
    # colors = 100*np.random.rand(len(polygns))
    # p.set_array(np.array(colors))
    # ax.add_collection(p)
    # print("Plotting")
    # plt.show()
    # xs, ys = [],[]
    # mergedtriangles = cascaded_union(outertriangles)
    # for triangle in outertriangles:
    #     xstemp,ystemp = triangle.exterior.xy
    #     print(xstemp,ystemp)
    # xs,ys = mergedtriangles.exterior.xy
    # fig, axs = plt.subplots()
    # axs.fill(xs, ys, alpha=0.5, fc='r', ec='none')
    # plt.show() #if not interactive.

    # print("Set Flag")

    # for idx,itm in enumerate(globaldata):
    #     if(idx > 0 and getFlag(idx,globaldata) == 1):
    #         globaldata = setFlags(idx,globaldata,60)

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
