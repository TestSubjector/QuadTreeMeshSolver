from shapely.ops import triangulate, cascaded_union
from shapely.geometry import MultiPoint
from shapely.geometry import Polygon as Polygon2
import argparse
from progress import printProgressBar
from core import *
import copy
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection


def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()

    print("Loading Data")

    file1 = open(args.input or "preprocessorfile.txt", "r")
    data = file1.read()
    globaldata = ["start"]
    splitdata = data.split("\n")
    splitdata = splitdata[:-1]
    silentRemove("penrose.dat")

    print("Processed Pre-Processor File")
    print("Converting to readable format")

    for idx, itm in enumerate(splitdata):
        printProgressBar(idx, len(splitdata) - 1,
                         prefix='Progress:', suffix='Complete', length=50)
        itm = itm.split(" ")
        itm.pop(-1)
        entry = itm
        globaldata.append(entry)

    globaldata = cleanNeighbours(globaldata)

    print("Calculating Moore-Penrose Inverse Matrices")
    firsttime = True
    for idx, itm in enumerate(globaldata):
        printProgressBar(idx, len(globaldata) - 1,
                         prefix='Progress:', suffix='Complete', length=50)
        if(idx > 0 and getFlag(idx, globaldata) == 1):
            xpos, xneg, ypos, yneg = getPenrose(idx, globaldata, 1e-3, 2)
            xpos = xpos.tolist()
            xneg = xneg.tolist()
            ypos = ypos.tolist()
            yneg = yneg.tolist()
            ptcord = getPointxy(idx, globaldata)
            with open("penrose.dat", "a+") as text_file:
                if(firsttime):
                    text_file.writelines([str(idx), " "])
                    firsttime = False
                else:
                    text_file.writelines(["\n", str(idx), " "])
                # Write MP
                text_file.writelines([str(len(xpos[0])), " "])
                for blah in xpos[0]:
                    text_file.writelines([str(blah), " "])

                text_file.writelines([str(len(xneg[0])), " "])
                for blah in xneg[0]:
                    text_file.writelines([str(blah), " "])

                text_file.writelines([str(len(ypos[1])), " "])
                for blah in ypos[1]:
                    text_file.writelines([str(blah), " "])

                text_file.writelines([str(len(yneg[1])), " "])
                for blah in yneg[1]:
                    text_file.writelines([str(blah), " "])

    print("Done")


if __name__ == "__main__":
    main()
