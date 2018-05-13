import math
import copy

# File Handling Input

with open("airfoil2.txt") as inputfile:
    input_data = inputfile.readlines()


with open("neighbour.txt", "r") as neighbourfile:
    original_neighbour_data = neighbourfile.readlines()

open("trueneighbour.txt","w").close()

# line  = neighbour_data[1]
# word = line.split() # Split into different words
# print type(word[2])
# xcord_main, ycord_main  = word[1].split(',') # Seperate the point under consideration
# print type(xcord_main), ycord_main
# print word[len(word) - 1] # Neighbours is this - 3

# print len(input_data[0].split())
# xcord_input, ycord_input =  input_data[0].split()
# for line in data:
#     word = line.split()
# print xcord_input, ycord_input


def equalityCheck(pointOne, pointTwo):
    
    xcord_p1, ycord_p1 = pointOne.split(',')
    xcord_p1 = float(xcord_p1)
    ycord_p1 = float(ycord_p1)
    xcord_p2, ycord_p2 = pointTwo.split(',')
    xcord_p2 = float(xcord_p2)
    ycord_p2 = float(ycord_p2)
    if(xcord_p1 == xcord_p2 and ycord_p1 == ycord_p2):
        return 1
    else:
        return 0

def squareDistance(mainPoint, pointList):
    xcord_main, ycord_main = mainPoint.split(',')
    xcord_main = float(xcord_main)
    ycord_main = float(ycord_main)
    distanceValue = 100
    good_point = ""
    for point in  pointList:
        xcord_neighbour, ycord_neighbour = point.split(',')
        xcord_neighbour = float(xcord_neighbour)
        ycord_neighbour = float(ycord_neighbour)
        value = math.sqrt(math.pow((xcord_main-xcord_neighbour),2) + math.pow((ycord_main - ycord_neighbour),2))
        if(distanceValue > value):
            distanceValue = value
            good_point = point
    return good_point

# def minX(xCoordlist, xcoord):
#     mainXCoordList = []
#     tempValue = 10
#     tempXCoord
#     for xCoord in xCoordlist:
#         if(xCoord)

def innerPointNeighburs(neighbour_line):
    neg_deltax = 0
    pos_deltax = 0
    neg_points = []
    pos_points = []
    closestPointList = []
    extended_NeighbourList = []

    splitted_line = neighbour_line.split()
    xcord_main, ycord_main = splitted_line[1].split(',')
    xcord_main = float(xcord_main)
    ycord_main = float(ycord_main)

    for neighbour in splitted_line[2:len(splitted_line)-1]:
        xcord_neighbour, ycord_neighbour = neighbour.split(',')
        xcord_neighbour = float(xcord_neighbour)
        ycord_neighbour = float(ycord_neighbour)
        if(xcord_neighbour - xcord_main <= 0):
            neg_deltax = neg_deltax + 1
            neg_points.append(neighbour)
        if(xcord_neighbour - xcord_main >= 0):
            pos_deltax = pos_deltax + 1
            pos_points.append(neighbour)

    # For negative delta neighbours
    if(neg_deltax < 3):
        # Need to add consitions for neg_deltax = 1 || neg_deltax =2
        closestPoint = squareDistance(splitted_line[1], neg_points)
        for neighbour_line in original_neighbour_data:
            if(len(neighbour_line.split()) <= 1):
                continue
            closestPoint_SplittedLine = neighbour_line.split()
            # We found the line which has the neighbouring point as main point
            if(closestPoint == closestPoint_SplittedLine[1]):
                for neighbour_point in closestPoint_SplittedLine[2:len(closestPoint_SplittedLine) - 1]:
                    if(equalityCheck(splitted_line[1], neighbour_point) + neg_points.count(neighbour_point) + 
                        pos_points.count(neighbour_point) < 1):
                        closestPointList.append(neighbour_point)
        extended_NeighbourList.append(squareDistance(splitted_line[1], closestPointList))

    # For positive delta neighbours
    if(pos_deltax < 3):
        closestPoint = squareDistance(splitted_line[1], pos_points)
        for neighbour_line in original_neighbour_data:
            if(len(neighbour_line.split()) <= 1):
                continue
            closestPoint_SplittedLine = neighbour_line.split()
            # We found the line which has the neighbouring point as main point
            if(closestPoint == closestPoint_SplittedLine[1]):
                for neighbour_point in closestPoint_SplittedLine[2:len(closestPoint_SplittedLine) - 1]:
                    if(equalityCheck(splitted_line[1], neighbour_point) + neg_points.count(neighbour_point) + 
                        pos_points.count(neighbour_point) < 1):
                        closestPointList.append(neighbour_point)
        extended_NeighbourList.append(squareDistance(splitted_line[1], closestPointList))
    return extended_NeighbourList

serial_no = 0
list_inputlines = []
list_interiorlines = []
neighbour_data = copy.copy(original_neighbour_data)


# Store all the wall point first in the file
for input_line in input_data:
    xcord_input, ycord_input =  input_line.split()
    xcord_input = float(xcord_input)
    ycord_input = float(ycord_input)
    for neighbour_line in neighbour_data:
        if(len(neighbour_line.split())<=1):  # To skip first blank line
            continue
        splitted_line = neighbour_line.split()
        xcord_main, ycord_main = splitted_line[1].split(',')
        xcord_main = float(xcord_main)
        ycord_main = float(ycord_main)
        if((xcord_input == xcord_main) and (ycord_input == ycord_main)):
            serial_no = serial_no + 1
            list_inputlines.append(' '.join([str(serial_no), neighbour_line[len(splitted_line[0]):]]))
            neighbour_data.remove(neighbour_line)
            # print splitted_line[1:]


for i in range(len(neighbour_data)):
    if(len(neighbour_data[i].split()) <= 1):
                continue
    splitted_line = neighbour_data[i].split()
    new_neighbours = ' '.join(innerPointNeighburs(neighbour_data[i]))
    serial_no = serial_no + 1
    list_interiorlines.append(' '.join([str(serial_no), neighbour_data[i][len(splitted_line[0]):-4], 
        new_neighbours, str(int(splitted_line[-1]) + len(new_neighbours.split())) , "\n"]))

# splitted_line = neighbour_data[1].split()
# new_neighbours = ' '.join(innerPointNeighburs(neighbour_data[1]))
# # The main line
# list_interiorlines.append(' '.join([str(serial_no), neighbour_data[1][len(splitted_line[0]):-4], 
#       new_neighbours, str(int(neighbour_data[1][-3]) + len(new_neighbours.split()))]))
# print list_interiorlines[0]


# splitted_data = neighbour_data[1].split()
# list_inputlines.append(' '.join([str(serial_no), neighbour_data[1][len(splitted_data[0]):]]))
# print list_inputlines

# for input_line in input_data:
#     xcord_input, ycord_input =  input_line.split()
#     for neighbour_line in neighbour_data:
#         splited_line = neighbour_line.split()

with open("trueneighbour.txt","a+") as trueneighbour_file:
    for list_inputline in list_inputlines:
        trueneighbour_file.write("%s" % list_inputline)

with open("trueneighbour.txt","a+") as trueneighbour_file:
    for list_interiorline in list_interiorlines:
        trueneighbour_file.write("%s" % list_interiorline)


print serial_no
        