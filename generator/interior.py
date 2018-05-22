from balance import *
from misc import *

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

def interiorBalance(index,globaldata,hashtable,item):
    currentneighbours = getNeighbours(index, globaldata)
    currentcord = item
    _,_,_,_,xposvals = deltaNeighbourCalculation(currentneighbours,currentcord,True,False)
    _,_,_,_,xnegvals = deltaNeighbourCalculation(currentneighbours,currentcord,True,True)
    _,_,_,_,yposvals = deltaNeighbourCalculation(currentneighbours,currentcord,False,False)
    _,_,_,_,ynegvals = deltaNeighbourCalculation(currentneighbours,currentcord,False,True)
    xposw = conditionCheckWithNeighbours(index,globaldata,item,xposvals)
    xnegw = conditionCheckWithNeighbours(index,globaldata,item,xnegvals)
    yposw = conditionCheckWithNeighbours(index,globaldata,item,yposvals)
    ynegw = conditionCheckWithNeighbours(index,globaldata,item,ynegvals)
    try:
        if(xposw >= 20 or xnegw >= 20 or yposw >= 20 or ynegw >= 20):
            if(xposw >= 20):
                totalnbhs = []
                for itm in xposvals:
                    totalnbhs = totalnbhs + getNeighbours(hashtable.index(itm), globaldata)
                totalnbhs = list(set(totalnbhs) - set([item]) - set(xposvals))
                _,_,_,_,newxposvals = deltaNeighbourCalculation(totalnbhs,currentcord,True,False)
                newxposvals = minCondition(index,globaldata,currentcord,newxposvals,20)
                if(len(newxposvals) != 0):
                    appendNeighbours(newxposvals[:1], index, globaldata)
                else:
                    newxposvals = minCondition(index,globaldata,currentcord,newxposvals,xposw)
                    appendNeighbours(newxposvals[:1], index, globaldata)
                    print(currentcord,index)
            if(xnegw >= 20):
                totalnbhs = []
                for itm in xnegvals:
                    totalnbhs = totalnbhs + getNeighbours(hashtable.index(itm), globaldata)
                totalnbhs = list(set(totalnbhs) - set([item]) - set(xnegvals))
                _,_,_,_,newxnegvals = deltaNeighbourCalculation(totalnbhs,currentcord,True,True)
                newxnegvals = minCondition(index,globaldata,currentcord,newxposvals,20)
                if(len(newxnegvals) != 0):
                    appendNeighbours(newxnegvals[:1], index, globaldata)
                else:
                    newxnegvals = minCondition(index,globaldata,currentcord,newxnegvals,xposw)
                    appendNeighbours(newxnegvals[:1], index, globaldata)
            if(yposw >= 20):
                totalnbhs = []
                for itm in yposvals:
                    totalnbhs = totalnbhs + getNeighbours(hashtable.index(itm), globaldata)
                totalnbhs = list(set(totalnbhs) - set([item]) - set(xposvals))
                _,_,_,_,newyposvals = deltaNeighbourCalculation(totalnbhs,currentcord,True,False)
                newyposvals = minCondition(index,globaldata,currentcord,newyposvals,20)
                if(len(newyposvals) != 0):
                    appendNeighbours(newyposvals[:1], index, globaldata)
                else:
                    newyposvals = minCondition(index,globaldata,currentcord,newyposvals,xposw)
                    appendNeighbours(newyposvals[:1], index, globaldata)
            if(ynegw >= 20):
                totalnbhs = []
                for itm in ynegvals:
                    totalnbhs = totalnbhs + getNeighbours(hashtable.index(itm), globaldata)
                totalnbhs = list(set(totalnbhs) - set([item]) - set(ynegvals))
                _,_,_,_,newynegvals = deltaNeighbourCalculation(totalnbhs,currentcord,True,True)
                newynegvals = minCondition(index,globaldata,currentcord,newynegvals,20)
                if(len(newynegvals) != 0):
                    appendNeighbours(newynegvals[:1], index, globaldata)
                else:
                    newynegvals = minCondition(index,globaldata,currentcord,newynegvals,xposw)
                    appendNeighbours(newynegvals[:1], index, globaldata)
    except TypeError:
        pass
    # print(xpos,ypos,xneg,yneg)
    xpos,ypos,xneg,yneg,_ = deltaNeighbourCalculation(currentneighbours,currentcord,False,False)
    if(xpos < 4 or ypos < 4 or xneg < 4 or yneg < 4):
        currentnewneighbours = []
        # print("Old")
        # print(xpos,ypos,xneg,yneg)
        for item in currentneighbours:
            itemsneighbours = getNeighbours(hashtable.index(item), globaldata)
            currentnewneighbours = currentnewneighbours + list(set(itemsneighbours) - set(currentneighbours) - set(currentnewneighbours) - set([currentcord]))
        currentnewneighbours = currentnewneighbours
        if(xpos < 4):
            _,_,_,_,temp = deltaNeighbourCalculation(currentnewneighbours,currentcord,True,False)
            w,_ = conditionCheck(index,globaldata,currentcord)
            shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
            # shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(4 - xpos)], index, globaldata)
        if(xneg < 4):
            _,_,_,_,temp = deltaNeighbourCalculation(currentnewneighbours,currentcord,True,True)
            w,_ = conditionCheck(index,globaldata,currentcord)
            shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
            # shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(4 - xneg)], index, globaldata)
        if(ypos < 4):
            _,_,_,_,temp = deltaNeighbourCalculation(currentnewneighbours,currentcord,True,False)
            w,_ = conditionCheck(index,globaldata,currentcord) 
            shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
            # shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(4 - ypos)], index, globaldata)
        if(yneg < 4):
            _,_,_,_,temp = deltaNeighbourCalculation(currentnewneighbours,currentcord,True,True)
            w,_ = conditionCheck(index,globaldata,currentcord)
            shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
            # shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(4 - yneg)], index, globaldata)
        xpos,ypos,xneg,yneg,_ = deltaNeighbourCalculation(getNeighbours(hashtable.index(item), globaldata), currentcord, False, False)
        if(xpos < 4 or ypos < 4 or xneg < 4 or yneg < 4):
            None