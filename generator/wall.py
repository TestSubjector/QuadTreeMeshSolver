from misc import *
from balance import *

def wallBalance(index,globaldata,hashtable,itemda,control,wallpoint):
    # print(index,item,control)
    currentneighbours = getNeighbours(index,globaldata)
    currentcord = itemda
    nx,ny = normalCalculation(index,currentcord,hashtable,globaldata,True)
    deltaspos,deltasneg,deltaszero,temp = deltaWallNeighbourCalculation(index,currentneighbours,currentcord,nx,ny,False,globaldata)
    if(deltaspos < control or deltasneg < control):
        newset = []
        posdiff = deltaspos
        negdiff = deltasneg
        for item in currentneighbours:
            itemnb = getNeighbours(hashtable.index(item) - 1,globaldata)
            newset = newset + itemnb
        # Filter 1
        newset = list(set(newset) - set(currentneighbours))
        newset = list(set(newset) - set([currentcord]))
        if(deltasneg < control):
            _,_,_,temp = deltaWallNeighbourCalculation(index,newset,currentcord,nx,ny,False,globaldata)
            temp = cleanWallPoints(temp,wallpoint)
            # w,_ = conditionCheck(index,globaldata,item)
            # shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
            shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(control-negdiff)],index,globaldata)
        if(deltaspos < control):
            _,_,_,temp = deltaWallNeighbourCalculation(index,newset,currentcord,nx,ny,True,globaldata)
            temp = cleanWallPoints(temp,wallpoint)
            # w,_ = conditionCheck(index,globaldata,item)
            # shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
            shortestnewneighbours = minDistance(temp,currentcord)
            appendNeighbours(shortestnewneighbours[:(control-posdiff)],index,globaldata)
        w,s = conditionCheck(index,globaldata,item)
        if(w >= 3 or s >= 3):
            if(control==6):
                print("Shit Man")
            else:
                # print(index,itemda)
                control = control + 1
                wallBalance(hashtable.index(itemda) - 1,globaldata,hashtable,itemda,control,wallpoint)

