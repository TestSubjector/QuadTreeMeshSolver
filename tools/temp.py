import progress
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def writeNormalsToText(globaldata):
    for idx,itm in enumerate(globaldata):
        if idx > 0:
            flag = core.getFlag(idx,globaldata)
            if(flag == 0):
                x,y = core.getPoint(idx,globaldata)
                nx,ny = core.normalCalculation(idx,globaldata,True)
                with open("file.dat", "a") as text_file:
                    text_file.writelines(str(x) + " " + str(y) + " " + str(nx) + " " + str(ny))
                    text_file.writelines("\n")


## To Plot
# plot 'file.dat' using 1:2:3:4 with vectors head filled lt 2


def writeConditionValuesForWall(globaldata):
    for idx,itm in enumerate(globaldata):
        if idx > 0:
            flag = core.getFlag(idx,globaldata)
            if(flag == 0):
                x,y = core.getPoint(idx,globaldata)
                xpos = core.getWeightedNormalConditionValueofWallXPos(idx,globaldata)
                xneg = core.getWeightedNormalConditionValueofWallXNeg(idx,globaldata)
                xposcount = len(core.getDWallXPosPoints(idx,globaldata))
                xnegcount = len(core.getDWallXNegPoints(idx,globaldata))
                if(xpos > 100 or xneg > 100 or xposcount < 3 or xnegcount < 3):
                    with open("condition.dat", "a") as text_file:
                        text_file.writelines(str(x) + " " + str(y) + " " + str(xposcount) + " " + str(xpos) + " " + str(xnegcount) + " " + str(xneg))
                        text_file.writelines("\n")

def createAdaptedFull(globaldata):
    for idx,_ in enumerate(globaldata):
        if idx > 0:
            flag = core.getFlag(idx,globaldata)
            if(flag == 0 or flag == 1):
                x,y = core.getPoint(idx,globaldata)
                with open("adapted.txt", "a") as text_file:
                    text_file.writelines(str(x) + " " + str(y) + " \n")
    with open("adapted.txt", "a") as text_file:
        text_file.writelines("1000 1000\n")
                    

def writeConditionValues(globaldata):
    writeFile = []
    for idx,itm in enumerate(globaldata):
        if idx > 0:
            flag = core.getFlag(idx,globaldata)
            if flag == 0:
                data = []
                nx,ny = core.normalCalculation(idx,globaldata,True)
                result = core.calculateNormalConditionValues(idx,globaldata,nx,ny)
                ptx,pty = core.getPoint(idx,globaldata)
                data.append(idx)
                data.append(ptx)
                data.append(pty)
                data.append(result["sposCond"])
                data.append(result["snegCond"])
                data.append(1)
                data.append(result["nnegCond"])
                writeFile.append(data)
            elif flag == 1:
                data = []
                nx,ny = core.getNormals(idx,globaldata)
                result = core.calculateNormalConditionValues(idx,globaldata,nx,ny)
                ptx,pty = core.getPoint(idx,globaldata)
                data.append(idx)
                data.append(ptx)
                data.append(pty)
                data.append(result["sposCond"])
                data.append(result["snegCond"])
                data.append(result["nposCond"])
                data.append(result["nnegCond"])
                writeFile.append(data)
            elif flag == 2:
                data = []
                nx,ny = core.normalCalculation(idx,globaldata,False)
                result = core.calculateNormalConditionValues(idx,globaldata,nx,ny)
                ptx,pty = core.getPoint(idx,globaldata)
                data.append(idx)
                data.append(ptx)
                data.append(pty)
                data.append(result["sposCond"])
                data.append(result["snegCond"])
                data.append(result["nposCond"])
                data.append(1)
                writeFile.append(data)
    with open("conditionFile.txt", "w") as text_file:
        for item1 in writeFile:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")

def writeSrikanthStyle(globaldata):
    with open("preprocessorfile_srikanth.txt", "w") as text_file:
        for idx,item1 in enumerate(globaldata):
            if idx > 0:
                item2 = item1
                item2.pop(7)
                item2.pop(7)
                item2.pop(7)
                item2.pop(7)
                item2.pop(7)
                item2.pop(7)
                text_file.writelines(["%s " % item for item in item2])
                text_file.writelines("\n") 