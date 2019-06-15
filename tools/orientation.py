import csv
import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    parser.add_argument("-f", "--fix", nargs="?")
    parser.add_argument("-p", "--inplace", nargs="?")
    args = parser.parse_args()
    file = open(args.input, "r")
    plist = []
    fix = False
    reader = csv.reader(file, delimiter = "\t")

    for x,y in reader:
        plist.append((float(x), float(y)))

    cwTurns = 0
    ccwTurns = 0
    plist.append(plist[0])
    plist.append(plist[1])

    for j in range(len(plist) - 2):
        (x1, y1) = plist[j]
        (x2, y2) = plist[j+1]
        (x3, y3) = plist[j+2]
        if (orientation(x1, y1, x2, y2, x3, y3) == "cw"):
            cwTurns += 1
        else:
            ccwTurns += 1

    if cwTurns == 0 or ccwTurns == 0:
        print("Geometry: Convex")
    else:
        print("Geometry: Not Convex")

    clockwise = False
    if cwTurns > ccwTurns:
        print("Orientation: Clockwise")
        clockwise = True
    else:
        print("Orientation: Anti Clockwise")

    if args.fix:
        fix = core.ConvertStringToBool(args.fix)

    inplace = False
    if args.inplace:
        inplace = core.ConvertStringToBool(args.inplace)

    if fix == True and clockwise == True:
        if not inplace:
            filename = os.path.basename(args.input)
        else:
            filename = args.input

        firstpt = plist[0]
        plist.pop()
        plist.pop()
        plist.pop(0)
        plist.reverse()
        plist.insert(0, firstpt)
        with open(filename, "w+") as the_file:
            for itm in plist:
                the_file.write("{}\t{}\n".format(itm[0], itm[1]))
        if inplace:
            print("Reconstructed in Counter Clockwise Direction and replaced inplace")
        else:
            print("Reconstructed in Counter Clockwise Direction")

def orientation(x1, y1, x2, y2, x3, y3):
    crossProduct = (x2 - x1) * (y3 - y2) - (x3 - x2) * (y2 - y1)
    if crossProduct > 0:
        return "ccw"
    else:
        return "cw"



if __name__ == "__main__":
    main()