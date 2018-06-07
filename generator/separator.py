import argparse
from progress import printProgressBar
from separatormisc import *

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input",const=str, nargs="?")
    args = parser.parse_args()

    print("Loading Data")

    file1 = open(args.input or "preprocessorfile.txt","r")
    data = file1.read()
    globaldata = ["start"]
    splitdata = data.split("\n")
    splitdata = splitdata[:-1]

    print("Processed Pre-Processor File")
    print("Converting to readable format")

    
    for idx, itm in enumerate(splitdata):
        printProgressBar(idx, len(splitdata) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        itm = itm.split(" ")
        itm.pop(-1)
        entry = itm
        globaldata.append(entry)

    print("Data Converted")

    print("Detecting Problem Points")
    
    problempts = getProblemPoints(globaldata,1000)
    print("Found",len(problempts),"problem points.")

    if(len(problempts)!=0):
        globaldata = nukePoints(globaldata,problempts,1000)
    
    globaldata = deletePoints(globaldata,problempts)

    currentindex = ["start"]
    oldindex = ["start"]

    for itm in globaldata[1:]:
        currentindex.append(int(itm[0]))
        oldindex.append(int(itm[0]))
    
    for itm in problempts:
        templist = currentindex[int(itm):]
        templist = [x-1 for x in templist]
        currentindex[int(itm):] = templist

    for itsval,item in enumerate(oldindex): 
        printProgressBar(itsval, len(oldindex) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        if(itsval>0):
            for index, individualitem in enumerate(globaldata):
                if(index>0):
                    for idx2,itm2 in enumerate(individualitem):
                        if(idx2<1 or idx2>11):
                            if(int(itm2)==int(item)):
                                if(int(item)!=int(currentindex[itsval])):
                                    globaldata[index][idx2] = int(currentindex[itsval])
                    
                
        
    globaldata.pop(0)
    with open("preprocessorfile_separator.txt", "w") as text_file:
        for item1 in globaldata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")

if __name__ == "__main__":
    main()