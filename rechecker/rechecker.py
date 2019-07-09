import argparse
import copy
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()

    log.info("Loading Data")
    log.debug("Arguments")
    log.debug(args)

    globaldata = core.getKeyVal("globaldata")
    configData = core.getConfig()

    if globaldata == None:

        file1 = open(args.input or "preprocessorfile_pointremoval.txt", "r")
        data = file1.read()
        globaldata = ["start"]
        splitdata = data.split("\n")
        splitdata = splitdata[:-1]

        log.info("Processed Pre-Processor File")
        log.info("Converting to readable format")

        for idx, itm in enumerate(splitdata):
            itm = itm.split(" ")
            itm.pop(-1)
            entry = itm
            globaldata.append(entry)

    else:
        globaldata.insert(0,"start")

    globaldata = core.cleanNeighbours(globaldata)

    wallpoints = core.getWallPointArray(globaldata)
    wallpoints = core.convertToShapely(wallpoints)

    configData = core.getConfig()

    THRESHOLD = int(configData["rechecker"]["conditionValueThreshold"])
    MAX_POINTS = -configData["rechecker"]["maxPoints"]

    badList = core.checkConditionNumberBad(globaldata, THRESHOLD, configData)
    log.info("Problematic Points to be fixed: {}".format(len(badList)))

    # for idx, itm in enumerate(globaldata):
    #     if idx > 0 and getFlag(idx, globaldata) == 0:
    #         checkConditionNumberWall(idx, globaldata, 30)

    for idx in badList:
        globaldata = core.fixXPosMain(idx, globaldata, THRESHOLD, wallpoints, MAX_POINTS, configData)
    for idx in badList:
        globaldata = core.fixXNegMain(idx, globaldata, THRESHOLD, wallpoints, MAX_POINTS, configData)
    for idx in badList:
        globaldata = core.fixYPosMain(idx, globaldata, THRESHOLD, wallpoints, MAX_POINTS, configData)
    for idx in badList:
        globaldata = core.fixYNegMain(idx, globaldata, THRESHOLD, wallpoints, MAX_POINTS, configData)

    badList = core.checkConditionNumberSelectively(globaldata, THRESHOLD, badList, configData)

    if len(badList) == 0:
        log.info("All problematic points have been fixed")
    else:
        log.warning("Total Number of Points unable to be fixed: {}".format(len(badList)))

    # print("Set Flag")

    # for idx,itm in enumerate(globaldata):
    #     if(idx > 0 and getFlag(idx,globaldata) == 1):
    #         globaldata = setFlags(idx,globaldata,60)

    globaldata = core.cleanNeighbours(globaldata)

    globaldata.pop(0)

    core.setKeyVal("globaldata",globaldata)

    with open("preprocessorfile_rechecker.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")

    log.info("Data Converted")


if __name__ == "__main__":
    import logging
    import os
    import json
    import logging.config
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    from core import core
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
