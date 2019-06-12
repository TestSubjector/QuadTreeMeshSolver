import os, sys, json

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

print("Scanning for available grids")
choices = os.listdir(path="grids")
for idx, f in enumerate(choices):
	print("({}) Grid {}".format(idx, f))

choice = int(input("Please select grid: "))
try:
	folder = choices[choice]
except:
	print("Invalid Choice")
	exit()

file_list = os.listdir(path="grids/{}".format(folder))
file_list.sort(key = lambda x : len(x))

if len(file_list) == 2:
	
	file = file_list[0]
	
	prefile = open("preprocessing.sh", "r")
	lines = prefile.readlines()

	for line in lines:

		if line[:3] == "GEO":
			lines[lines.index(line)] = "GEOMETRY=" + "\"" + folder + "\"" + " # The folder in which the iterations will be stored\n"
		elif line == "        #Shape Generation\n":
			lines[lines.index(line) + 1] = "        python3 shapemod/shape.py -w" + " ./grids/" + folder + "/" + file + "\n"
		elif line == "        # Indexing\n":
			lines[lines.index(line) + 1] = "        python3 ./generator/generate.py -n ./files/f$value/neighbour.txt -w" + " ./grids/" + folder + "/" + file + "\n"
		elif line == "        # Neighbour Generation\n":
			lines[lines.index(line) + 1] = "       ./quadtree/main ./grids/" + folder + "/" + file_list[0] + " ./adapted.txt ./shape_generated.txt\n"

	new_file = open("preprocessing.sh", "w")
	for line in lines: 
		new_file.write(line)

	print("Preprocessing File Updated")

	configData = dict(core.load_obj("config"))
	orientation_file = open("grids/" + folder + "/" + file, "r")
	if core.orientation(orientation_file, verbose=False) == "ccw":
		configData["global"]["wallPointOrientation"] = "ccw"
	else:
		configData["global"]["wallPointOrientation"] = "cw"
	orientation_file.close()
	core.save_obj(configData, "config", indent=4)
	print("Configuration File Updated")

else: 
	
	file_order = file_list[-2].split("_")
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

	new_file = open("preprocessing.sh", "w")
	for line in lines: 
		new_file.write(line)

	print("Preprocessing File Updated")

	orientation_file = open(os.path.join("grids/", folder, "/", file_order[0]))
	orient = core.orientation(orientation_file, verbose=False)
	orientation_file.close()
	
	for file in file_order[1:]:
		orientation_file = open("grids/" + folder + "/" + file)
		if core.orientation(orientation_file) != orient:
			print("Orientation of all grids are not same. Exiting.")
			exit()
		orientation_file.close()

	configData = dict(core.load_obj("config"))
	if orient == "ccw":
		configData["global"]["wallPointOrientation"] = "ccw"
	else:
		configData["global"]["wallPointOrientation"] = "cw"
	core.save_obj(configData, "config", indent=4)

	print("Configuration File Updated")

