import argparse
import connectivity
from shapely.geometry import MultiPoint
from shapely.ops import triangulate
import balance
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

    globaldata = core.cleanNeighbours(globaldata)
    wallpoints = core.getWallPointArray(globaldata)
    wallpointsData = core.generateWallPolygons(wallpoints)
    conf = config.getConfig()

    # interiorpts = []
    # interiorpts.extend(range(1, len(globaldata)))
    # interiorpts = core.convertPointToShapelyPoint(core.convertIndexToPoints(interiorpts,globaldata))
    # interiorpts = MultiPoint(interiorpts)
    # interiortriangles = triangulate(interiorpts)
    # polydata = balance.getPolygon(interiortriangles)
    # plot 'preprocessorfile.txt' using 2:3:(sprintf("%d", $1)) with labels notitle
    core.clearScreen()

    while True:
        print("Type 'exit! to quit (Does not save changes).")
        print("Type 'exit to quit (Saves changes).")
        print("Type 'wcc' to run Wall Connectivity Check on all Wall Points.")
        print("Type 'wcc!' to run Wall Connectivity Check on all Wall Points and return nearest point.")
        print("Type 'wcc!!' to run Wall Connectivity Check on all Wall Points and generate a corresponding sensor file.")
        print("Type 'wcc!!!' to run Wall Connectivity Check on all Wall Points and try fixing sparsity.")
        print("Type 'wcc!!!!' to run Wall Connectivity Check on all Wall Points and just print them.")
        print("Type 'icc' to run Interior Connectivity Check on all Interior Points.")
        print("Type 'cache' to push the file you read into cache.")
        print("Type 'integrity' to check wall.json integrity")
        print("Type 'full' to perform one full refinement")
        print("Type 'fullno' to perform one full refinement (excluding outer)")
        print("Type 'customrefine' to perform custom refinement")
        print("Type 'clean' to cleanse the soul of adapted.txt")
        print("Type 'old' to convert preprocessorfile to old format")
        print("Type 'bad2' to print all points with 2 in it's split connectivity")
        print("Type 'bad1' to print all points with 1 in it's split connectivity")
        print("Type 'split' to output the different type of points in a file")
        print("Type 'config' to start Config Manager")
        print("Type 'plot' to start Plot Manager")
        ptidx = input("Which point do you want to fix? ")
        if ptidx == "exit!":
            exit()
        if ptidx == "exit":
            break
        elif ptidx == "wcc":
            core.clearScreen()
            globaldata = connectivity.connectivityCheck(globaldata, True, False)
            core.wallConnectivityCheck(globaldata)
        elif ptidx == "wcc!":
            core.clearScreen()
            globaldata = connectivity.connectivityCheck(globaldata, True, False)
            core.wallConnectivityCheckNearest(globaldata)
        elif ptidx == "wcc!!":
            core.clearScreen()
            globaldata = connectivity.connectivityCheck(globaldata, True, False)
            core.wallConnectivityCheckSensor(globaldata)    
        elif ptidx == "wcc!!!":
            core.clearScreen()
            globaldata = connectivity.connectivityCheck(globaldata, True, False)
            core.sparseNullifier(globaldata)  
        elif ptidx == "wcc!!!!":
            core.clearScreen()
            globaldata = connectivity.connectivityCheck(globaldata, True, False)
            core.wallConnectivityCheck(globaldata, verbose=True)
        elif ptidx == "icc":
            core.clearScreen()
            core.interiorConnectivityCheck(globaldata)
        elif ptidx == "cache":
            core.clearScreen()
            core.pushCache(globaldata)
        elif ptidx == "integrity":
            core.clearScreen()
            core.verifyIntegrity()
        elif ptidx == "clean":
            core.clearScreen()
            core.cleanAdapted()
        elif ptidx == "full":
            core.clearScreen()
            core.fullRefine(globaldata)
        elif ptidx == "fullno":
            core.clearScreen()
            core.fullRefineOuter(globaldata)
        elif ptidx == "customrefine":
            core.clearScreen()
            core.refineCustom(globaldata)
        elif ptidx == "old":
            core.clearScreen()
            core.oldMode(globaldata)
        elif ptidx == "bad2":
            core.clearScreen()
            globaldata = connectivity.connectivityCheck(globaldata, True, True)
            core.printBadness(2,globaldata)    
        elif ptidx == "bad1":
            core.clearScreen()
            globaldata = connectivity.connectivityCheck(globaldata, True, True)
            core.printBadness(1,globaldata)   
        elif ptidx == "split":
            core.clearScreen()
            core.splitWrite(globaldata) 
        elif ptidx == "config":
            core.clearScreen()
            core.configManager() 
        elif ptidx == "plot":
            core.clearScreen()
            core.plotManager(globaldata, wallpoints)
        isPointIndex = False
        try:
            ptidx = int(ptidx)
            isPointIndex = True
        except ValueError:
            isPointIndex = False
            pass
        if isPointIndex == True:
            core.clearScreen()
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
                print(core.getConditionNumberNormal(ptidx,globaldata, conf))
                xpos = core.getDWallXPosPoints(ptidx,globaldata, conf)
                xneg = core.getDWallXNegPoints(ptidx,globaldata, conf)
                print("xpos",len(xpos),"xneg",len(xneg))
            else:
                print(core.getConditionNumber(ptidx,globaldata, conf))
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
            print("(6) Find Point Perpendicular to nearest wall segment")
            print("(7) Exit")
            print("(8) Exit without saving any changes")
            print("(9) Go Back")
            print("(10) Increase connectivity set to 3")
            print("(11) Find nearest distance to wall points")
            whatkind = int(input("What option do you want to select? "))
            if whatkind == 1:
                # tris = balance.getNeighboursFromTriangle(ptidx,globaldata,polydata)
                # tris = core.getAeroPointsFromSet(ptidx,tris,globaldata,wallpointsData)
                # tris = core.convertPointsToIndex(tris,globaldata)
                # globaldata = core.replaceNeighbours(ptidx,tris,globaldata)
                None
            elif whatkind == 2:
                # tris = balance.getNeighboursFromTriangle(ptidx,globaldata,polydata)
                # tris = core.getAeroPointsFromSet(ptidx,tris,globaldata,wallpointsData)
                # tris = core.convertPointsToIndex(tris,globaldata)
                # globaldata = core.replaceNeighbours(ptidx,tris,globaldata)
                # globadata = balance.fixXneg
                None
            elif whatkind == 3:
                # tris = balance.getNeighboursFromTriangle(ptidx,globaldata,polydata)
                # tris = core.getAeroPointsFromSet(ptidx,tris,globaldata,wallpointsData)
                # tris = core.convertPointsToIndex(tris,globaldata)
                # globaldata = core.replaceNeighbours(ptidx,tris,globaldata)
                # globaldata = balance.triangleBalance(globaldata,polydata,wallpointsData,ptidx)
                None
            elif whatkind == 4:
                # globaldata = balance.triangleBalance(globaldata,polydata,wallpointsData,ptidx)
                None
            elif whatkind == 5:
                None
            elif whatkind == 6:
                print(core.getPerpendicularPoint(ptidx,globaldata))
            elif whatkind == 7:
                core.clearScreen()
                break
            elif whatkind == 8:
                exit()
            elif whatkind == 9:
                core.clearScreen()
                None
            elif whatkind == 10:
                tris = core.getNeighbours(ptidx,globaldata)
                tris = core.getAeroPointsFromSet(ptidx,tris,globaldata,wallpointsData)
                tris = core.convertPointsToIndex(tris,globaldata)
                globaldata = balance.forcePointsToFix(ptidx,tris,globaldata)
            elif whatkind == 11:
                core.clearScreen()
                px, py = core.getPoint(ptidx, globaldata)
                print("Nearest Distance: {}".format(min(core.wallDistance((px, py), wallpointsData))))
            else:
                core.clearScreen()
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