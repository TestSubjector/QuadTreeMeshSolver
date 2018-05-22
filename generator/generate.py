import argparse
from load import *
from boundary import *
from interior import *
from balance import *
from wall import *
from outer import *

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

    ## Point Validation
    print("Beginning Point Delta Calculation")
    for index,item in enumerate(hashtable[1:]):
        if(getFlag(index,globaldata)==1):
            interiorBalance(index,globaldata,hashtable,item)
        elif(getFlag(index,globaldata)==0):
            wallBalance(index,globaldata,hashtable,item,3,wallpoint)
        elif(getFlag(index,globaldata)==2):
            outerBalance(index,globaldata,hashtable,item)
    print("Points Delta Calculated and Balanced")

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