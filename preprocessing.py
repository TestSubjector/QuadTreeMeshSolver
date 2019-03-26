import tqdm
import argparse
import os
from glob import glob
import json

def main():
    checkPrevious()

def checkPrevious():
    if os.path.isdir("files/temp"):
        result = glob("files/temp/*/")
        if len(result) == 0:
            askMain()
    else:
        os.mkdir("files/temp")
        askMain()


def askMain(error = None):
    print("***************************************************************")
    print("Type '1' to start a new iteration")
    print("Type '0' to exit")
    print("***************************************************************")
    grids = getGrids()
    if grids != None:
        print("Grids loaded: %s" % len(grids))
    else:
        clearScreen()
        print("Grids are missing!")
        exit()
    if error != None:
        print("Invalid Option")
    res = input("Enter command to proceed: ")
    try:
        res = int(res)
    except:
        clearScreen()
        askMain(error = "Invalid Option")
    if res == 0:
        exit()
    elif res == 1:
        startIteration(grids)
    
def startIteration(grids):
    

def getGrids():
    if os.path.isdir("grids"):
        res = glob("grids/*/")
        return res
    else:
        return None

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')            

if __name__ == "__main__":
    main()