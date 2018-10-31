import numpy as np
import math
import os
import errno
import config
import itertools
from shapely.geometry import Polygon, Point
from shapely import wkt
from shapely.ops import linemerge, unary_union, polygonize
import shapely
import json

def appendNeighbours(index, globaldata, newpts):
    pt = getIndexFromPoint(newpts, globaldata)
    nbhs = getNeighbours(index, globaldata)
    nbhs = nbhs + [pt]
    nbhs = list(set(nbhs))
    globaldata[int(index)][20:] = nbhs
    globaldata[int(index)][19] = len(nbhs)
    return globaldata

def silentRemove(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred

def deltaX(xcord, orgxcord):
    return float(orgxcord - xcord)


def deltaY(ycord, orgycord):
    return float(orgycord - ycord)


def getFlag(indexval, list):
    indexval = int(indexval)
    return int(list[indexval][5])


def getNeighbours(index, globaldata):
    index = int(index)
    ptdata = globaldata[index]
    ptdata = ptdata[20:]
    return ptdata


def getIndexFromPoint(pt, globaldata):
    ptx = float(pt.split(",")[0])
    pty = float(pt.split(",")[1])
    for itm in globaldata:
        if str(itm[1]) == str(ptx) and str(itm[2]) == str(pty):
            return int(itm[0])

def getIndexFromPointTuple(pt, globaldata):
    ptx = pt[0]
    pty = pt[1]
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

def getDistance(point1,point2,globaldata):
    ptax,ptay = getPoint(point1,globaldata)
    ptbx,ptby = getPoint(point2,globaldata)
    ptx = deltaX(ptax,ptbx)**2
    pty = deltaY(ptay,ptby)**2
    result = math.sqrt(ptx + pty)
    return result

def getPerpendicularPoint(idx,globaldata,normal):
    wallptData = getWallPointArray(globaldata)
    wallptDataOr = wallptData
    wallptData = flattenList(wallptData)
    pts = findNearestNeighbourWallPoints(idx,globaldata,wallptData,wallptDataOr)
    mainpt = getPointxy(idx,globaldata)
    mainptx = float(mainpt.split(",")[0])
    mainpty = float(mainpt.split(",")[1])
    pts1x = float(pts[0].split(",")[0])
    pts1y = float(pts[0].split(",")[1])
    pts2x = float(pts[1].split(",")[0])
    pts2y = float(pts[1].split(",")[1])
    if normal:
        return perpendicularPt(pts1x,pts2x,mainptx,pts1y,pts2y,mainpty)
    else:
        return midPt(pts1x,pts2x,pts1y,pts2y)

def getPerpendicularPointManual(pt,globaldata,normal,quadrant):
    wallptData = getWallPointArray(globaldata)
    wallptDataOr = wallptData
    wallptData = flattenList(wallptData)
    pts = findNearestNeighbourWallPointsManual(pt,globaldata,wallptData,wallptDataOr)
    mainptx = pt[0]
    mainpty = pt[1]
    pts1x = float(pts[0].split(",")[0])
    pts1y = float(pts[0].split(",")[1])
    pts2x = float(pts[1].split(",")[0])
    pts2y = float(pts[1].split(",")[1])
    if normal:
        pptx,ppty = perpendicularPt(pts1x,pts2x,mainptx,pts1y,pts2y,mainpty)
        if quadrantContains(quadrant,(pptx,ppty)):
            return pptx,ppty
        else:
            return None
    else:
        return midPt(pts1x,pts2x,pts1y,pts2y)

def quadrantContains(quadrant,pt):
    quadpoly = shapely.geometry.Polygon(quadrant)
    ptpoly = shapely.geometry.Point(pt)
    if quadpoly.contains(ptpoly):
        return True
    else:
        return False

def flattenList(ptdata):
    return list(itertools.chain.from_iterable(ptdata))

def feederData(wallpts,wallptData):
    wallpt = wallpts[0]
    for idx,itm in enumerate(wallptData):
        if wallpt in itm:
            return (itm.index(wallpts[0]),itm.index(wallpts[1]),itm.index(wallpts[2]),idx,wallpts[0],wallpts[1])

def distance(ax,ay,bx,by):
    return math.sqrt((ax - bx)**2 + (ay - by)**2)

def undelimitXY(a):
    finallist = []
    for itm in a:
        cord = []
        cord.append(float(itm.split(",")[0]))
        cord.append(float(itm.split(",")[1]))
        finallist.append(cord)
    return finallist

def findNearestPoint(ptAtt,splineArray):
    if len(splineArray) == 0:
        print("Warning no bspline points were available")
        return False
    cord = {"x":0,"y":0}
    dist = distance(ptAtt[0],ptAtt[1],splineArray[0][0],splineArray[0][1])
    cord["x"] = splineArray[0][0]
    cord["y"] = splineArray[0][1]
    for itm in splineArray:
        distcurr = distance(ptAtt[0],ptAtt[1],itm[0],itm[1])
        if distcurr > dist:
            None
        else:
            dist = distcurr
            cord["x"] = itm[0]
            cord["y"] = itm[1]
    return (cord["x"],cord["y"])

def save_obj(obj, name ):
    with open(name + '.json', 'w') as f:
        json.dump(obj, f)

def load_obj(name ):
    with open(name + '.json', 'r') as f:
        return json.load(f)

def isNonAeroDynamic(index, cordpt, globaldata, wallpoints):
    main_pointx,main_pointy = getPoint(index, globaldata)
    cordptx = float(cordpt.split(",")[0])
    cordpty = float(cordpt.split(",")[1])
    line = shapely.geometry.LineString([[main_pointx, main_pointy], [cordptx, cordpty]])
    responselist = []
    for item in wallpoints:
        polygonpts = []
        for item2 in item:
            polygonpts.append([float(item2.split(",")[0]), float(item2.split(",")[1])])
        polygontocheck = shapely.geometry.Polygon(polygonpts)
        merged = linemerge([polygontocheck.boundary, line])
        borders = unary_union(merged)
        polygons = polygonize(borders)
        i = 0
        for p in polygons:
            i = i + 1
        if i == 1:
            responselist.append(False)
        else:
            responselist.append(True)
    if True in responselist:
        return True
    else:
        return False

def findNearestNeighbourWallPoints(idx,globaldata,wallptData,wallptDataOr):
    ptx,pty = getPoint(idx,globaldata)
    leastdt,leastidx = 1000,1000
    for itm in wallptData:
        if not isNonAeroDynamic(idx,itm,globaldata,wallptDataOr):
            itmx = float(itm.split(",")[0])
            itmy = float(itm.split(",")[1])
            ptDist = math.sqrt((deltaX(itmx,ptx) ** 2) + (deltaY(itmy,pty) ** 2))
            if leastdt > ptDist:
                leastdt = ptDist
                leastidx = getIndexFromPoint(itm,globaldata)
    ptsToCheck = convertIndexToPoints(getLeftandRightPoint(leastidx,globaldata),globaldata)
    leastdt2,leastidx2 = 1000,1000
    leastptx,leastpty = getPoint(leastidx,globaldata)
    currangle = 1000
    for itm in ptsToCheck:
        if not isNonAeroDynamic(idx,itm,globaldata,wallptDataOr):
            itmx = float(itm.split(",")[0])
            itmy = float(itm.split(",")[1])
            ptDist = math.sqrt((deltaX(itmx,ptx) ** 2) + (deltaY(itmy,pty) ** 2))
            anglecal = angle(ptx,pty,leastptx,leastpty,itmx,itmy)
            if currangle == 1000:
                currangle = anglecal
                leastidx2 = getIndexFromPoint(itm,globaldata)
            elif anglecal < currangle:
                currangle = anglecal
                leastidx2 = getIndexFromPoint(itm,globaldata)
    if leastidx > leastidx2 and leastidx2 != 1:
        leastidx,leastidx2 = leastidx2,leastidx
    if leastidx == 1 and leastidx2 > 1:
        leastidx,leastidx2 = leastidx2,leastidx
    return convertIndexToPoints([leastidx,leastidx2],globaldata)
    
def findNearestNeighbourWallPointsManual(pt,globaldata,wallptData,wallptDataOr):
    ptx,pty = pt[0],pt[1]
    leastdt,leastidx = 1000,1000
    for itm in wallptData:
        itmx = float(itm.split(",")[0])
        itmy = float(itm.split(",")[1])
        ptDist = math.sqrt((deltaX(itmx,ptx) ** 2) + (deltaY(itmy,pty) ** 2))
        if leastdt > ptDist:
            leastdt = ptDist
            leastidx = getIndexFromPoint(itm,globaldata)
    ptsToCheck = convertIndexToPoints(getLeftandRightPoint(leastidx,globaldata),globaldata)
    leastdt2,leastidx2 = 1000,1000
    leastptx,leastpty = getPoint(leastidx,globaldata)
    currangle = 1000
    for itm in ptsToCheck:
        itmx = float(itm.split(",")[0])
        itmy = float(itm.split(",")[1])
        ptDist = math.sqrt((deltaX(itmx,ptx) ** 2) + (deltaY(itmy,pty) ** 2))
        anglecal = angle(ptx,pty,leastptx,leastpty,itmx,itmy)
        if currangle == 1000:
            currangle = anglecal
            leastidx2 = getIndexFromPoint(itm,globaldata)
        elif anglecal < currangle:
            currangle = anglecal
            leastidx2 = getIndexFromPoint(itm,globaldata)
    if leastidx > leastidx2 and leastidx2 != 1:
        leastidx,leastidx2 = leastidx2,leastidx
    if leastidx == 1 and leastidx2 > 1:
        leastidx,leastidx2 = leastidx2,leastidx
    return convertIndexToPoints([leastidx,leastidx2],globaldata)

def getLeftandRightPoint(index,globaldata):
    index = int(index)
    ptdata = globaldata[index]
    leftpt = ptdata[3]
    rightpt = ptdata[4]
    nbhs = []
    nbhs.append(leftpt)
    nbhs.append(rightpt)
    return nbhs

def perpendicularPt(x1,x2,x3,y1,y2,y3):
    k = ((y2-y1) * (x3-x1) - (x2-x1) * (y3-y1)) / ((y2-y1)**2 + (x2-x1)**2)
    x4 = x3 - k * (y2-y1)
    y4 = y3 + k * (x2-x1)
    return x4,y4

def midPt(x1,x2,y1,y2):
    x3 = (x1+x2)/2
    y3 = (y1+y2)/2
    return x3,y3

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

def angle(x1, y1, x2, y2, x3, y3):
    a = np.array([x1, y1])
    b = np.array([x2, y2])
    c = np.array([x3, y3])

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)

