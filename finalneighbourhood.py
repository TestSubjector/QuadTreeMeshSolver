with open("airfoil2.txt") as inputfile:
    input_data = inputfile.readlines()


with open("neighbour.txt", "r") as neighbourfile:
    neighbour_data = neighbourfile.readlines()

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

serial_no = 0

for input_line in input_data:
    xcord_input, ycord_input =  input_line.split()
    xcord_input = float(xcord_input)
    ycord_input = float(ycord_input)
    for neighbour_line in neighbour_data:
        if(len(neighbour_line.split())<=1):
            continue
        splitted_line = neighbour_line.split()
        xcord_main, ycord_main = splitted_line[1].split(',')
        xcord_main = float(xcord_main)
        ycord_main = float(ycord_main)
        if(xcord_input == xcord_main):
            if(ycord_input == ycord_main):
                serial_no = serial_no +1
                # print splitted_line[1:]
                with open("trueneighbour.txt","a+") as trueneighbour_file:
                    trueneighbour_file.write("%s" % serial_no)
                    for item in neighbour_line[len(splitted_line[0]):]:
                        trueneighbour_file.write("%s" % item)
                    

print serial_no

# for input_line in input_data:
#     xcord_input, ycord_input =  input_line.split()
#     for neighbour_line in neighbour_data:
#         splited_line = neighbour_line.split()
        