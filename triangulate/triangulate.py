from shapely.ops import triangulate, cascaded_union
from shapely.geometry import MultiPoint
from shapely.geometry import Polygon as Polygon2
import argparse
from progress import printProgressBar
from core import *
from connectivity import *
from balance import *
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

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

    wallpts = getWallPointArray(globaldata[1:])

    print("Triangulating")

    interiorpts = []
    interiorpts.extend(range(1, len(globaldata)))
    interiorpts = convertPointToShapelyPoint(convertIndexToPoints(interiorpts,globaldata))
    interiorpts = MultiPoint(interiorpts)
    interiortriangles = triangulate(interiorpts)

    print("Detected",len(wallpts),"geometry(s).")
    polydata = getPolygon(interiortriangles)
    print("Generated",len(polydata),"triangle(s).")
    print("Running Connectivity Check")
    globaldata = connectivityCheck(globaldata)
    print("Connectivity Check Done")
    print("Running Triangulation Balancing")
    globaldata = triangleBalance(globaldata,polydata,wallpts)
    print("Triangle Balancing Done")
    print("Running Connectivity Recheck")
    globaldata = connectivityCheck(globaldata)
    print("Connectivity Recheck Done")
    print("Writing Deletion Points")
    problempts = findDeletionPoints(globaldata)
    
    globaldata = cleanNeighbours(globaldata)

    globaldata.pop(0)

    with open("removal_points.txt", "w") as text_file:
        for item1 in problempts:
            text_file.writelines(["%s " % item1])
            text_file.writelines("\n")

    print("Writing Preprocessor File")

    with open("preprocessorfile_triangulate.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")
    print("Done")

if __name__ == "__main__":
    main()
