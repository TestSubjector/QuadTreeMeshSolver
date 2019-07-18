import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

def writeNormalsToText(globaldata, configData):
    with open("file.dat", "w+") as text_file:
        for idx,_ in enumerate(globaldata):
            if idx > 0:
                flag = core.getFlag(idx,globaldata)
                if(flag == 0):
                    x,y = core.getPoint(idx,globaldata)
                    nx,ny = core.normalCalculation(idx,globaldata,True, configData)
                    text_file.write("{} {} {} {}\n".format(x, y, nx, ny))

def writeNormalsAllCustom(globaldata, configData):
    with open("file.dat", "w+") as text_file:
        for idx,_ in enumerate(globaldata):
            if idx > 0:
                flag = core.getFlag(idx,globaldata)
                if flag == 0:
                    x,y = core.getPoint(idx,globaldata)
                    nx,ny = core.normalCalculation(idx,globaldata,True, configData)
                    text_file.write("{} {} {} {}\n".format(x, y, nx, ny))
                elif flag == 1:
                    x,y = core.getPoint(idx,globaldata)
                    nx, ny = core.getNormals(idx, globaldata, configData)
                    if nx != 0 and ny != 1:
                        text_file.write("{} {} {} {}\n".format(x, y, nx, ny))

## To Plot
# plot 'file.dat' using 1:2:3:4 with vectors head filled lt 2

def writeConditionValuesForWall(globaldata, configData):
    for idx,itm in enumerate(globaldata):
        if idx > 0:
            flag = core.getFlag(idx,globaldata)
            if(flag == 0):
                x,y = core.getPoint(idx,globaldata)
                xpos = core.conditionNumberOfXPos(idx,globaldata, configData)
                xneg = core.conditionNumberOfXNeg(idx,globaldata, configData)
                xposcount = len(core.getXPosPoints(idx,globaldata, configData))
                xnegcount = len(core.getXNegPoints(idx,globaldata, configData))
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