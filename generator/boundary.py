# from progress import *
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
    count = 0
    while True:
        count += 1
        # printProgressBar(currentstatus, 5, prefix = 'Progress:', suffix = 'Complete', length = 50)
        currentneighbours = getNeighbours(hashtable.index(currentcord) - 1, globaldata)
        # print(currentcord,currentneighbours)
        # if(currentcord=='9.375,-1.875'):
        #     break
        # print(currentneighbours)
        # print(currentcord)
        if currentstatus == 1:
            # print(currentcord)
            currentneighbours = getNeighboursDirectional(
                1, currentcord, currentneighbours
            )
            try:
                leftcord = getFarthestPoint(currentneighbours)
                # xvals = getXCordNeighbours(currentneighbours)
                # currentnewneighbours = []
                # for index, item in enumerate(xvals):
                #     if item == min(xvals):
                #         currentnewneighbours.append(currentneighbours[index])
                # currentYCords = getYCordNeighbours(currentneighbours)
                # leftcord = currentneighbours[currentYCords.index(max(currentYCords))]
                # print(leftcord)
            except Exception:
                None
            if currentcord == smallestxbiggesty:
                currentstatus += 1
                # Switch Direction to bottom
            startindex = hashtable.index(currentcord) - 1
        elif currentstatus == 2:
            # print(currentcord,currentneighbours)
            currentneighbours = getNeighboursDirectional(
                2, currentcord, currentneighbours
            )
            try:
                leftcord = getFarthestPoint(currentneighbours)
                # yvals = getYCordNeighbours(currentneighbours)
                # currentnewneighbours = []
                # for index, item in enumerate(yvals):
                #     if item == min(yvals):
                #         currentnewneighbours.append(currentneighbours[index])
                # currentXCords = getXCordNeighbours(currentneighbours)
                # leftcord = currentneighbours[currentXCords.index(min(currentXCords))]
                # print(leftcord)
            except Exception:
                None
            if currentcord == smallestxy:
                currentstatus += 1
                # Switch Direction to bottom
            startindex = hashtable.index(currentcord) - 1
        elif currentstatus == 3:
            # print(currentcord)
            currentneighbours = getNeighboursDirectional(
                3, currentcord, currentneighbours
            )
            try:
                leftcord = getFarthestPoint(currentneighbours)
                # xvals = getXCordNeighbours(currentneighbours)
                # currentnewneighbours = []
                # for index, item in enumerate(xvals):
                #     if item == max(xvals):
                #         currentnewneighbours.append(currentneighbours[index])
                # currentYCords = getYCordNeighbours(currentnewneighbours)
                # leftcord = currentnewneighbours[currentYCords.index(min(currentYCords))]
                # print(leftcord)
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
                # yvals = getYCordNeighbours(currentneighbours)
                # currentnewneighbours = []
                # for index, item in enumerate(yvals):
                #     if item == max(yvals):
                #         currentnewneighbours.append(currentneighbours[index])
                # currentXCords = getXCordNeighbours(currentnewneighbours)
                # leftcord = currentnewneighbours[currentXCords.index(max(currentXCords))]
                # print(leftcord)
            except Exception:
                None
            if currentcord == biggestxy:
                globaldata = updateRight(
                    hashtable.index(biggestxy) - 1, globaldata, previouscord
                )
                # printProgressBar(5, 5, prefix = 'Progress:', suffix = 'Complete', length = 50)
                break
            startindex = hashtable.index(currentcord) - 1
        globaldata = updateRight(startindex, globaldata, previouscord)
        globaldata = updateFlag(startindex, globaldata, 2)
        globaldata = updateLeft(startindex, globaldata, leftcord)
        previouscord = currentcord
        currentcord = leftcord
    print("Outer Points Left and Right Detection Complete")
    return hashtable, globaldata
