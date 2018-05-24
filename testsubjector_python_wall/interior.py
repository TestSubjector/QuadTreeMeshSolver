from balance import *
from misc import *
from logger import writeLog

def deltaX(xcord,orgxcord):
    return float(xcord - orgxcord)

def deltaY(ycord,orgycord):
    return float(ycord - orgycord)

def deltaNeighbourCalculation(currentneighbours,currentcord,isxcord,isnegative):
    xpos,xneg,ypos,yneg = 0,0,0,0
    temp = []
    for item in currentneighbours:
        if((deltaX(float(currentcord.split(",")[0]), float(item.split(",")[0]))) <= 0):
            if(isxcord and not isnegative):
                temp.append(item)
            xpos = xpos + 1
        if((deltaX(float(currentcord.split(",")[0]), float(item.split(",")[0]))) >= 0):
            if(isxcord and isnegative):
                temp.append(item)
            xneg = xneg + 1
        if((deltaY(float(currentcord.split(",")[1]), float(item.split(",")[1]))) <= 0):
            if(not isxcord and not isnegative):
                temp.append(item)
            ypos = ypos + 1
        if((deltaY(float(currentcord.split(",")[1]), float(item.split(",")[1]))) >= 0):
            if(not isxcord and isnegative):
                temp.append(item)
            yneg = yneg + 1
    return xpos,ypos,xneg,xneg,temp

def interiorBalanceXPos(index,globaldata,hashtable,item,count,tolerant):
    tolerant = float(tolerant)
    currentneighbours = getNeighbours(index, globaldata)
    currentcord = item
    _,_,_,_,xposvals = deltaNeighbourCalculation(currentneighbours,currentcord,True,False)
    xposw = conditionCheckWithNeighbours(index,globaldata,item,xposvals)
    try:
        if(xposw >= tolerant):
            totalnbhs = []
            for itm in xposvals:
                totalnbhs = totalnbhs + getNeighbours(hashtable.index(itm) - 1, globaldata)
            totalnbhs = list(set(totalnbhs) - set([item]) - set(xposvals))
            _,_,_,_,newxposvals = deltaNeighbourCalculation(totalnbhs,currentcord,True,False)
            newxposvals = minCondition(index,globaldata,currentcord,newxposvals,tolerant)
            if(len(newxposvals) != 0):
                appendNeighbours(newxposvals[:1], index, globaldata)
                xpos,_,_,_,_ = deltaNeighbourCalculation(currentneighbours,currentcord,True,False)
                currentnewneighbours = []
                for item in currentneighbours:
                    itemsneighbours = getNeighbours(hashtable.index(item) - 1, globaldata)
                    currentnewneighbours = currentnewneighbours + list(set(itemsneighbours) - set(currentneighbours) - set(currentnewneighbours) - set([currentcord]))
                if(xpos < 4):
                    try:
                        _,_,_,_,temp = deltaNeighbourCalculation(currentnewneighbours,currentcord,True,False)
                        shortestnewneighbours = minDistance(temp,currentcord)
                        if(len(shortestnewneighbours) == 0):
                            print("Couldn't find neighbour of neighbours which can reduce the xpos condition for the point (",currentcord,")")
                        appendNeighbours(shortestnewneighbours[:(4 - xpos)], index, globaldata) 
                        xpos,_,_,_,_ = deltaNeighbourCalculation(getNeighbours(hashtable.index(item) - 1, globaldata), currentcord, False, False)
                        if(xpos < 4 and count < 3):
                            interiorBalanceXPos(hashtable.index(currentcord) - 1,globaldata,hashtable,currentcord,count+1,tolerant)
                        elif(xpos < 4 and count == 2):
                            print("#2 Couldn't find neighbour of neighbours even after 2 recursions which can reduce the xpos condition for the point (",currentcord,")")
                    except TypeError:
                            print("Couldn't find neighbour of neighbours which can reduce the xpos condition for the point (",currentcord,")")
            else:
                print("Couldn't satisfy the xpos tolerant value ",tolerant," for point (",currentcord, ")")
    except TypeError:
        pass
