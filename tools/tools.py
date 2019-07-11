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
    loaded = False
    try:
        file1 = open(args.input, "r")
        data = file1.read()
        globaldata = ["start"]
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
        wallpointsall = list(map(int, core.flattenList(core.getWallPointArrayIndex(globaldata))))
        loaded = True
    
    except:
        loaded = False
    
    conf = core.getConfig()

    # interiorpts = []
    # interiorpts.extend(range(1, len(globaldata)))
    # interiorpts = core.convertPointToShapelyPoint(core.convertIndexToPoints(interiorpts,globaldata))
    # interiorpts = MultiPoint(interiorpts)
    # interiortriangles = triangulate(interiorpts)
    # polydata = balance.getPolygon(interiortriangles)
    # plot 'preprocessorfile.txt' using 2:3:(sprintf("%d", $1)) with labels notitle
    core.clearScreen()
    while True and loaded:
        print("Type 'exit! to quit (Does not save changes).")
        print("Type 'exit to quit (Saves changes).")
        print("Type 'wcc' to run Wall Connectivity Check on all Wall Points.")
        print("Type 'wcc!' to run Wall Connectivity Check on all Wall Points and return nearest point.")
        print("Type 'wcc!!' to run Wall Connectivity Check on all Wall Points and generate a corresponding sensor file.")
        print("Type 'wcc!!!' to run Wall Connectivity Check on all Wall Points and try fixing sparsity. (Wall Mode)")
        print("Type 'wcc!!!!' to run Wall Connectivity Check on all Wall Points and try fixing sparsity. (Interior Mode)")
        print("Type 'wcc!!!!!' to run Wall Connectivity Check on all Wall Points and just print them.")
        print("Type 'icc' to run Interior Connectivity Check on all Interior Points.")
        print("Type 'cache' to push the file you read into cache.")
        print("Type 'integrity' to check wall.json integrity")
        print("Type 'integrity!' to check wall.json integrity and fix it")
        print("Type 'full' to perform one full refinement")
        print("Type 'fullno' to perform one full refinement (excluding outer)")
        print("Type 'customrefine' to perform custom refinement")
        print("Type 'old' to convert preprocessorfile to old format")
        print("Type 'bad2' to print all points with 2 in it's split connectivity")
        print("Type 'bad1' to print all points with 1 in it's split connectivity")
        print("Type 'split' to output the different type of points in a file")
        print("Type 'config' to start Config Manager")
        print("Type 'plot' to start Plot Manager")
        print("Type 'config' to start Config Manager")
        print("Type 'hills' to start Hills and Valleys Manager")
        
        ptidx = input("Which point do you want to fix? ").lower()

        if ptidx == "exit!":
            exit()
        if ptidx == "exit":
            break
        elif ptidx == "hills":
            core.hills_manager()
        elif ptidx == "wcc":
            core.clearScreen()
            globaldata,_ = core.connectivityCheck(globaldata, wallpointsall, conf)
            core.wallConnectivityCheck(globaldata)
        elif ptidx == "wcc!":
            core.clearScreen()
            globaldata,_ = core.connectivityCheck(globaldata, wallpointsall, conf)
            core.wallConnectivityCheckNearest(globaldata)
        elif ptidx == "wcc!!":
            core.clearScreen()
            globaldata,_ = core.connectivityCheck(globaldata, wallpointsall, conf)
            core.wallConnectivityCheckSensor(globaldata)    
        elif ptidx == "wcc!!!":
            core.clearScreen()
            globaldata,_ = core.connectivityCheck(globaldata, wallpointsall, conf)
            core.sparseNullifier(globaldata, flagCheck=0)
        elif ptidx == "wcc!!!!":
            core.clearScreen()
            globaldata,_ = core.connectivityCheck(globaldata, wallpointsall, conf)
            core.sparseNullifier(globaldata, flagCheck=1)  
        elif ptidx == "wcc!!!!!":
            core.clearScreen()
            globaldata,_ = core.connectivityCheck(globaldata, wallpointsall, conf)
            core.wallConnectivityCheck(globaldata, verbose=True)
        elif ptidx == "icc":
            core.clearScreen()
            core.interiorConnectivityCheck(globaldata, offset=len(wallpointsall))
        elif ptidx == "cache":
            core.clearScreen()
            core.pushCache(globaldata)
        elif ptidx == "integrity":
            core.clearScreen()
            core.verifyIntegrity()
        elif ptidx == "integrity!":
            core.clearScreen()
            core.fixWallIntegrity()
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
            globaldata,_ = core.connectivityCheck(globaldata, None, conf)
            core.printBadness(2,globaldata)    
        elif ptidx == "bad1":
            core.clearScreen()
            globaldata,_ = core.connectivityCheck(globaldata, None, conf)
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
        elif ptidx == "clear":
            core.clearScreen()
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
            print("Point Co ordinate:",core.getPointXY(ptidx,globaldata))
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
                print(core.getConditionNumberNew(ptidx,globaldata, conf))
                xpos = core.getXPosPoints(ptidx,globaldata, conf)
                xneg = core.getXNegPoints(ptidx,globaldata, conf)
                ypos = core.getYPosPoints(ptidx,globaldata, conf)
                yneg = core.getYNegPoints(ptidx,globaldata, conf)
                print("xpos",len(xpos),"xneg",len(xneg))
            else:
                print(core.getConditionNumberNew(ptidx,globaldata, conf))
                xpos = core.getXPosPoints(ptidx,globaldata, conf)
                xneg = core.getXNegPoints(ptidx,globaldata, conf)
                ypos = core.getYPosPoints(ptidx,globaldata, conf)
                yneg = core.getYNegPoints(ptidx,globaldata, conf)
                print("xpos",len(xpos),"xneg",len(xneg),"ypos",len(ypos),"yneg",len(yneg))
            nx, ny = core.getNormals(ptidx, globaldata, conf)
            print("nx = {} ny = {}".format(nx, ny))
            print("Select Point Repair Option")
            print("(1) Exit")
            print("(2) Exit without saving any changes")
            print("(3) Go Back")
            print("(4) Find nearest distance to wall points")
            print("(5) Print Detailed Connectivity")
            whatkind = int(input("What option do you want to select? "))
            if whatkind == 1:
                core.clearScreen()
                break
            elif whatkind == 2:
                exit()
            elif whatkind == 3:
                core.clearScreen()
            elif whatkind == 4:
                core.clearScreen()
                px, py = core.getPoint(ptidx, globaldata)
                print("Nearest Distance: {}".format(min(core.wallDistance((px, py), wallpointsData))))
            elif whatkind == 5:
                core.clearScreen()
                print("xpos connectivity: {}, no. of xpos: {}".format(core.convertPointsToIndex(xpos, globaldata), len(xpos)))
                print("xneg connectivity: {}, no. of xneg: {}".format(core.convertPointsToIndex(xneg, globaldata), len(xneg)))
                print("ypos connectivity: {}, no. of ypos: {}".format(core.convertPointsToIndex(ypos, globaldata), len(ypos)))
                print("yneg connectivity: {}, no. of yneg: {}".format(core.convertPointsToIndex(yneg, globaldata), len(yneg)))
            else:
                core.clearScreen()
                break

    if loaded:
        globaldata.pop(0)
        
        with open("preprocessorfile_tools.txt", "w") as text_file:
            for item1 in globaldata:
                text_file.writelines(["%s " % item for item in item1])
                text_file.writelines("\n") 
    else:
        while True:
            print("Type 'integrity' to check wall.json integrity")
            print("Type 'integrity!' to check wall.json integrity and fix it")
            print("Type 'config' to start Config Manager")
            print("Type 'hills' to start Hills and Valleys Manager")
            print("Type 'exit' to exit")

            ptidx = input("Enter command: ").lower()

            if ptidx == "integrity":
                core.clearScreen()
                core.verifyIntegrity()

            elif ptidx == "integrity!":
                core.clearScreen()
                core.fixWallIntegrity()

            
            elif ptidx == "config":
                core.clearScreen()
                core.configManager() 

            elif ptidx == "hills":
                core.clearScreen()
                core.hills_manager()

            elif ptidx == "exit":
                exit()



if __name__ == "__main__":
    import logging
    import os
    import json
    import logging.config
    import sys
    import numpy as np
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    from core import core
    

    default_path='logging.json'
    path = default_path
    level = core.getConfig()["global"]["logger"]["level"]

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
        logging.basicConfig(level=level,filename=core.getConfig()["global"]["logger"]["logPath"],format="%(asctime)s %(name)s %(levelname)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
    with np.errstate(divide='ignore', invalid='ignore'):
        main()