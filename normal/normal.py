import argparse
import copy
import logging
import numpy as np
import math
import itertools
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
from tqdm import tqdm
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    parser.add_argument("-n", "--normal", nargs="+")
    parser.add_argument("-c", "--cache", nargs="?")
    parser.add_argument("-d", "--dry-run", nargs="?")
    parser.add_argument("-l", "--legacy", nargs="?")
    args = parser.parse_args()

    log.info("Loading Data")
    log.debug("Arguments")
    log.debug(args)

    globaldata = core.getKeyVal("globaldata")

    configData = core.getConfig()

    cache = True
    if args.cache:
        cache = core.ConvertStringToBool(args.cache)

    legacy = configData["normalWall"]["legacyMode"]
    if args.legacy:
        legacy = core.ConvertStringToBool(args.legacy)

    dryRun = False
    if args.dry_run:
        dryRun = core.ConvertStringToBool(args.dry_run)

    pseudoPts = []
    if args.normal:
        log.info("Info: Custom Points to be checked are enforced")
        pseudoPts = tuple(map(int, args.normal))

    if globaldata == None or cache == False:

        file1 = open(args.input, "r")
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
    
    else:
        globaldata.insert(0,"start")
    
    if legacy:
        log.info("Using Legacy Normal Rotation Method")
        if len(pseudoPts) == 0:
            None
            # pseudoPts = core.inflatedWallPolygon(globaldata,float(configData["normalWall"]["inflatedPolygonDistance"]), configData)
        log.info("Found {} pseudo points".format(len(pseudoPts)))
        # globaldata = core.rotateNormalsLegacy(pseudoPts, globaldata, configData, dryRun)

    else:
        log.info("Using Normal Rotation Method")
        if len(pseudoPts) == 0:
            pseudoPts = core.getPseudoPoints(globaldata)
        log.info("Found {} pseudo points".format(len(pseudoPts)))
        globaldata = core.rotateNormals(pseudoPts, globaldata, configData, dryRun)

    globaldata.pop(0)

    core.setKeyVal("globaldata",globaldata)

    with open("preprocessorfile_normal.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")
            
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