def interiorBalanceXNeg(index,globaldata,hashtable,item,count,tolerant):
    tolerant = float(tolerant)
    currentneighbours = getNeighbours(index, globaldata)
    currentcord = item
    _,_,_,_,xnegvals = deltaNeighbourCalculation(currentneighbours,currentcord,True,True)
    xnegw = conditionCheckWithNeighbours(index,globaldata,item,xnegvals)
    try:
        if(xnegw >= tolerant):
            totalnbhs = []
            for itm in xnegvals:
                totalnbhs = totalnbhs + getNeighbours(hashtable.index(itm) - 1, globaldata)
            totalnbhs = list(set(totalnbhs) - set([item]) - set(xnegvals))
            _,_,_,_,newxnegvals = deltaNeighbourCalculation(totalnbhs,currentcord,True,True)
            newxnegvals = minCondition(index,globaldata,currentcord,newxnegvals,tolerant)
            if(len(newxnegvals) != 0):
                appendNeighbours(newxnegvals[:1], index, globaldata)
                xneg,_,_,_,_ = deltaNeighbourCalculation(currentneighbours,currentcord,True,True)
                currentnewneighbours = []
                for item in currentneighbours:
                    itemsneighbours = getNeighbours(hashtable.index(item) - 1, globaldata)
                    currentnewneighbours = currentnewneighbours + list(set(itemsneighbours) - set(currentneighbours) - set(currentnewneighbours) - set([currentcord]))
                if(xneg < 4):
                    try:
                        _,_,_,_,temp = deltaNeighbourCalculation(currentnewneighbours,currentcord,True,False)
                        shortestnewneighbours = minDistance(temp,currentcord)
                        if(len(shortestnewneighbours) == 0):
                            print("Couldn't find neighbour of neighbours which can reduce the xneg condition for the point (",currentcord,")")
                        appendNeighbours(shortestnewneighbours[:(4 - xneg)], index, globaldata) 
                        xneg,_,_,_,_ = deltaNeighbourCalculation(getNeighbours(hashtable.index(item) - 1, globaldata), currentcord, False, False)
                        if(xneg < 4 and count < 3):
                            interiorBalanceXNeg(hashtable.index(currentcord) - 1,globaldata,hashtable,currentcord,count+1,tolerant)
                        elif(xneg < 4 and count == 2):
                            print("#2 Couldn't find neighbour of neighbours even after 2 recursions which can reduce the xneg condition for the point (",currentcord,")")
                    except TypeError:
                            print("Couldn't find neighbour of neighbours which can reduce the xneg condition for the point (",currentcord,")")
            else:
                print("Couldn't satisfy the xneg tolerant value ",tolerant," for point (",currentcord, ")")
    except TypeError:
        pass
