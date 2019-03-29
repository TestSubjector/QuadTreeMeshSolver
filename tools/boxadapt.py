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
    parser.add_argument("-a", "--headadapt", const=str, nargs="?")
    args = parser.parse_args()

    log.info("Loading Data")

    file1 = open(args.input or "preprocessorfile.txt", "r")
    data = file1.read()
    globaldata = ["start"]
    splitdata = data.split("\n")
    splitdata = splitdata[:-1]

    headAdpt = core.str_to_bool(args.headadapt) 

    log.info("Processed Pre-Processor File")
    log.info("Converting to readable format")

    for _, itm in enumerate(tqdm(splitdata)):
        itm = itm.split(" ")
        itm.pop(-1)
        entry = itm
        globaldata.append(entry)

    globaldata = core.cleanNeighbours(globaldata)
    wallpoints = core.getWallPointArray(globaldata)
    
    if headAdpt:
        log.info("Find Points inside the Box (Head Adaptation)")
        result = core.findBoxAdaptPoints(globaldata,wallpoints)
        log.info("Writing file to disk")
    else:
        log.info("Find Points inside the Box (General Box Adaptation)")
        result = core.findGeneralBoxAdaptPoints(globaldata)
        log.info("Writing file to disk")

    with open("adapted.txt", "a") as text_file:
        for item1 in result:
            ptx,pty = core.getPoint(int(item1),globaldata)
            text_file.writelines(["%s %s" % (ptx, pty)])
            text_file.writelines("\n")
        text_file.writelines("1000 1000\n")

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