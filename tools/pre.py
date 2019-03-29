import core
import argparse
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
from tqdm import tqdm

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()

    log.info("Loading Data")

    globaldata = config.getKeyVal("globaldata")

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

    log.info("Generating triangle data")
    core.generateOutput(globaldata, wallpoints, wallpointsData)

    globaldata.pop(0)

    config.setKeyVal("globaldata",globaldata)

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