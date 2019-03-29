import argparse
import core
import copy
import logging
import config
import numpy as np
import math
import itertools
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
from tqdm import tqdm

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()

    log.info("Loading Data")
    log.debug("Arguments")
    log.debug(args)

    globaldata = config.getKeyVal("globaldata")

    if globaldata == None:

        file1 = open(args.input or "preprocessorfile_normal.txt", "r")
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
    
    pseudoPts = core.inflatedWallPolygon(globaldata,float(config.getConfig()["normalWall"]["inflatedPolygonDistance"]))
    log.info("Found " + str(len(pseudoPts)) + " pseudo points")

    globaldata = core.setNormals(pseudoPts,globaldata)

    for _,idx in enumerate(pseudoPts):
        core.checkConditionNumberLogger(idx,globaldata,float(config.getConfig()["normalWall"]["conditionValueThreshold"]))

    f = open("history.txt","a+")
    f.write("\n ====== \n")
    f.close()

    globaldata.pop(0)

    config.setKeyVal("globaldata",globaldata)

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
