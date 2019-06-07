import csv
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()
    file = open(args.input, "r")
    plist = []
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

    if cwTurns > ccwTurns:
        print("Orientation: Clockwise")
    else:
        print("Orientation: Anti Clockwise")


if __name__ == "__main__":
    main()