import argparse
from progress import printProgressBar
import core
import copy
import logging
import bsplinegen
import config
import numpy as np
import math
import itertools
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
import pyximport; pyximport.install(pyimport = True)


def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    parser.add_argument("-b", "--bspline", nargs="+")
    parser.add_argument("-n", "--normal", nargs="?")
    args = parser.parse_args()

    normalApproach = False
    if args.normal:
        normalApproach = core.str_to_bool(args.normal)

    log.info("Loading Data")
    log.debug("Arguments")
    log.debug(args)

    file1 = open(args.input or "preprocessorfile_bspline.txt", "r")
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

    globaldata = core.cleanNeighbours(globaldata)
    problempts,perpendicularpts = core.checkPoints(globaldata,args.bspline,normalApproach)
    wallPts = core.getWallPointArray(globaldata)
    additionPts = []
    try:
        writingDict = dict(core.load_obj("wall"))
    except IOError:
        writingDict = {}
    print(writingDict)
    print("Bsplining", len(problempts), "points.")
    for idx,itm in enumerate(problempts): 
        data = core.feederData(itm,wallPts)
        # print(data[0],data[1])
        if config.getConfig()["bspline"]["polygon"] == False:
            newpts = bsplinegen.bsplineCall(np.array(core.undelimitXY(data[2])),int(config.getConfig()["bspline"]["pointControl"]),data[0],data[1])
            newpts = [core.findNearestPoint(perpendicularpts[idx],newpts)]
        else:
            newpts = [list(perpendicularpts[idx])]
        printProgressBar(idx + 1, len(problempts), prefix="Progress:", suffix="Complete", length=50)
        try:
            writingDict[data[2][int(data[0])]] = writingDict[data[2][int(data[0])]] + newpts
        except KeyError:
            writingDict[data[2][int(data[0])]] = newpts
        additionPts.append(newpts)
    additionPts = list(itertools.chain.from_iterable(additionPts))
    print(writingDict)
    with open("adapted.txt", "a+") as text_file:
        text_file.writelines("1000 1000\n2000 2000\n")
        for item1 in additionPts:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")
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