def getBoundingBoxOfQuadrant(index,globaldata):
    toplx = float(globaldata[index][15])
    toply = float(globaldata[index][16])
    bottomrx = float(globaldata[index][17])
    bottomry = float(globaldata[index][18])
    toprx = bottomrx
    topry = toply
    bottomlx = toplx
    bottomly = bottomry
    topl = (toplx,toply)
    topr = (toprx,topry)
    bottoml = (bottomlx,bottomly)
    bottomr = (bottomrx,bottomry)
    return (topl,topr,bottomr,bottoml)

def getNorthWestQuadrant(index,globaldata):
    box = getBoundingBoxOfQuadrant(index,globaldata)
    midx,midy = getCentroidOfQuadrant(index,globaldata)
    topl = box[0]
    bottomr = (midx,midy)
    topr = (bottomr[0],topl[1])
    bottoml = (topl[0],bottomr[1])
    return (topl,topr,bottomr,bottoml)

def getNorthEastQuadrant(index,globaldata):
    box = getBoundingBoxOfQuadrant(index,globaldata)
    midx,midy = getCentroidOfQuadrant(index,globaldata)
    topr = box[1]
    bottoml = (midx,midy)
    topl = (bottoml[0],topr[1])
    bottomr = (topr[0],bottoml[1])
    return (topl,topr,bottomr,bottoml)

