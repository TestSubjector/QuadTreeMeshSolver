import argparse
import copy
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from tqdm import tqdm
from core import core

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()

    log.info("Loading Data")
    log.debug("Arguments")
    log.debug(args)

    globaldata = core.getKeyVal("globaldata")
    configData = core.getConfig()
    globaldata.insert(0,"start")
    # print(len(globaldata))
    globaldata = core.cleanNeighbours(globaldata)
    wallpoints = core.getWallPointArrayIndex(globaldata)
    wallpoints = core.flattenList(wallpoints)
    # wallpoints = core.convertToShapely(wallpoints)
    shiftFlag = int(configData["shift"]["shiftFlag"])
    # Get interiorpts list
    interiorpts = core.getInteriorPointArrayIndex(globaldata)
    # print(interiorpts)
    # If the interior point has a wallpoint as neighbour
    log.info("Scanning Interior Points for Possible Shifting")
    for idx in tqdm(interiorpts):
        if core.containsWallPoints(globaldata, idx, wallpoints):
            # print(idx)
            toplx,toply,bottomrx,bottomry = core.getBoundingPointsOfQuadrant(idx, globaldata)
            nbhcords = core.getNeighbours(idx,globaldata)

            mainptx, mainpty = core.getPoint(idx,globaldata)
            bestwallpt = 0
            mindist = 1000.0
            # Get all neighbouring
            for itm in nbhcords:
                if core.getFlag(itm,globaldata) == 0:
                    wallptx, wallpty = core.getPoint(itm, globaldata)
                    if mindist > core.distance(mainptx, mainpty, wallptx, wallpty):
                        mindist = core.distance(mainptx, mainpty, wallptx, wallpty)
                        bestwallpt = itm

            # Safety Case
            if bestwallpt == 0:
                continue
            else:
                itm = bestwallpt

            # Calculate normal for that wall point
            nx, ny = core.normalCalculation(itm, globaldata, True, configData)
            slope = ny/nx
            wallptx, wallpty = core.getPoint(itm, globaldata)
            leftsidey = slope * (toplx - wallptx) + wallpty
            rightsidey = slope * (bottomrx - wallptx) + wallpty
            lowersidex = (bottomry - wallpty) / slope + wallptx
            uppersidex = (toply - wallpty) / slope + wallptx
            # Check if the quadrant and normal intersect
            if shiftFlag == 0:
                maxdist = 0.0
                if leftsidey <= toply and leftsidey >= bottomry:
                    # If yes, change x, y of interior point to lie on the normal
                    if maxdist < core.distance(wallptx, wallpty, toplx, leftsidey):
                        maxdist = core.distance(wallptx, wallpty, toplx, leftsidey)
                        globaldata[idx][1] = toplx
                        globaldata[idx][2] = leftsidey
                        globaldata = core.setNormals(idx, globaldata, (nx, ny))
                if rightsidey <= toply and rightsidey >= bottomry:
                    if maxdist < core.distance(wallptx, wallpty, bottomrx, rightsidey):
                        maxdist = core.distance(wallptx, wallpty, bottomrx, rightsidey)
                        globaldata[idx][1] = bottomrx
                        globaldata[idx][2] = rightsidey
                        globaldata = core.setNormals(idx, globaldata, (nx, ny))
                if uppersidex <= bottomrx and uppersidex >= toplx:
                    if maxdist < core.distance(wallptx, wallpty, toplx, leftsidey):
                        maxdist = core.distance(wallptx, wallpty, toplx, leftsidey)
                        globaldata[idx][1] = uppersidex
                        globaldata[idx][2] = toply
                        globaldata = core.setNormals(idx, globaldata, (nx, ny))
                if lowersidex <= bottomrx and lowersidex >= toplx:
                    if maxdist < core.distance(wallptx, wallpty, lowersidex, bottomry):
                        maxdist = core.distance(wallptx, wallpty, lowersidex, bottomry)
                        globaldata[idx][1] = lowersidex
                        globaldata[idx][2] = bottomry
                        globaldata = core.setNormals(idx, globaldata, (nx, ny))
            elif shiftFlag == 1:
                mindist = 1000.0
                if leftsidey <= toply and leftsidey >= bottomry:
                    # If yes, change x, y of interior point to lie on the normal
                    if mindist > core.distance(wallptx, wallpty, toplx, leftsidey):
                        mindist = core.distance(wallptx, wallpty, toplx, leftsidey)
                        globaldata[idx][1] = toplx
                        globaldata[idx][2] = leftsidey
                        globaldata = core.setNormals(idx, globaldata, (nx, ny))
                if rightsidey <= toply and rightsidey >= bottomry:
                    if mindist > core.distance(wallptx, wallpty, bottomrx, rightsidey):
                        mindist = core.distance(wallptx, wallpty, bottomrx, rightsidey)
                        globaldata[idx][1] = bottomrx
                        globaldata[idx][2] = rightsidey
                        globaldata = core.setNormals(idx, globaldata, (nx, ny))
                if uppersidex <= bottomrx and uppersidex >= toplx:
                    if mindist > core.distance(wallptx, wallpty, toplx, leftsidey):
                        mindist = core.distance(wallptx, wallpty, toplx, leftsidey)
                        globaldata[idx][1] = uppersidex
                        globaldata[idx][2] = toply
                        globaldata = core.setNormals(idx, globaldata, (nx, ny))
                if lowersidex <= bottomrx and lowersidex >= toplx:
                    if mindist > core.distance(wallptx, wallpty, lowersidex, bottomry):
                        mindist = core.distance(wallptx, wallpty, lowersidex, bottomry)
                        globaldata[idx][1] = lowersidex
                        globaldata[idx][2] = bottomry
                        globaldata = core.setNormals(idx, globaldata, (nx, ny))
                # print(idx)
                # break
            # else:
                # continue
                # print(nx, ny)
    globaldata.pop(0)
    core.setKeyVal("globaldata",globaldata)
    log.info("Writing file to disk")
    with open("preprocessorfile_shift.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")

    log.info("Geometry Shifted Converted")


if __name__ == "__main__":
    main()
