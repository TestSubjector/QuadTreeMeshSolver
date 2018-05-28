import argparse
import re

def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    if iteration == total: 
        print()

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

    
    for idx, itm in enumerate(splitdata):
        printProgressBar(idx, len(splitdata) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        itm = itm.split(" ")
        entry = [itm[0], itm[1], itm[2]]
        globaldata.append(entry)
    
    print("Processed Pre-Processor File")

    file2 = open(args.adapt or "sensor_flag.dat")
    data2 = file2.read()
    data2 = re.sub(' +', ' ',data2)
    data2 = data2.split("\n")
    data2 = data2[:-1]

    print("Reading Adaptation File")

    for idx2,itm2 in enumerate(data2):
        printProgressBar(idx2, len(data2) - 1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        adaptpoint = itm2.split(" ")
        adaptpoint.pop(0)
        if(int(adaptpoint[1]) == 1):
            xcord = globaldata[int(adaptpoint[0])][1]
            ycord = globaldata[int(adaptpoint[0])][2]
            adaptdata.append([xcord,ycord])
    
    print("Adaptation File Data Processed")
    print("Writing adapted.txt")
    
    with open("adapted.txt", "w") as text_file:
        for item1 in adaptdata:
            text_file.writelines(["%s " % item for item in item1])
            text_file.writelines("\n")
    
    print("Done")

if __name__ == "__main__":
    main()