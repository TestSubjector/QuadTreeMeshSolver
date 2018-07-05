import argparse
from progress import printProgressBar
from trialfunctions import *
from neighbouradder import *
import copy
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    parser.add_argument("-r", "--removal", const=str, nargs="?")
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

    for idx, itm in enumerate(splitdata):
        printProgressBar(
            idx, len(splitdata) - 1, prefix="Progress:", suffix="Complete", length=50
        )
        itm = itm.split(" ")  # Split the gaps
        itm.pop(-1)  # Remove last element
        entry = itm
        globaldata.append(entry)

    file2 = open(args.removal or "removal_points.txt", "r")
    removalFlags = file2.read()
    file2.close()
    removalFlags = removalFlags.replace("\t", " ")
    removalFlags = removalFlags.split("\n")
    removalFlags.pop(-1)
    removalFlags = [int(i) for i in removalFlags]
    # print(1030 in removalFlags)

    removalFlags = list(set(removalFlags))

    globaldata = cleanNeighbours(globaldata)
    wallpoints = getWallPointArray(globaldata)
    globaldata = addNewPoints(globaldata, removalFlags, 100, 1, wallpoints)
    globaldata = cleanNeighbours(globaldata)

    # The New Index (with bad points removed) || 5 --> 4
    aliasArray = [0] * (len(globaldata))
    # The Old Index from the new || 4 --> 5
    reverseAliasArray = [0] * (len(globaldata))

    count = 1
    for individiualPoint in globaldata[1:]:
        index = int(individiualPoint[0])
        # print(index)
        if index in removalFlags:
            continue
        else:
            aliasArray[count] = index
            reverseAliasArray[index] = count
            count = count + 1

    # print(globaldata)
    # print(aliasArray)
    # print(count)

    newglobaldata = ["start"]
    for i in range(1, count):
        storage = []
        aliasArrayIndex = aliasArray[i]
        storage.append(i)
        storage.append(globaldata[aliasArrayIndex][1])
        storage.append(globaldata[aliasArrayIndex][2])
        reverseAliasArrayIndex = reverseAliasArray[aliasArrayIndex]
        if reverseAliasArrayIndex == 0:
            left_point = 0
            right_point = 0
        else:
            left_point = int(globaldata[aliasArrayIndex][3])
            right_point = int(globaldata[aliasArrayIndex][4])
        storage.append(reverseAliasArray[left_point])
        storage.append(reverseAliasArray[right_point])
        # The Flags
        for i in range(5, 11):
            storage.append(globaldata[aliasArrayIndex][i])
        # The Neighbours
        neighbourCount = 0
        storage.append(0)  # Temporary count of neighbours
        # We are skipping the element that has total number of original
        # neighbours
        for neighbourIterate in globaldata[aliasArrayIndex][12:]:
            if int(neighbourIterate) in removalFlags:
                continue
            else:
                storage.append(reverseAliasArray[int(neighbourIterate)])
                neighbourCount = neighbourCount + 1
        storage[11] = neighbourCount
        newglobaldata.append(storage)

    # print(newglobaldata[1028:1034])

    newglobaldata = cleanNeighbours(newglobaldata)

    problempts = []
    for individiualPoint in newglobaldata[1:]:
        if int(individiualPoint[5]) != 1:
            continue
        index = int(individiualPoint[0])
        checkConditionNumber(index, newglobaldata, aliasArray, 80, problempts)

    print("***********************************")
    log.info("Writing Removal Points To File")
    print("***********************************")

    problempts = list(dict.fromkeys(problempts))
    # print(problempts)

    with open("removal_points2.txt", "w") as text_file:
        for item1 in problempts:
            text_file.writelines(["%s " % item1])
            text_file.writelines("\n")

    newglobaldata.pop(0)

    with open("preprocessorfile_pointremoval.txt", "w") as text_file:
        for item1 in newglobaldata:
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