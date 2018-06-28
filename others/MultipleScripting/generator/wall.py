from misc import *
from balance import *


def printWallConditionValue(index, globaldata, hashtable):
    currentnbhs = getNeighbours(index, globaldata)
    currentcord = getPoint(index, globaldata)
    nx, ny = normalCalculation(index, hashtable, globaldata, True)
    _, _, _, ds = deltaWallNeighbourCalculation(
        index, currentnbhs, nx, ny, False, globaldata
    )
    _, _, _, ds2 = deltaWallNeighbourCalculation(
        index, currentnbhs, nx, ny, True, globaldata
    )
    dsCondN = conditionCheckWithNeighboursWall(index, globaldata, ds, nx, ny)
    dsCondP = conditionCheckWithNeighboursWall(index, globaldata, ds2, nx, ny)
    if dsCondP > 10:
        nbhofnbh = []
        for nbh in ds2:
            items = getNeighbours(getIndexOf(nbh, hashtable), globaldata)
            nbhofnbh = nbhofnbh + list(
                set(items) - set([currentcord]) - set(currentnbhs)
            )
        # print(nbhofnbh)
        pointsSurvived = minCondition(
            index, hashtable, globaldata, nbhofnbh, 10, nx, ny
        )
        if len(pointsSurvived) == 0:
            print("\n Problems")
        else:
            pointToBeAdded = pointsSurvived
            # print(pointToBeAdded)
            appendNeighbours(list([pointToBeAdded]), index, globaldata)

    if dsCondN > 10:
        nbhofnbh = []
        for nbh in ds:
            items = getNeighbours(getIndexOf(nbh, hashtable), globaldata)
            nbhofnbh = nbhofnbh + list(
                set(items) - set([currentcord]) - set(currentnbhs)
            )
        # print(nbhofnbh)
        pointsSurvived = minCondition(
            index, hashtable, globaldata, nbhofnbh, 10, nx, ny
        )
        if len(pointsSurvived) == 0:
            print("\n Problems")
        else:
            pointToBeAdded = pointsSurvived
            # print(pointToBeAdded)
            appendNeighbours(list([pointToBeAdded]), index, globaldata)

    # print(index,dsCondP,len(ds2),dsCondN,len(ds))


def printWall(index, globaldata, hashtable):
    currentnbhs = getNeighbours(index, globaldata)
    currentcord = getPoint(index, globaldata)
    nx, ny = normalCalculation(index, hashtable, globaldata, True)
    _, _, _, ds = deltaWallNeighbourCalculation(
        index, currentnbhs, nx, ny, False, globaldata
    )
    _, _, _, ds2 = deltaWallNeighbourCalculation(
        index, currentnbhs, nx, ny, True, globaldata
    )
    dsCondN = conditionCheckWithNeighboursWall(index, globaldata, ds, nx, ny)
    dsCondP = conditionCheckWithNeighboursWall(index, globaldata, ds2, nx, ny)
    if dsCondN > 10 or dsCondP > 10:
        None
        # print(index,dsCondP,len(ds2),dsCondN,len(ds))


def printOuterConditionValue(index, globaldata, hashtable):
    currentnbhs = getNeighbours(index, globaldata)
    currentcord = getPoint(index, globaldata)
    nx, ny = normalCalculation(index, hashtable, globaldata, False)
    _, _, _, ds = deltaOuterNeighbourCalculation(
        index, currentnbhs, nx, ny, False, globaldata
    )
    _, _, _, ds2 = deltaOuterNeighbourCalculation(
        index, currentnbhs, nx, ny, True, globaldata
    )
    dsCondN = conditionCheckWithNeighboursWall(index, globaldata, ds, nx, ny)
    dsCondP = conditionCheckWithNeighboursWall(index, globaldata, ds2, nx, ny)
    if dsCondP > 10:
        nbhofnbh = []
        for nbh in ds2:
            items = getNeighbours(getIndexOf(nbh, hashtable), globaldata)
            nbhofnbh = nbhofnbh + list(
                set(items) - set([currentcord]) - set(currentnbhs)
            )
        # print(nbhofnbh)
        pointsSurvived = minCondition(
            index, hashtable, globaldata, nbhofnbh, 10, nx, ny
        )
        if len(pointsSurvived) == 0:
            print("\n Problems")
        else:
            pointToBeAdded = pointsSurvived
            # print(pointToBeAdded)
            appendNeighbours(list([pointToBeAdded]), index, globaldata)

    if dsCondN > 10:
        nbhofnbh = []
        for nbh in ds:
            items = getNeighbours(getIndexOf(nbh, hashtable), globaldata)
            nbhofnbh = nbhofnbh + list(
                set(items) - set([currentcord]) - set(currentnbhs)
            )
        # print(nbhofnbh)
        pointsSurvived = minCondition(
            index, hashtable, globaldata, nbhofnbh, 10, nx, ny
        )
        if len(pointsSurvived) == 0:
            print("\n Problems")
        else:
            pointToBeAdded = pointsSurvived
            # print(pointToBeAdded)
            appendNeighbours(list([pointToBeAdded]), index, globaldata)

    # print(index,dsCondP,len(ds2),dsCondN,len(ds))


def printOuter(index, globaldata, hashtable):
    currentnbhs = getNeighbours(index, globaldata)
    currentcord = getPoint(index, globaldata)
    nx, ny = normalCalculation(index, hashtable, globaldata, False)
    _, _, _, ds = deltaOuterNeighbourCalculation(
        index, currentnbhs, nx, ny, False, globaldata
    )
    _, _, _, ds2 = deltaOuterNeighbourCalculation(
        index, currentnbhs, nx, ny, True, globaldata
    )
    dsCondN = conditionCheckWithNeighboursWall(index, globaldata, ds, nx, ny)
    dsCondP = conditionCheckWithNeighboursWall(index, globaldata, ds2, nx, ny)
    if dsCondN > 10 or dsCondP > 10:
        None
        # print(index,dsCondP,len(ds2),dsCondN,len(ds))
