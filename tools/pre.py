import argparse
import logging
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
    args = parser.parse_args()

    log.info("Loading Data")

    globaldata = core.getKeyVal("globaldata")

    if globaldata != None:

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
    
    else:
        globaldata.insert(0,"start")

    globaldata = core.cleanNeighbours(globaldata)
    wallpoints = core.getWallPointArray(globaldata)
    wallcount = str(wallpoints)
    wallcount = wallcount.count(",")-wallcount.count("[]")+1
    wallpointsData = core.generateWallPolygons(wallpoints)

    log.info("Running Non Aero Checks")
    globaldata = core.checkAeroGlobal2(globaldata,wallpointsData,wallcount)

    log.info("Generating Polyfile data")
    core.generateOutput(globaldata, wallpoints, wallpointsData)

    log.info("Synchronizing Neighbours")
    globaldata = core.neighbourSynchronize(globaldata)

    globaldata.pop(0)

    core.setKeyVal("globaldata",globaldata)

    log.info("Writing file to disk")

    with open("preprocessorfile_cleaned.txt", "w") as text_file:
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
        logging.core.dictConfig(config)
    else:
        logging.basicConfig(level=level,filename=core.getConfig()["global"]["logger"]["logPath"],format="%(asctime)s %(name)s %(levelname)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
    main()