def getSouthWestQuadrant(index,globaldata):
    box = getBoundingBoxOfQuadrant(index,globaldata)
    midx,midy = getCentroidOfQuadrant(index,globaldata)
    bottoml = box[3]
    topr = (midx,midy)
    topl = (bottoml[0],topr[1])
    bottomr = (topr[0],bottoml[1])
    return (topl,topr,bottomr,bottoml)

def getSouthEastQuadrant(index,globaldata):
    box = getBoundingBoxOfQuadrant(index,globaldata)
    midx,midy = getCentroidOfQuadrant(index,globaldata)
    bottomr = box[2]
    topl = (midx,midy)
    topr = (bottomr[0],topl[1])
    bottoml = (topl[0],bottomr[1])
    return (topl,topr,bottomr,bottoml)

def getPerpendicularPointsFromQuadrants(index,globaldata):
    NWQ = getNorthWestQuadrant(index,globaldata)
    NEQ = getNorthEastQuadrant(index,globaldata)
    SWQ = getSouthWestQuadrant(index,globaldata)
    SEQ = getSouthEastQuadrant(index,globaldata)
    ptx,pty = getPoint(index,globaldata)
    pt = (ptx,pty)
    if len(set(NWQ)) < 4 or len(set(NEQ)) < 4 or len(set(SEQ)) < 4 or len(set(SWQ)) < 4:
        print("Warning point index: " + str(index) + " has same NW and SE bounding box")
        exit()

    perPoints = []
    walldata = getWallPointArray(globaldata)
    if doesItIntersect(index, NWQ,globaldata,walldata):
        centercord = getCentroidOfQuadrantManual(globaldata, NWQ)
        ppp = None
        # ppp = getPerpendicularPointManual(centercord,globaldata,True,NWQ)
        if ppp is None:
            perPoints.append((centercord,NWQ,pt))
        else:
            perPoints.append((ppp,NWQ,pt))
    if doesItIntersect(index, NEQ,globaldata,walldata):
        centercord = getCentroidOfQuadrantManual(globaldata, NEQ)
        ppp = None
        # ppp = getPerpendicularPointManual(centercord,globaldata,True,NEQ)
        if ppp is None:
            perPoints.append((centercord,NEQ,pt))
        else:
            perPoints.append((ppp,NEQ,pt))
    if doesItIntersect(index, SWQ,globaldata,walldata):
        centercord = getCentroidOfQuadrantManual(globaldata, SWQ)
        ppp = None
        # ppp = getPerpendicularPointManual(centercord,globaldata,True,SWQ)
        if ppp is None:
            perPoints.append((centercord,SWQ,pt))
        else:
            perPoints.append((ppp,SWQ,pt))
    if doesItIntersect(index, SEQ,globaldata,walldata):
        centercord = getCentroidOfQuadrantManual(globaldata, SEQ)
        ppp = None
        # ppp = getPerpendicularPointManual(centercord,globaldata,True,SEQ)
        if ppp is None:
            perPoints.append((centercord,SEQ,pt))
        else:
            perPoints.append((ppp,SEQ,pt))
    return perPoints

