import os, sys, json

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from core import core

os.chdir("grids")

count = 0
for f in os.listdir():
	print(count, f)
	count += 1

choice = int(input())
folder = os.listdir()[choice]
os.chdir(folder)

file_list = os.listdir()
file_list.sort(key = lambda x : len(x))

if len(file_list) == 2:
	
	file = file_list[0]

	os.chdir("..")
	os.chdir("..")
	
	prefile = open("preprocessing.sh", "r")
	lines = prefile.readlines()

	for line in lines:

		if line[:3] == "GEO":
			lines[lines.index(line)] = "GEOMETRY=" + "\"" + folder + "\"" + " # The folder in which the iterations will be stored\n"
		elif line == "        #Shape Generation\n":
			lines[lines.index(line) + 1] = "        python3 shapemod/shape.py -w" + " ./grids/" + folder + "/" + file
		elif line == "        # Indexing\n":
			lines[lines.index(line) + 1] = "        python3 ./generator/generate.py -n ./files/f$value/neighbour.txt -w" + " ./grids/" + folder + "/" + file
		elif line == "        # Neighbour Generation\n":
			lines[lines.index(line) + 1] = "       ./quadtree/main ./grids/" + folder + "/" + file_list[1] + " ./adapted.txt ./shape_generated.txt\n"

	new_file = open("preprocessing.txt", "w")
	for line in lines: 
		new_file.write(line)

	print("Preprocessing file generated.")

	orientation_file = open("grids/" + folder + "/" + file, "r")
	config_file = open("config.json", "r+")
	data = json.load(config_file)

	if core.orientation(orientation_file) == "ccw":
		data["global"]["wallPointOrientation"] = "ccw"
	else:
		data["global"]["wallPointOrientation"] = "cw"

	config_file.seek(0)
	json.dump(data, config_file)
	config_file.truncate()
	config_file.close()

	orientation_file.close()

	print("JSON file edited.")



else: 
	
	file_order = file_list[-2].split("_")

	os.chdir("..")
	os.chdir("..")

	prefile = open("preprocessing.sh", "r")
	lines = prefile.readlines()

	seg = ""	#constructing segment to write
	for string in file_order:
		seg += " ./grids/" + folder + "/" + string

	for line in lines:
		
		if line[:3] == "GEO":
			lines[lines.index(line)] = "GEOMETRY=" + "\"" + folder + "\"" + " # The folder in which the iterations will be stored\n"
		elif line == "        #Shape Generation\n":
			lines[lines.index(line) + 1] = "        python3 shapemod/shape.py -w" + seg + "\n"
		elif line == "        # Indexing\n":
			lines[lines.index(line) + 1] = "        python3 ./generator/generate.py -n ./files/f$value/neighbour.txt -w" + seg + "\n"
		elif line == "        # Neighbour Generation\n":
			lines[lines.index(line) + 1] = "       ./quadtree/main ./grids/" + folder + "/" + file_list[-2] + " ./adapted.txt ./shape_generated.txt\n"

	new_file = open("preprocessing.txt", "w")
	for line in lines: 
		new_file.write(line)

	print("Preprocessing file generated.")

	orientation_file = open("grids/" + folder + "/" + file_order[0])
	orient = core.orientation(orientation_file)
	orientation_file.close()
	
	for file in file_order[1:]:
		orientation_file = open("grids/" + folder + "/" + file)
		if core.orientation(orientation_file) != orient:
			print("Orientations of all files is not same. Exiting.")
			break
		orientation_file.close()

	config_file = open("./config.json", "r+")
	data = json.load(config_file)

	if orient == "ccw":
		data["global"]["wallPointOrientation"] = "ccw"
	else:
		data["global"]["wallPointOrientation"] = "cw"

	config_file.seek(0)
	json.dump(data, config_file)
	config_file.truncate()
	config_file.close()

	print("JSON file edited.")

