# from progress import *
import logging
import pickle
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())


def loadWall(geometrydata,hashtable,globaldata,idf):
    log.info("Beginning Wall Point Processing")
    wallpoint = []

    index = len(hashtable)
    startpt = index
    lastpt = len(globaldata) + len(geometrydata)
    for i in range(len(geometrydata)):
        # printProgressBar(i, len(geometrydata) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        xcord = float(geometrydata[i].split()[0])
        ycord = float(geometrydata[i].split()[1])
        # print(len(geometrydata[i].split(" ")))
        # print(geometrydata[i].split(" ")[1])

        hashtable.append(str(xcord) + "," + str(ycord))
        wallpoint.append(str(xcord) + "," + str(ycord))  # Storing Wallpoints

        walldata = []
        # First Point
        if index == startpt:
            walldata.append(index)
            walldata.insert(1, xcord)
            walldata.insert(2, ycord)
            walldata.insert(3, lastpt)
            walldata.insert(4, index + 1)
            walldata.insert(5, 0)
            walldata.insert(6, idf)
            walldata.insert(7, 0)
            walldata.insert(8, 0)
            walldata.insert(9, 0)
            walldata.insert(10, 0)
            globaldata.append(walldata)
            index += 1
        # Last Point
        elif index == lastpt:
            walldata.append(index)
            walldata.insert(1, xcord)
            walldata.insert(2, ycord)
            walldata.insert(3, startpt + len(geometrydata) - 2)
            walldata.insert(4, startpt)
            walldata.insert(5, 0)
            walldata.insert(6, idf)
            walldata.insert(7, 0)
            walldata.insert(8, 0)
            walldata.insert(9, 0)
            walldata.insert(10, 0)
            globaldata.append(walldata)
            index += 1
        # Other Points
        else:
            walldata.append(index)
            walldata.insert(1, xcord)
            walldata.insert(2, ycord)
            walldata.insert(3, index - 1)
            walldata.insert(4, index + 1)
            walldata.insert(5, 0)
            walldata.insert(6, idf)
            walldata.insert(7, 0)
            walldata.insert(8, 0)
            walldata.insert(9, 0)
            walldata.insert(10, 0)
            globaldata.append(walldata)
            index += 1
    log.info("Wall Point Processed")
    return hashtable, wallpoint, globaldata


def loadInterior(data, hashtable, globaldata, index):
    log.info("Beginning Interior Point and Wall Point Neighbour Processing")
    for i in range(len(data)):
        # printProgressBar(i, len(data) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        cleandata = str(data[i]).split(" ")
        cord = (
            str(float(cleandata[1].split(",")[0]))
            + ","
            + str(float(cleandata[1].split(",")[1]))
        )
        try:
            if i != len(data) - 1:
                val = hashtable.index(cord)
                cleandata.pop(0)  # Pop index
                cleandata.pop(-1)  # Pop blank space
                cleandata.pop(-2)  # Pop number of neighbours
                cleandata.pop(0)  # Pop blank space
                cleandata.insert(0, str(int(cleandata[len(cleandata) - 1]) + 2))
                cleandata.pop(-1)
                cleandata.append(
                    str(float(hashtable[int(globaldata[val - 1][3])].split(",")[0]))
                    + ","
                    + str(float(hashtable[int(globaldata[val - 1][3])].split(",")[1]))
                )
                cleandata.append(
                    str(float(hashtable[int(globaldata[val - 1][4])].split(",")[0]))
                    + ","
                    + str(float(hashtable[int(globaldata[val - 1][4])].split(",")[1]))
                )
                globaldata[val - 1] = globaldata[val - 1] + cleandata
            else:
                val = hashtable.index(cord)
                cleandata.pop(0)
                cleandata.pop(-2)
                cleandata.pop(0)
                cleandata.insert(0, str(int(cleandata[len(cleandata) - 1]) + 2))
                cleandata.pop(-1)
                cleandata.append(
                    str(float(hashtable[int(globaldata[val - 1][3])].split(",")[0]))
                    + ","
                    + str(float(hashtable[int(globaldata[val - 1][3])].split(",")[1]))
                )
                cleandata.append(
                    str(float(hashtable[int(globaldata[val - 1][4])].split(",")[0]))
                    + ","
                    + str(float(hashtable[int(globaldata[val - 1][4])].split(",")[1]))
                )
                globaldata[val - 1] = globaldata[val - 1] + cleandata
        except Exception as err:
            if i != len(data) - 1:
                hashtable.append(cord)
                cleandata.pop(0)
                cleandata.pop(-1)
                cleandata.pop(-2)
                cleandata.pop(0)
                cleandata.insert(0, cleandata[len(cleandata) - 1])
                cleandata.pop(-1)
                cleandata.insert(0, 0)
                cleandata.insert(0, 0)
                cleandata.insert(0, 0)
                cleandata.insert(0, 0)
                cleandata.insert(0, 0)
                cleandata.insert(0, 1)
                cleandata.insert(0, 0)
                cleandata.insert(0, 0)
                cleandata.insert(0, cord.split(",")[1])
                cleandata.insert(0, cord.split(",")[0])
                cleandata.insert(0, index)
                index += 1
                globaldata.append(cleandata)
            else:
                hashtable.append(cord)
                cleandata.pop(0)
                cleandata.pop(-2)
                cleandata.pop(0)
                cleandata.insert(0, cleandata[len(cleandata) - 1])
                cleandata.pop(-1)
                cleandata.insert(0, 0)
                cleandata.insert(0, 0)
                cleandata.insert(0, 0)
                cleandata.insert(0, 0)
                cleandata.insert(0, 0)
                cleandata.insert(0, 1)
                cleandata.insert(0, 0)
                cleandata.insert(0, 0)
                cleandata.insert(0, cord.split(",")[1])
                cleandata.insert(0, cord.split(",")[0])
                cleandata.insert(0, index)
                index += 1
                globaldata.append(cleandata)
    log.info("Interior Point and Wall Point Neighbour Processed")
    return hashtable, globaldata


def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, protocol=0)

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

def checkIfInside(xcord,ycord,wallData):
    for idx,itm in enumerate(wallData):
        compare = itm.split("\t")
        compareValX = float(compare[0])
        compareValY = float(compare[1])
        if xcord == compareValX and ycord == compareValY:
            return True,idx
    return False,0