def getCentroidOfQuadrant(index,globaldata):
    quadrant = getBoundingBoxOfQuadrant(index,globaldata)
    midx = quadrant[0][0] + quadrant[2][0]
    midx = midx / 2
    midy = quadrant[0][1] + quadrant[2][1]
    midy = midy / 2
    return midx,midy

def getCentroidOfQuadrantManual(globaldata,quadrant):
    midx = quadrant[0][0] + quadrant[2][0]
    midx = midx / 2
    midy = quadrant[0][1] + quadrant[2][1]
    midy = midy / 2
    return midx,midy

def doesItIntersect(idx, quadrant, globaldata, wallpoints):
    quadrantpoly = shapely.geometry.Polygon(quadrant)
    getPtx,getPty = getPoint(idx,globaldata)
    pttocheck = shapely.geometry.Point([getPtx,getPty])
    responselist = []
    if quadrantpoly.contains(pttocheck):
        responselist.append(False)
    else:
        for item in wallpoints:
            polygonpts = []
            for item2 in item:
                polygonpts.append([float(item2.split(",")[0]), float(item2.split(",")[1])])
            polygontocheck = shapely.geometry.Polygon(polygonpts)
            response = polygontocheck.intersects(quadrantpoly)
            response = True
            if response:
                responselist.append(True)
            else:
                responselist.append(False)
    if True in responselist:
        return True
    else:
        return False

def convertToSuperNicePoints(quadrant,data):
    quadCheck = quadrant[1]
    finallist = []
    for itm in data:
        if quadrantContains(quadCheck,itm):
            finallist.append(itm)
        else:
            None
    return finallist