import csv
import argparse
import core
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    parser.add_argument("-f", "--fix", nargs="?")
    args = parser.parse_args()
    file = open(args.input, "r")
    plist = []
    fix = False
    reader = csv.reader(file, delimiter = "\t")

    for x,y in reader:
        plist.append((float(x), float(y)))

    def orientation(x1, y1, x2, y2, x3, y3):
        crossProduct = (x2 - x1) * (y3 - y2) - (x3 - x2) * (y2 - y1)
        if crossProduct > 0:
            return "ccw"
        else:
            return "cw"

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
        fix = core.str_to_bool(args.fix)

    if fix == True and clockwise == True:
        filename = os.path.basename(args.input)
        firstpt = plist[0]
        plist.pop()
        plist.pop()
        plist.pop(0)
        plist.reverse()
        plist.insert(0, firstpt)
        with open(filename, "w+") as the_file:
            for itm in plist:
                the_file.write("{}\t{}\n".format(itm[0], itm[1]))
        print("Reconstructed in Counter Clockwise Direction")


if __name__ == "__main__":
    main()