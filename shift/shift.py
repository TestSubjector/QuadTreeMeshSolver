import argparse
import copy
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

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

    # Get interiorpts list
    interiorpts = core.getInteriorPointArrayIndex(globaldata)
    # print(interiorpts)
    # If the interior point has a wallpoint as neighbour
    for idx in interiorpts:
        if core.containsWallPoints(globaldata, idx, wallpoints):
            # print(idx)
            toplx,toply,bottomrx,bottomry = core.getBoundingPointsOfQuadrant(idx, globaldata)
            nbhcords = core.getNeighbours(idx,globaldata)
            for itm in nbhcords:
                if core.getFlag(itm,globaldata) == 0:
                # Calculate normal for that wall point
                    nx, ny = core.normalCalculation(itm, globaldata, True, configData)
                    slope = ny/nx
                    wallptx, wallpty = core.getPoint(itm, globaldata)
                    leftsidey = slope * (toplx - wallptx) + wallpty
                    rightsidey = slope * (bottomrx - wallptx) + wallpty
                        # Check if the quadrant and normal intersect
                    if leftsidey <= toply and leftsidey >= bottomry:
                        # If yes, change x, y of interior point to lie on the normal
                        globaldata[idx][1] = toplx
                        globaldata[idx][2] = leftsidey
                        # print(idx)
                        break
                    elif rightsidey <= toply and rightsidey >= bottomry:
                        globaldata[idx][1] = bottomrx
                        globaldata[idx][2] = rightsidey
                        # print(idx)
                        break
                    else:
                        continue

                    # print(nx, ny)
    globaldata.pop(0)
    with open("preprocessorfile_shift.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")

    log.info("Data Converted")


if __name__ == "__main__":
    main()
