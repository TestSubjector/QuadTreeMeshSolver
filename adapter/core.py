import numpy as np
import math
import os
import errno
import config
from shapely.geometry import Polygon, Point

def appendNeighbours(index, globaldata, newpts):
    pt = getIndexFromPoint(newpts, globaldata)
    nbhs = getNeighbours(index, globaldata)
    nbhs = nbhs + [pt]
    nbhs = list(set(nbhs))
    globaldata[int(index)][14:] = nbhs
    globaldata[int(index)][13] = len(nbhs)
    return globaldata

def silentRemove(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred



def getFlag(indexval, list):
    indexval = int(indexval)
    return int(list[indexval][5])


def getNeighbours(index, globaldata):
    index = int(index)
    ptdata = globaldata[index]
    ptdata = ptdata[14:]
    return ptdata


def getIndexFromPoint(pt, globaldata):
    ptx = float(pt.split(",")[0])
    pty = float(pt.split(",")[1])
    for itm in globaldata:
        if str(itm[1]) == str(ptx) and str(itm[2]) == str(pty):
            return int(itm[0])


def getPoint(index, globaldata):
    index = int(index)
    ptdata = globaldata[index]
    ptx = float(ptdata[1])
    pty = float(ptdata[2])
    return ptx, pty


def getPointxy(index, globaldata):
    index = int(index)
    ptx, pty = getPoint(index, globaldata)
    return str(ptx) + "," + str(pty)


def convertIndexToPoints(indexarray, globaldata):
    ptlist = []
    for item in indexarray:
        item = int(item)
        ptx, pty = getPoint(item, globaldata)
        ptlist.append((str(ptx) + "," + str(pty)))
    return ptlist


def normalCalculation(index, globaldata, wallpoint):
    nx = 0
    ny = 0
    cordx = float(globaldata[index][1])
    cordy = float(globaldata[index][2])
    pointdata = globaldata[index]
    leftpoint = getPointxy(pointdata[3], globaldata)
    rightpoint = getPointxy(pointdata[4], globaldata)
    leftpointx = float(leftpoint.split(",")[0])
    leftpointy = float(leftpoint.split(",")[1])
    rightpointx = float(rightpoint.split(",")[0])
    rightpointy = float(rightpoint.split(",")[1])
    if not wallpoint:
        nx1 = leftpointy - cordy
        nx2 = cordy - rightpointy
        ny1 = leftpointx - cordx
        ny2 = cordx - rightpointx
    else:
        nx1 = cordy - leftpointy
        nx2 = rightpointy - cordy
        ny1 = cordx - leftpointx
        ny2 = rightpointx - cordx
    nx = (nx1 + nx2) / 2
    ny = (ny1 + ny2) / 2
    det = math.sqrt((nx * nx) + (ny * ny))
    if not wallpoint:
        nx = nx / det
    else:
        direction = config.getConfig()["global"]["wallPointOrientation"]
        if direction == "cw":
            nx = (-nx) / det
        elif direction == "ccw":
            nx = nx / det
    ny = ny / det
    return nx, ny


def cleanNeighbours(globaldata):
    print("Beginning Duplicate Neighbour Detection")
    for i in range(len(globaldata)):
        if i == 0:
            continue
        noneighours = int(globaldata[i][11])
        cordneighbours = globaldata[i][-noneighours:]
        result = []
        for item in cordneighbours:
            if int(item) == i:
                continue
            if str(item) not in result:
                result.append(str(item))
        cordneighbours = result

        noneighours = len(cordneighbours)
        globaldata[i] = globaldata[i][:11] + [noneighours] + list(cordneighbours)
    print("Duplicate Neighbours Removed")
    return globaldata


def convertPointToShapelyPoint(pointarry):
    pointnewarry = []
    for itm in pointarry:
        xcord = float(itm.split(",")[0])
        ycord = float(itm.split(",")[1])
        pointnewarry.append((xcord, ycord))
    return pointnewarry


def nonAdaptWallPolygon(globaldata, wallpoints, dist, interiorpts):
    print("Creating Inflated Wall Point")
    pseudopts = []
    inflatedWall = []
    for itm in wallpoints:
        idx = getIndexFromPoint(itm,globaldata)
        orgWallpt = getPointxy(idx, globaldata)
        nx, ny = normalCalculation(idx, globaldata, True)
        orgWallptx = float(orgWallpt.split(",")[0])
        orgWallpty = float(orgWallpt.split(",")[1])
        normalVector = np.array([nx, ny])
        orgVector = np.array([orgWallptx, orgWallpty])
        newWallpt = orgVector + dist * normalVector
        newWallpt = tuple(newWallpt.tolist())
        inflatedWall.append(newWallpt)
    wallptsData = convertPointToShapelyPoint(wallpoints)
    wallpointGeo = Polygon(wallptsData)
    lastpt = wallptsData[0]
    newpt = (lastpt[0] + dist, lastpt[1])
    inflatedWall.pop(0)
    inflatedWall.insert(0, newpt)
    inflatedwallpointGeo = Polygon(inflatedWall)
    print("Checking for Pseudo Points")
    # fig, ax = plt.subplots()
    # x1,y1 = wallpointGeo.exterior.xy
    # x2,y2 = inflatedwallpointGeo.exterior.xy
    # # ax = fig.add_subplot(111)
    # # ax.scatter(x1, y1, color='red', alpha=0.7, zorder=2)
    # # ax.set_title('Polygon')
    # # ax = fig.add_subplot(111)
    # # ax.scatter(x2, y2, color='blue', alpha=0.7, zorder=2)
    # # ax.set_title('Polygon2')
    # # ax = fig.add_subplot(111)
    # ax.plot(x1, y1, color='red', alpha=0.7, zorder=2)
    # ax.plot(x2, y2, color='blue', alpha=0.7, zorder=2)
    # plt.show()
    for itm in interiorpts:
        itmval = convertPointToShapelyPoint(convertIndexToPoints([itm], globaldata))[0]
        interiorpoint = Point(itmval)
        if inflatedwallpointGeo.contains(interiorpoint):
            pseudopts.append(itm)
    print("Found", len(pseudopts), "points which aren't gonna be adapted!")
    with open("pseudopoints.txt", "a") as text_file:
        for item1 in pseudopts:
            text_file.writelines(str(item1))
            text_file.writelines("\t\n")
    return pseudopts


def createEdgeCircle(globaldata, edgePoints, dist, interiorpts):
    pseudopts = []
    for idx,edge in enumerate(edgePoints):
        ptx,pty = getPoint(edge,globaldata)
        circle = Point(ptx,pty).buffer(dist[idx])
        for itm in interiorpts:
            itmval = convertPointToShapelyPoint(convertIndexToPoints([itm], globaldata))[0]
            interiorpoint = Point(itmval)
            if circle.contains(interiorpoint):
                pseudopts.append(itm)
    print("Found", len(pseudopts), "points which aren't gonna be adapted!")
    with open("pseudopoints.txt", "a") as text_file:
        for item1 in pseudopts:
            text_file.writelines(str(item1))
            text_file.writelines("\t\n")
    return pseudopts

def adaptGetWallPointArray(globaldata):
    wallpointarray = []
    startgeo = 0
    newstuff = []
    for idx,itm in enumerate(globaldata):
        if idx > 0:
            geoflag = int(itm[6])
            if(startgeo == geoflag and getFlag(idx,globaldata) == 0):
                newstuff.append(getPointxy(idx,globaldata))
            if(startgeo != geoflag and getFlag(idx,globaldata) == 0):
                newstuff = []
                wallpointarray.append(newstuff)
                newstuff.append(getPointxy(idx,globaldata))
                startgeo = startgeo + 1
    return wallpointarray

def getDistance(point1,point2,globaldata):
    ptax,ptay = getPoint(point1,globaldata)
    ptbx,ptby = getPoint(point2,globaldata)
    ptx = deltaX(ptax,ptbx)**2
    pty = deltaY(ptay,ptby)**2
    result = math.sqrt(ptx + pty)
    return result

def getWallPointArray(globaldata):
    wallpointarray = []
    startgeo = 0
    newstuff = []
    for idx,itm in enumerate(globaldata):
        if idx > 0:
            geoflag = int(itm[6])
            if(startgeo == geoflag and getFlag(idx,globaldata) == 0):
                newstuff.append(getPointxy(idx,globaldata))
            if(startgeo != geoflag and getFlag(idx,globaldata) == 0):
                newstuff = []
                wallpointarray.append(newstuff)
                newstuff.append(getPointxy(idx,globaldata))
                startgeo = startgeo + 1
    return wallpointarray

def getWallPointArrayIndex(globaldata):
    wallpointarray = []
    startgeo = 0
    newstuff = []
    for idx,itm in enumerate(globaldata):
        if idx > 0:
            geoflag = int(itm[6])
            if(startgeo == geoflag and getFlag(idx,globaldata) == 0):
                newstuff.append(idx)
            if(startgeo != geoflag and getFlag(idx,globaldata) == 0):
                newstuff = []
                wallpointarray.append(newstuff)
                newstuff.append(idx)
                startgeo = startgeo + 1
    return wallpointarray