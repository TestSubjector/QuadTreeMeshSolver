import argparse
from progress import printProgressBar
from core import *
import copy
import logging
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

    file1 = open(args.input or "preprocessorfile_pointremoval.txt", "r")
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

    wallpoints = getWallPointArray(globaldata)

    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 1:
            checkConditionNumber(idx, globaldata, 30)

    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 0:
            checkConditionNumberWall(idx, globaldata, 30)

    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 1:
            globaldata = fixXPosMain(idx, globaldata, 30, wallpoints, -1)
    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 1:
            globaldata = fixXNegMain(idx, globaldata, 30, wallpoints, -1)
    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 1:
            globaldata = fixYPosMain(idx, globaldata, 30, wallpoints, -1)
    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 1:
            globaldata = fixYNegMain(idx, globaldata, 30, wallpoints, -1)
            
    log.info("New")

    for idx, itm in enumerate(globaldata):
        if idx > 0 and getFlag(idx, globaldata) == 1:
            checkConditionNumber(idx, globaldata, 30)

    # print("Set Flag")

    # for idx,itm in enumerate(globaldata):
    #     if(idx > 0 and getFlag(idx,globaldata) == 1):
    #         globaldata = setFlags(idx,globaldata,60)

    globaldata = cleanNeighbours(globaldata)

    globaldata.pop(0)

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
