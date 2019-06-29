import argparse
import re
import copy
import numpy as np
import itertools
from tqdm import tqdm
import os, shutil
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()

    log.info("Reading File With Foreign Point Generation")
    wallptsArray = []
    inputArray = []
    try:
        file1 = open(args.input, "r")
        data1 = file1.read()
        file1.close()
        data1 = re.sub(" +", " ", data1)
        splitdata = data1.split("\n")
    except:
        log.error("Failed to read file")
    splitdata = splitdata[:-1]
    wallpts = []
    prevWall = True
    for _, itm in enumerate(tqdm(splitdata)):
        itm = itm.split(" ")[2:]
        cord = tuple(map(float, itm[0:2]))
        if int(itm[2]) == 1 or int(itm[2]) == 4:
            if prevWall == True:
                wallpts.append(cord)
            else:
                prevWall = True
                wallpts = [cord]
        else:
            if prevWall == True:
                wallptsArray.append(wallpts)
                prevWall = False
        inputArray.append(cord)
    
    geometry_name = input("Please enter the name of the geometry: ")
    yn = input("Do you want to save it in grids? (Y/n): ").lower()
    if yn == "y":
        grid_folder = "grids/{}".format(geometry_name)
        if os.path.exists(grid_folder):
            if input("Grid exists. Do you want to delete it? (Y/n): ").lower() == "y":
                shutil.rmtree(grid_folder)
            else:
                log.warning("Did not save grid!")
                exit()
        os.mkdir(grid_folder)
        for idx, itm in enumerate(wallptsArray):
            with open(os.path.join(grid_folder, "{}_{}".format(geometry_name, str(idx + 1))), "w+") as the_file:
                for idx, corditm in enumerate(itm):
                    if idx == len(itm) - 1:
                        the_file.write("{}\t{}".format(corditm[0], corditm[1]))
                    else:
                        the_file.write("{}\t{}\n".format(corditm[0], corditm[1]))
        with open(os.path.join(grid_folder, "{}_{}".format(geometry_name, "_".join(map(str,range(1, len(wallptsArray) + 1))))), "w+") as the_file:
            for idx, corditm in enumerate(inputArray):
                if idx == len(inputArray) - 1:
                    the_file.write("{}\t{}".format(corditm[0], corditm[1]))
                else:
                    the_file.write("{}\t{}\n".format(corditm[0], corditm[1]))
        log.info("Saved Grid!")
    else:
        log.warning("Did not save grid!")
        exit()

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
