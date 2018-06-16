import argparse
from progress import printProgressBar
from separatormisc import *


def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()

    print("Loading Data")

    file1 = open(args.input or "preprocessorfile.txt", "r")
    data = file1.read()
    globaldata = ["start"]
    splitdata = data.split("\n")
    splitdata = splitdata[:-1]

    print("Processed Pre-Processor File")
    print("Converting to readable format")

    for idx, itm in enumerate(splitdata):
        printProgressBar(idx, len(splitdata) - 1,
                         prefix='Progress:', suffix='Complete', length=50)
        itm = itm.split(" ")
        itm.pop(-1)
        entry = itm
        globaldata.append(entry)

    print("Data Converted")

    print("Detecting Problem Points")

    # problempts = getProblemPoints(globaldata,100,1)
    problempts = [1029, 1091, 1104, 1129, 1140, 1602, 1636, 1782, 2089, 2138, 2162, 2255, 2261,
                  2327, 3198, 3246, 3336, 3355, 3846, 3874, 4022, 4279, 4320, 4342, 4488, 4492, 4541, 4681]
    # problempts = []
    problempts = [x + 1 for x in problempts]
    # print(problempts)
    print("Found", len(problempts), "problem points.")

    # for ptitms in globaldata[640:]:
    #     if(int(ptitms[3]) != 1):
    #         continue
    #     ptitm = int(ptitms[0])
    #     pxy = ptitms[1:3]
    #     threshold = 100
    #     xpos = getWeightedInteriorConditionValueofXPos(ptitm,globaldata)
    #     xneg = getWeightedInteriorConditionValueofXNeg(ptitm,globaldata)
    #     ypos = getWeightedInteriorConditionValueofYPos(ptitm,globaldata)
    #     yneg = getWeightedInteriorConditionValueofYNeg(ptitm,globaldata)
    #     dSPointXPos = getDXPosPoints(ptitm, globaldata)
    #     dSPointXNeg = getDXNegPoints(ptitm, globaldata)
    #     dSPointYPos = getDYPosPoints(ptitm, globaldata)
    #     dSPointYNeg = getDYNegPoints(ptitm, globaldata)
    #     if(xneg > threshold or xpos > threshold or ypos > threshold or yneg > threshold):
    #         print(ptitm,pxy, len(dSPointXPos),xpos,len(dSPointXNeg),xneg,len(dSPointYPos),ypos,len(dSPointYNeg),yneg)
    #         print(getNeighbours(ptitm,globaldata))

    globaldata = cleanNeighbours(globaldata[1:])

    if(len(problempts) != 0):
        globaldata = nukePoints(globaldata, problempts, 25, 1)

    globaldata = deletePoints(globaldata, problempts)

    currentindex = ["start"]
    oldindex = ["start"]

    for itm in globaldata[1:]:
        currentindex.append(int(itm[0]))
        oldindex.append(int(itm[0]))
        # Not storing the removed points or that specific index

    # for item in currentindex[1:]:
    #     print(currentindex[int(item)])

    count = 0
    for itm in problempts:
        templist = currentindex[int(itm + count):]
        # print(itm - int(templist[0]))
        templist = [x - 1 for x in templist]
        # print(templist[0])
        currentindex[int(itm + count):] = templist
        count = count - 1

    for itsval, item in enumerate(oldindex):
        printProgressBar(itsval, len(oldindex) - 1,
                         prefix='Progress:', suffix='Complete', length=50)
        if(itsval > 0):  # Skip the start index
            for index, individualitem in enumerate(globaldata):
                if(index > 0):
                    for idx2, itm2 in enumerate(individualitem):
                        if(idx2 < 1 or idx2 > 11):
                            if(int(itm2) == int(item)):
                                if(int(item) != int(currentindex[itsval])):
                                    globaldata[index][idx2] = int(
                                        currentindex[itsval])
                        else:
                            if(getPointFlag(index, globaldata) == 2):
                                if(idx2 == 3 or idx2 == 4):
                                    if(int(itm2) == int(item)):
                                        if(int(item) != int(currentindex[itsval])):
                                            globaldata[index][idx2] = int(
                                                currentindex[itsval])

    globaldata.pop(0)
    globaldata = cleanNeighbours(globaldata)

    for ptitms in globaldata[640:]:
        if(int(ptitms[5]) != 1):
            continue
        ptitm = int(ptitms[0])
        pxy = ptitms[1:3]
        threshold = 100
        xpos = getWeightedInteriorConditionValueofXPos(ptitm, globaldata)
        xneg = getWeightedInteriorConditionValueofXNeg(ptitm, globaldata)
        ypos = getWeightedInteriorConditionValueofYPos(ptitm, globaldata)
        yneg = getWeightedInteriorConditionValueofYNeg(ptitm, globaldata)
        dSPointXPos = getDXPosPoints(ptitm, globaldata)
        dSPointXNeg = getDXNegPoints(ptitm, globaldata)
        dSPointYPos = getDYPosPoints(ptitm, globaldata)
        dSPointYNeg = getDYNegPoints(ptitm, globaldata)
        if(xneg > threshold or xpos > threshold or ypos > threshold or yneg > threshold):
            print(ptitm, pxy, len(dSPointXPos), xpos, len(dSPointXNeg),
                  xneg, len(dSPointYPos), ypos, len(dSPointYNeg), yneg)
            print(getNeighbours(ptitm, globaldata))

    with open("preprocessorfile_separator.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")


if __name__ == "__main__":
    main()
