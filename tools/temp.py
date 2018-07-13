import core

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
                    