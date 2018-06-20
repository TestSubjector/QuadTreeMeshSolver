from misc import *
from balance import *

# def outerBalance(index,globaldata,hashtable,item):
#     currentneighbours = getNeighbours(index,globaldata)
#     currentcord = item
#     nx,ny = normalCalculation(index,currentcord,hashtable,globaldata,False)
#     deltaspos,deltasneg,deltaszero,temp = deltaWallNeighbourCalculation(index,currentneighbours,currentcord,nx,ny,False,globaldata)
#     # if(item=="8.75,8.75"):
#     # print(index,len(currentneighbours),deltaspos,deltasneg,deltaszero,nx,ny,currentneighbours)
#     if(deltaspos < 4 or deltasneg < 4):
#         newset = []
#         posdiff = deltaspos
#         negdiff = deltasneg
#         for item in currentneighbours:
#             itemnb = getNeighbours(hashtable.index(item) - 1,globaldata)
#             newset = newset + itemnb
#         # Filter 1
#         newset = list(set(newset) - set(currentneighbours))
#         newset = list(set(newset) - set([currentcord]))
#         if(deltasneg < 4):
#             _,_,_,temp = deltaWallNeighbourCalculation(index,newset,currentcord,nx,ny,False,globaldata)
#             shortestnewneighbours = minDistance(temp,currentcord)
#             appendNeighbours(shortestnewneighbours[:(4-negdiff)],index,globaldata)
#         if(deltaspos < 4):
#             _,_,_,temp = deltaWallNeighbourCalculation(index,newset,currentcord,nx,ny,True,globaldata)
#             shortestnewneighbours = minDistance(temp,currentcord)
#             appendNeighbours(shortestnewneighbours[:(4-posdiff)],index,globaldata)
