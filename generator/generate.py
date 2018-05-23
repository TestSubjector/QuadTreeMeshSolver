import argparse
from load import *
from boundary import *
from interior import *
from balance import *
from wall import *
from outer import *
import progress

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--neighbour",const=str, nargs="?")
    parser.add_argument("-w","--wall",const=str, nargs="?")
    args = parser.parse_args()
    print("Loading Data")
    file1 = open(args.neighbour or "neighbour.txt","r")
    data = file1.read()
    data = data.replace("\t"," ")
    data = data.split("\n")
    data.pop(0)
    file2 = open(args.wall or "airfoil_160.txt","r")
    geometrydata = file2.read()
    geometrydata = geometrydata.split("\n")
    print("Loaded Data")

    hashtable,wallpoint,globaldata = loadWall(geometrydata)
    hashtable,globaldata = loadInterior(data,hashtable,globaldata,len(hashtable))
    globaldata = cleanNeighbours(globaldata)
    hashtable,globaldata = detectOuter(hashtable, globaldata)
    # Point Validation
    # print("Beginning Point Delta Calculation")
    # for index,item in enumerate(hashtable[1:]):
    #     # printProgressBar(index, len(hashtable[1:]) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #     if(getFlag(index,globaldata)==1):
    #         interiorBalanceYPos(index,globaldata,hashtable,item,0,1500)
    # print("Points Delta Calculated and Balanced")
    # print("Beginning Point Delta Calculation")
    # for index,item in enumerate(hashtable[1:]):
    #     # printProgressBar(index, len(hashtable[1:]) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #     if(getFlag(index,globaldata)==1):
    #         interiorBalanceYNeg(index,globaldata,hashtable,item,0,1500)
    # print("Points Delta Calculated and Balanced")
    # print("Beginning Point Delta Calculation")
    # for index,item in enumerate(hashtable[1:]):
    #     # printProgressBar(index, len(hashtable[1:]) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #     if(getFlag(index,globaldata)==1):
    #         interiorBalanceYPos(index,globaldata,hashtable,item,0,20)
    # print("Points Delta Calculated and Balanced")
    # print("Beginning Point Delta Calculation")
    # for index,item in enumerate(hashtable[1:]):
    #     # printProgressBar(index, len(hashtable[1:]) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #     if(getFlag(index,globaldata)==1):
    #         interiorBalanceYNeg(index,globaldata,hashtable,item,0,20)
    # print("Points Delta Calculated and Balanced")

    # print("Beginning Point Delta Calculation")
    # for index,item in enumerate(hashtable[1:]):
    #     # printProgressBar(index, len(hashtable[1:]) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #     if(getFlag(index,globaldata)==1):
    #         interiorBalanceXPos(index,globaldata,hashtable,item,0,30)
    # print("Points Delta Calculated and Balanced")
    # print("Beginning Point Delta Calculation")
    # for index,item in enumerate(hashtable[1:]):
    #     # printProgressBar(index, len(hashtable[1:]) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #     if(getFlag(index,globaldata)==1):
    #         interiorBalanceXNeg(index,globaldata,hashtable,item,0,30)
    # print("Points Delta Calculated and Balanced")
    # print("Beginning Point Delta Calculation")
    # for index,item in enumerate(hashtable[1:]):
    #     # printProgressBar(index, len(hashtable[1:]) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #     if(getFlag(index,globaldata)==1):
    #         interiorBalanceXPos(index,globaldata,hashtable,item,0,50)
    # print("Points Delta Calculated and Balanced")
    # print("Beginning Point Delta Calculation")
    # for index,item in enumerate(hashtable[1:]):
    #     # printProgressBar(index, len(hashtable[1:]) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #     if(getFlag(index,globaldata)==1):
    #         interiorBalanceXNeg(index,globaldata,hashtable,item,0,50)
    # print("Points Delta Calculated and Balanced")
    # print("Wall DS Positive")
    # for index,item in enumerate(hashtable[1:]):
    #     # printProgressBar(index, len(hashtable[1:]) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #     if(getFlag(index,globaldata)==0):
    #         wallDeltaSPositiveConditionCheck(index,globaldata,hashtable,item,wallpoint,0,10)
    # print("Wall DS Negative")
    # for index,item in enumerate(hashtable[1:]):
    #     # printProgressBar(index, len(hashtable[1:]) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #     if(getFlag(index,globaldata)==0):
    #         wallDeltaSNegativeConditionCheck(index,globaldata,hashtable,item,wallpoint,0,10)
    # print("End")

    for index,item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==0):
            
            # printWallConditionValue(index,globaldata,hashtable,item)
            wallDeltaSPositiveConditionCheck(index,globaldata,hashtable,wallpoint,0,10)

    for index,item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==0):
            None
            # printWallConditionValue(index,globaldata,hashtable,item)
            # wallDeltaSPositiveConditionCheck(index,globaldata,hashtable,item,wallpoint,0,10)
            

    for index,item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1):
            currentneighbours = getNeighbours(index, globaldata)
            currentcord = item
            _,_,_,_,yposvals = deltaNeighbourCalculation(currentneighbours,currentcord,False,False)
            _,_,_,_,ynegvals = deltaNeighbourCalculation(currentneighbours,currentcord,False,True)
            yposw = conditionCheckWithNeighbours(index,globaldata,yposvals)
            ynegw = conditionCheckWithNeighbours(index,globaldata,ynegvals)
            _,_,_,_,xposvals = deltaNeighbourCalculation(currentneighbours,currentcord,True,False)
            _,_,_,_,xnegvals = deltaNeighbourCalculation(currentneighbours,currentcord,True,True)
            xposw = conditionCheckWithNeighbours(index,globaldata,xposvals)
            xnegw = conditionCheckWithNeighbours(index,globaldata,xnegvals)
            if(xposw > 25 or xnegw > 25):
                None
                # print(index,xposw,xnegw, len(xposvals),len(xnegvals))

    globaldata = cleanNeighbours(globaldata)
    globaldata = generateReplacement(hashtable,globaldata)

    with open("preprocessorfile.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")
    # deltaData = []
    # for index,item in enumerate(globaldata):
    #     mainptx = float(item[1])
    #     mainpty = float(item[2])
    #     nbh = getNeighbours(index,globaldata)
    #     deltaSumX = 0
    #     deltaSumY = 0
    #     deltaSumXY = 0
    #     data = []
    #     for nbhitem in nbh:
    #         nbhitemX = float(nbhitem.split(",")[0])
    #         nbhitemY = float(nbhitem.split(",")[1])
    #         deltaSumX = deltaSumX + (nbhitemX-mainptx)**2
    #         deltaSumY = deltaSumY + (nbhitemY-mainpty)**2
    #         deltaSumXY = deltaSumXY + (nbhitemX-mainptx)*(nbhitemY-mainpty)
    #     data.append(deltaSumX)
    #     data.append(deltaSumXY)
    #     data.append(deltaSumXY)
    #     data.append(deltaSumY)
    #     deltaData.append(data)
    #     random = np.array(deltaData[index])
    #     shape = (2,2)
    #     random = random.reshape(shape)
    #     w,v = LA.eig(random)
    #     w = max(w)/min(w)
    #     s = np.linalg.svd(random,full_matrices=False,compute_uv=False)
    #     s = max(s)/min(s)
    #     with open("eig.txt", "a+") as text_file:
    #         if(s >= 0):
    #             text_file.writelines([str(index)," ",str(w)," ", str(s)])
    #             text_file.writelines("\n")
        # print(max(w)/min(w))


            
    # print(deltaData)

if __name__ == "__main__":
    main()