import argparse
import re
import copy
import numpy as np
import itertools


def printProgressBar(
    iteration, total, prefix="", suffix="", decimals=1, length=100, fill="█"
):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print("\r%s |%s| %s%% %s" % (prefix, bar, percent, suffix), end="\r")
    if iteration == total:
        print()


def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    parser.add_argument("-a", "--adapt", const=str, nargs="?")
    args = parser.parse_args()

    print("Reading File With Foreign Point Generation")

    file1 = open(args.input or "airfoil-unstructured-grid", "r")
    if(args.input != None):
        file2 = open(args.input + ".txt", "w")
    else:
        file2 = open("airfoil_unstructured_grid.txt", "w")      
    if(args.input != None):
        file3 = open("shape_" + args.input + ".txt", "w")
    else:
        file3 = open("shape_" + "airfoil_unstructured_grid.txt", "w")     

    data1 = file1.read()
    data1 = re.sub(" +", " ", data1)
    splitdata = data1.split("\n")
    splitdata = splitdata[:-1]

    file3.write("0 0\n")


    print("Writing proper file format")
    for _, itm1 in enumerate(splitdata):
        # printProgressBar(
        #     idx1, len(data1) - 1, prefix="Progress:", suffix="Complete", length=50
        # )
        adaptpoint = itm1.split(" ")
        adaptpoint.pop(0)
        if(adaptpoint[3] == str(3)):
            file2.write(str(adaptpoint[1]) + " " + str(adaptpoint[2]))
            file2.write("\n")
            file3.write(str(adaptpoint[1]) + " " + str(adaptpoint[2]))
            file3.write("\n")
        else:
            file2.write(str(adaptpoint[1]) + " " + str(adaptpoint[2]))
            file2.write("\n")

    file3.write("0 0\n")
    file1.close()
    file2.close()
    file3.close()
    print("Done")


if __name__ == "__main__":
    main()
