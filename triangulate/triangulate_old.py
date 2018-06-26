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

    print("Processed Pre-Processor File")
    print("Converting to readable format")

    for idx, itm in enumerate(splitdata):
        printProgressBar(
            idx, len(splitdata) - 1, prefix="Progress:", suffix="Complete", length=50
        )
        itm = itm.split(" ")
        itm.pop(-1)
        entry = itm
        globaldata.append(entry)

    globaldata = cleanNeighbours(globaldata)

    outerpts = []
    interiorpts = []
    wallpts = []

    print("Point Classification")

    for idx, itm in enumerate(globaldata):
        printProgressBar(
            idx, len(globaldata) - 1, prefix="Progress:", suffix="Complete", length=50
        )
        if idx > 0 and getFlag(idx, globaldata) == 2:
            outerpts.append(idx)
        elif (idx > 0 and getFlag(idx, globaldata) == 1) or (idx > 0 and getFlag(idx,globaldata) == 0) or (idx > 0 and getFlag(idx,globaldata) == 2):
            interiorpts.append(idx)

    wallpts = getWallPointArray(globaldata[1:])

    print("Triangulating")

    interiorpts = convertPointToShapelyPoint(
        convertIndexToPoints(interiorpts, globaldata)
    )
    interiorpts = MultiPoint(interiorpts)
    interiortriangles = triangulate(interiorpts)

    wallptsNew = []
    for itm in wallpts:
        itm = convertPointToShapelyPoint(itm)
        itm = Polygon2(itm)
        wallptsNew.append(itm)

    print("Generating Model")
    polygns = []
    fig, ax = plt.subplots()
    for idx, itm in enumerate(interiortriangles):
        printProgressBar(
            idx,
            len(interiortriangles) - 1,
            prefix="Progress:",
            suffix="Complete",
            length=50,
        )
        theshit = list(zip(*itm.exterior.xy))
        polygns.append(Polygon(theshit, True))

    p = PatchCollection(polygns, cmap=matplotlib.cm.jet, alpha=0.4)
    colors = 100 * np.random.rand(len(polygns))
    p.set_array(np.array(colors))
    ax.add_collection(p)
    print("Plotting")
    plt.show()
    # xs, ys = [],[]
    # mergedtriangles = cascaded_union(outertriangles)
    # for triangle in outertriangles:
    #     xstemp,ystemp = triangle.exterior.xy
    #     print(xstemp,ystemp)
    # xs,ys = mergedtriangles.exterior.xy
    # fig, axs = plt.subplots()
    # axs.fill(xs, ys, alpha=0.5, fc='r', ec='none')
    # plt.show() #if not interactive.

    # print("Set Flag")

    # for idx,itm in enumerate(globaldata):
    #     if(idx > 0 and getFlag(idx,globaldata) == 1):
    #         globaldata = setFlags(idx,globaldata,60)

    print("Done")


if __name__ == "__main__":
    main()
