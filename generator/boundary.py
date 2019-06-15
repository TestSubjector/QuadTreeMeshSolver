
from misc import *

def detectOuter(hashtable, globaldata):
    print("Beginning Left and Right Detection of Outer Points")
    biggestxy = getBiggestXBiggestY(hashtable[1:])
    smallestxy = getSmallestXSmallestY(hashtable[1:])
    smallestxbiggesty = getSmallestXBiggestY(hashtable[1:])
    biggestxsmallesty = getBiggestXSmallestY(hashtable[1:])
    startindex = hashtable.index(biggestxy) - 1
    currentstatus = 1
    currentcord = biggestxy
    previouscord = biggestxy
    leftcord = "start"
    count = 0
    while True:
        count += 1
        currentneighbours = getNeighbours(hashtable.index(currentcord) - 1, globaldata)
        if currentstatus == 1:
            currentneighbours = getNeighboursDirectional(
                1, currentcord, currentneighbours
            )
            try:
                leftcord = getFarthestPoint(currentneighbours)
            except Exception:
                None
            if currentcord == smallestxbiggesty:
                currentstatus += 1
                # Switch Direction to bottom
            startindex = hashtable.index(currentcord) - 1
        elif currentstatus == 2:
            currentneighbours = getNeighboursDirectional(
                2, currentcord, currentneighbours
            )
            try:
                leftcord = getFarthestPoint(currentneighbours)
            except Exception:
                None
            if currentcord == smallestxy:
                currentstatus += 1
                # Switch Direction to bottom
            startindex = hashtable.index(currentcord) - 1
        elif currentstatus == 3:
            currentneighbours = getNeighboursDirectional(
                3, currentcord, currentneighbours
            )
            try:
                leftcord = getFarthestPoint(currentneighbours)
            except Exception:
                None
            if currentcord == biggestxsmallesty:
                currentstatus += 1
                # Switch Direction to bottom
            startindex = hashtable.index(currentcord) - 1
        elif currentstatus == 4:
            currentneighbours = getNeighboursDirectional(
                4, currentcord, currentneighbours
            )
            try:
                leftcord = getFarthestPoint(currentneighbours)
            except Exception:
                None
            if currentcord == biggestxy:
                globaldata = updateRight(
                    hashtable.index(biggestxy) - 1, globaldata, previouscord
                )
                break
            startindex = hashtable.index(currentcord) - 1
        globaldata = updateRight(startindex, globaldata, previouscord)
        globaldata = updateFlag(startindex, globaldata, 2)
        globaldata = updateLeft(startindex, globaldata, leftcord)
        previouscord = currentcord
        currentcord = leftcord
    print("Outer Points Left and Right Detection Complete")
    return hashtable, globaldata