def interiorBalanceYPos(index,globaldata,hashtable,item,count,tolerant):
    tolerant = float(tolerant)
    currentneighbours = getNeighbours(index, globaldata)
    currentcord = item
    _,_,_,_,yposvals = deltaNeighbourCalculation(currentneighbours,currentcord,False,False)
    yposw = conditionCheckWithNeighbours(index,globaldata,item,yposvals)
    try:
        if(yposw >= tolerant):
            totalnbhs = []
            for itm in yposvals:
                totalnbhs = totalnbhs + getNeighbours(hashtable.index(itm) - 1, globaldata)
            totalnbhs = list(set(totalnbhs) - set([item]) - set(yposvals))
            _,_,_,_,newyposvals = deltaNeighbourCalculation(totalnbhs,currentcord,False,False)
            newyposvals = minCondition(index,globaldata,currentcord,newyposvals,tolerant)
            if(len(newyposvals) != 0):
                appendNeighbours(newyposvals[:1], index, globaldata)
                ypos,_,_,_,_ = deltaNeighbourCalculation(currentneighbours,currentcord,False,False)
                currentnewneighbours = []
                for item in currentneighbours:
                    itemsneighbours = getNeighbours(hashtable.index(item) - 1, globaldata)
                    currentnewneighbours = currentnewneighbours + list(set(itemsneighbours) - set(currentneighbours) - set(currentnewneighbours) - set([currentcord]))
                if(ypos < 4):
                    try:
                        _,_,_,_,temp = deltaNeighbourCalculation(currentnewneighbours,currentcord,False,False)
                        shortestnewneighbours = minDistance(temp,currentcord)
                        if(len(shortestnewneighbours) == 0):
                            print("Couldn't find neighbour of neighbours which can reduce the ypos condition for the point (",currentcord,")")
                        appendNeighbours(shortestnewneighbours[:(4 - ypos)], index, globaldata) 
                        ypos,_,_,_,_ = deltaNeighbourCalculation(getNeighbours(hashtable.index(item) - 1, globaldata), currentcord, False, False)
                        if(ypos < 4 and count < 3):
                            interiorBalanceYPos(hashtable.index(currentcord) - 1,globaldata,hashtable,currentcord,count+1,tolerant)
                        elif(ypos < 4 and count == 2):
                            print("#2 Couldn't find neighbour of neighbours even after 2 recursions which can reduce the ypos condition for the point (",currentcord,")")
                    except TypeError:
                            print("Couldn't find neighbour of neighbours which can reduce the ypos condition for the point (",currentcord,")")
            else:
                print("Couldn't satisfy the ypos tolerant value ",tolerant," for point (",currentcord, ")")
    except TypeError:
        pass

def interiorBalanceYNeg(index,globaldata,hashtable,item,count,tolerant):
    tolerant = float(tolerant)
    currentneighbours = getNeighbours(index, globaldata)
    currentcord = item
    _,_,_,_,ynegvals = deltaNeighbourCalculation(currentneighbours,currentcord,False,True)
    ynegw = conditionCheckWithNeighbours(index,globaldata,item,ynegvals)
    try:
        if(ynegw >= tolerant):
            totalnbhs = []
            for itm in ynegvals:
                totalnbhs = totalnbhs + getNeighbours(hashtable.index(itm) - 1, globaldata)
            totalnbhs = list(set(totalnbhs) - set([item]) - set(ynegvals))
            _,_,_,_,newynegvals = deltaNeighbourCalculation(totalnbhs,currentcord,False,True)
            newynegvals = minCondition(index,globaldata,currentcord,newynegvals,tolerant)
            if(len(newynegvals) != 0):
                appendNeighbours(newynegvals[:1], index, globaldata)
                yneg,_,_,_,_ = deltaNeighbourCalculation(currentneighbours,currentcord,False,True)
                currentnewneighbours = []
                for item in currentneighbours:
                    itemsneighbours = getNeighbours(hashtable.index(item) - 1, globaldata)
                    currentnewneighbours = currentnewneighbours + list(set(itemsneighbours) - set(currentneighbours) - set(currentnewneighbours) - set([currentcord]))
                if(yneg < 4):
                    try:
                        _,_,_,_,temp = deltaNeighbourCalculation(currentnewneighbours,currentcord,False,True)
                        shortestnewneighbours = minDistance(temp,currentcord)
                        if(len(shortestnewneighbours) == 0):
                            print("Couldn't find neighbour of neighbours which can reduce the yneg condition for the point (",currentcord,")")
                        appendNeighbours(shortestnewneighbours[:(4 - yneg)], index, globaldata) 
                        yneg,_,_,_,_ = deltaNeighbourCalculation(getNeighbours(hashtable.index(item) - 1, globaldata), currentcord, False, True)
                        if(yneg < 4 and count < 3):
                            interiorBalanceYNeg(hashtable.index(currentcord) - 1,globaldata,hashtable,currentcord,count+1,tolerant)
                        elif(yneg < 4 and count == 2):
                            print("#2 Couldn't find neighbour of neighbours even after 2 recursions which can reduce the yneg condition for the point (",currentcord,")")
                    except TypeError:
                            print("Couldn't find neighbour of neighbours which can reduce the yneg condition for the point (",currentcord,")")
            else:
                print("Couldn't satisfy the yneg tolerant value ",tolerant," for point (",currentcord, ")")
    except TypeError:
        pass