from misc import *
from balance import *

# def wallBalance(index,globaldata,hashtable,itemda,control,wallpoint):
#     # print(index,item,control)
#     currentneighbours = getNeighbours(index,globaldata)
#     currentcord = itemda
#     nx,ny = normalCalculation(index,currentcord,hashtable,globaldata,True)
#     deltaspos,deltasneg,deltaszero,temp = deltaWallNeighbourCalculation(index,currentneighbours,currentcord,nx,ny,False,globaldata)
#     if(deltaspos < control or deltasneg < control):
#         newset = []
#         posdiff = deltaspos
#         negdiff = deltasneg
#         for item in currentneighbours:
#             itemnb = getNeighbours(hashtable.index(item) - 1,globaldata)
#             newset = newset + itemnb
#         # Filter 1
#         newset = list(set(newset) - set(currentneighbours))
#         newset = list(set(newset) - set([currentcord]))
#         if(deltasneg < control):
#             _,_,_,temp = deltaWallNeighbourCalculation(index,newset,currentcord,nx,ny,False,globaldata)
#             temp = cleanWallPoints(temp,wallpoint)
#             # w,_ = conditionCheck(index,globaldata,item)
#             # shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
#             shortestnewneighbours = minDistance(temp,currentcord)
#             appendNeighbours(shortestnewneighbours[:(control-negdiff)],index,globaldata)
#         if(deltaspos < control):
#             _,_,_,temp = deltaWallNeighbourCalculation(index,newset,currentcord,nx,ny,True,globaldata)
#             temp = cleanWallPoints(temp,wallpoint)
#             # w,_ = conditionCheck(index,globaldata,item)
#             # shortestnewneighbours = minCondition(index,globaldata,currentcord,temp,w)
#             shortestnewneighbours = minDistance(temp,currentcord)
#             appendNeighbours(shortestnewneighbours[:(control-posdiff)],index,globaldata)
#         w,s = conditionCheck(index,globaldata,item)
#         if(w >= 3 or s >= 3):
#             if(control==6):
#                 None
#                 # print("Shit Man")
#             else:
#                 control = control + 1
#                 wallBalance(hashtable.index(itemda) - 1,globaldata,hashtable,itemda,control,wallpoint)


def wallDeltaSPositiveConditionCheck(index,globaldata,hashtable,wallpoints,control,threshold):
    threshold = float(threshold)
    currentcord = getPoint(index,globaldata)
    currentnbhs = getNeighbours(index,globaldata)
    nx,ny = normalCalculation(index,hashtable,globaldata,True)
    _,_,_,ds = deltaWallNeighbourCalculation(index,currentnbhs,nx,ny,True,globaldata)
    dsCond = conditionCheckWithNeighboursWall(index,globaldata,ds, nx, ny)
    

    # if(dsCond > threshold):
    #     nbhofnbh = []
    #     for nbh in ds:
    #         items = getNeighbours(index,globaldata)
    #         nbhofnbh = nbhofnbh + list(set(items) - set([currentcord]) - set(currentnbhs))
    #     pointsSurvived = minCondition(index,globaldata,nbhofnbh,threshold)
    #     if(len(pointsSurvived) == 0):
    #         print("Couldn't reduce ds positive (",currentcord,":",index,") to threshold (",threshold,"). Doing nothing to this point.")
    #     else:
    #         pointToBeAdded = pointsSurvived[:1]
    #         appendNeighbours(list(pointToBeAdded),index,globaldata)

def wallDeltaSNegativeConditionCheck(index,globaldata,hashtable,wallpoints,control,threshold):
    threshold = float(threshold)
    currentcord = getPoint(index,globaldata)
    currentnbhs = getNeighbours(index,globaldata)
    nx,ny = normalCalculation(index,hashtable,globaldata,True)
    _,_,_,ds = deltaWallNeighbourCalculation(index,currentnbhs,nx,ny,False,globaldata)
    dsCond = conditionCheckWithNeighbours(index,globaldata,ds)
    if(dsCond > threshold):
        nbhofnbh = []
        for nbh in ds:
            items = getNeighbours(index,globaldata)
            nbhofnbh = nbhofnbh + list(set(items) - set([currentcord]) - set(currentnbhs))
        pointsSurvived = minCondition(index,globaldata,nbhofnbh,threshold)
        if(len(pointsSurvived) == 0):
            print("Couldn't reduce ds negative (",currentcord,":",index,") to threshold (",threshold,"). Doing nothing to this point.")
        else:
            pointToBeAdded = pointsSurvived[:1]
            appendNeighbours(list(pointToBeAdded),index,globaldata)

def printWallConditionValue(index,globaldata,hashtable):
    currentnbhs = getNeighbours(index,globaldata)
    currentcord = getPoint(index,globaldata)
    nx,ny = normalCalculation(index,hashtable,globaldata,True)
    _,_,_,ds = deltaWallNeighbourCalculation(index,currentnbhs,nx,ny,False,globaldata)
    _,_,_,ds2 = deltaWallNeighbourCalculation(index,currentnbhs,nx,ny,True,globaldata)
    dsCondN = conditionCheckWithNeighboursWall(index,globaldata,ds,nx, ny)
    dsCondP = conditionCheckWithNeighboursWall(index,globaldata,ds2, nx, ny)   
    if(dsCondP > 10):
        nbhofnbh = []
        for nbh in ds2:
            items = getNeighbours(getIndexOf(nbh, hashtable),globaldata)
            nbhofnbh = nbhofnbh + list(set(items) - set([currentcord]) - set(currentnbhs))
        # print(nbhofnbh)
        pointsSurvived = minCondition(index,hashtable, globaldata,nbhofnbh,10, nx, ny)
        if(len(pointsSurvived) == 0):
            print("\n Problems")
        else:
            pointToBeAdded = pointsSurvived
            print(pointToBeAdded)
            appendNeighbours(list([pointToBeAdded]),index,globaldata)

    if(dsCondN > 10):
        nbhofnbh = []
        for nbh in ds:
            items = getNeighbours(getIndexOf(nbh, hashtable),globaldata)
            nbhofnbh = nbhofnbh + list(set(items) - set([currentcord]) - set(currentnbhs))
        # print(nbhofnbh)
        pointsSurvived = minCondition(index,hashtable, globaldata,nbhofnbh,10, nx, ny)
        if(len(pointsSurvived) == 0):
            print("\n Problems")
        else:
            pointToBeAdded = pointsSurvived
            print(pointToBeAdded)
            appendNeighbours(list([pointToBeAdded]),index,globaldata)
    
    print(index,dsCondP,len(ds2),dsCondN,len(ds))

def printWall(index,globaldata,hashtable):
    currentnbhs = getNeighbours(index,globaldata)
    currentcord = getPoint(index,globaldata)
    nx,ny = normalCalculation(index,hashtable,globaldata,True)
    _,_,_,ds = deltaWallNeighbourCalculation(index,currentnbhs,nx,ny,False,globaldata)
    _,_,_,ds2 = deltaWallNeighbourCalculation(index,currentnbhs,nx,ny,True,globaldata)
    dsCondN = conditionCheckWithNeighboursWall(index,globaldata,ds,nx, ny)
    dsCondP = conditionCheckWithNeighboursWall(index,globaldata,ds2, nx, ny)
    if(dsCondN >10 or dsCondP >10):
        print(index,dsCondP,len(ds2),dsCondN,len(ds))
