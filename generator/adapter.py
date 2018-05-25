import argparse
import progress
import re

def loadFile():
    None

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input",const=str, nargs="?")
    parser.add_argument("-a","--adapt",const=str, nargs="?")
    args = parser.parse_args()

    print("Loading Data")

    file1 = open(args.input or "preprocessorfile.txt","r")
    data = file1.read()
    globaldata = ["start"]
    adaptdata = []
    splitdata = data.split("\n")
    splitdata = splitdata[:-1]

    
    for itm in splitdata:
        itm = itm.split(" ")
        entry = [itm[0], itm[1], itm[2]]
        globaldata.append(entry)

    file2 = open(args.adapt or "sensor.dat")
    data2 = file2.read()
    data2 = re.sub(' +', ' ',data2)
    data2 = data2.split("\n")
    data2 = data2[:-1]

    for itm2 in data2:
        adaptpoint = itm2.split(" ")
        adaptpoint.pop(0)
        if(int(adaptpoint[1]) == 1):
            adaptdata.append([globaldata[int(adaptpoint[0])][1],globaldata[int(adaptpoint[0])][2]])
    
    with open("adapted.txt", "w") as text_file:
        for item1 in adaptdata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")
    


if __name__ == "__main__":
    main()