import argparse
import core
import reportgen
from tqdm import tqdm

def main():
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", const=str, nargs="?")
    args = parser.parse_args()

    print("Loading Data")

    file1 = open(args.input or "preprocessorfile.txt", "r")
    data = file1.read()
    globaldata = ["start"]
    splitdata = data.split("\n")
    splitdata = splitdata[:-1]

    print("Processed Pre-Processor File")
    print("Converting to readable format")

    for _, itm in enumerate(tqdm(splitdata)):
        itm = itm.split(" ")
        itm.pop(-1)
        entry = itm
        globaldata.append(entry)

    globaldata = core.cleanNeighbours(globaldata)

    a,b,c = reportgen.generateReportConditionValue(globaldata,30)
    print("Wall")
    print(a)
    print("Interior")
    print(b)
    print("Outer")
    print(c)

    print("Done")

if __name__ == "__main__":
    main()
