import core
from progress import printProgressBar
import argparse
from shapely.geometry import MultiPoint
from shapely.ops import triangulate
import balance
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

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

    globaldata = core.cleanNeighbours(globaldata)
    wallpoints = core.getWallPointArray(globaldata)
    wallpointsData = core.generateWallPolygons(wallpoints)

    interiorpts = []
    interiorpts.extend(range(1, len(globaldata)))
    interiorpts = core.convertPointToShapelyPoint(core.convertIndexToPoints(interiorpts,globaldata))
    interiorpts = MultiPoint(interiorpts)
    interiortriangles = triangulate(interiorpts)
    polydata = balance.getPolygon(interiortriangles)


    while True:
        print("Type exit to quit.")
        ptidx = input("Which point do you want to fix? ")
        if ptidx == "exit":
            break
        ptidx = int(ptidx)

        print("Point Index:",ptidx)
        print("Point Co ordinate:",core.getPointxy(ptidx,globaldata))
        flag = core.getFlag(ptidx,globaldata)
        flag = int(flag)
        if flag == 0:
            flagd = "Wall Point"
        elif flag == 1:
            flagd = "Interior Point"
        else:
            flagd = "Outer Point"
        print("Point Type:",flagd)
        nbhs = core.getNeighbours(ptidx,globaldata)
        print("Total Number of Neighbours:",len(nbhs))
        print("Neighbour Array")
        print(nbhs)
        if(flag==0):
            print(core.getConditionNumberNormal(ptidx,globaldata))
            xpos = core.getDWallXPosPoints(ptidx,globaldata)
            xneg = core.getDWallXNegPoints(ptidx,globaldata)
            print("xpos",len(xpos),"xneg",len(xneg))
        else:
            print(core.getConditionNumber(ptidx,globaldata))
            xpos = core.getDXPosPoints(ptidx,globaldata)
            xneg = core.getDXNegPoints(ptidx,globaldata)
            ypos = core.getDYPosPoints(ptidx,globaldata)
            yneg = core.getDYNegPoints(ptidx,globaldata)
            print("xpos",len(xpos),"xneg",len(xneg),"ypos",len(ypos),"yneg",len(yneg))

        print("Select Point Repair Option")
        print("(1) Delete Connectivity and reinstate connectivity using Triangle Data.")
        print("(2) Delete Connectivity and reinstate connectivity using Triangle Data and balance the remaining using Kumar's Connectivity.")
        print("(3) Delete Connectivity and reinstate connectivity using Triangle Data and balance the remaining using Nischay's Connectivity.")
        print("(4) Balance Connectivity using Triangle Data.")
        print("(5) Balance Connectivity using Triangle Data.")
        print("(5) Exit")
        print("(6) Exit without saving any changes")
        print("(7) Go Back")
        whatkind = int(input("What option do you want to select? "))
        if whatkind == 1:
            tris = balance.getNeighboursFromTriangle(ptidx,globaldata,polydata)
            tris = core.getAeroPointsFromSet(ptidx,tris,globaldata,wallpointsData)
            tris = core.convertPointsToIndex(tris,globaldata)
            globaldata = core.replaceNeighbours(ptidx,tris,globaldata)
        elif whatkind == 2:
            tris = balance.getNeighboursFromTriangle(ptidx,globaldata,polydata)
            tris = core.getAeroPointsFromSet(ptidx,tris,globaldata,wallpointsData)
            tris = core.convertPointsToIndex(tris,globaldata)
            globaldata = core.replaceNeighbours(ptidx,tris,globaldata)
            globadata = balance.fixXneg
        elif whatkind == 3:
            tris = balance.getNeighboursFromTriangle(ptidx,globaldata,polydata)
            tris = core.getAeroPointsFromSet(ptidx,tris,globaldata,wallpointsData)
            tris = core.convertPointsToIndex(tris,globaldata)
            globaldata = core.replaceNeighbours(ptidx,tris,globaldata)
            globaldata = balance.triangleBalance(globaldata,polydata,wallpointsData,ptidx)
        elif whatkind == 4:
            globaldata = balance.triangleBalance(globaldata,polydata,wallpointsData,ptidx)
        elif whatkind == 5:
            break
        elif whatkind == 6:
            exit()
        elif whatkind == 7:
            None
        else:
            break

    globaldata.pop(0)
    
    with open("preprocessorfile_tools.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n") 

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