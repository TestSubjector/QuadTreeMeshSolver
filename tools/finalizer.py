import argparse
from shapely.geometry import MultiPoint
from shapely.ops import triangulate
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
from tqdm import tqdm
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()
    np.seterr(divide='ignore')

    print("Loading Data")

    file1 = open(args.input or "preprocessorfile.txt", "r")
    data = file1.read()
    globaldata = ["start"]
    # splitdata = StringIO(data)
    # print(splitdata)
    # globaldata = np.loadtxt(splitdata)
    splitdata = data.split("\n")
    splitdata = splitdata[:-1]

    print("Processed Pre-Processor File")
    print("Converting to readable format")

    for _, itm in enumerate(tqdm(splitdata)):
        itm = itm.split(" ")
        itm.pop(-1)
        entry = itm
        globaldata.append(entry)

    print("Cleaning File")
    
    globaldata.pop(0)
    with open("preprocessorfile_final.txt", "w+") as the_file:
        for itm in tqdm(globaldata):
            stuff = itm[:7]
            stuff.append(itm[11])
            stuff.append(itm[12])
            stuff.append(itm[13])
            stuff.append(itm[19])
            stuff.extend(itm[20:])
            the_file.write("{}\n".format(" ".join(stuff)))
    print("Done")



if __name__ == "__main__":
    main()