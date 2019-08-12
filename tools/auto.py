import os, sys, stat
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
try:
    from core import core
except:
    None

def main():

    log.info("Scanning for available grids")
    choices = os.listdir(path="grids")
    for idx, f in enumerate(choices):
        log.info("({}) Grid {}".format(idx, f))

    choice = int(input("Please select grid: "))
    try:
        folder = choices[choice]
    except:
        log.error("Invalid Choice")
        exit()

    shape_file = False
    file_list = os.listdir(path="grids/{}".format(folder))
    for itm in file_list:
        if itm.startswith("shape_"):
            shape_file = True
    file_list.sort(key = lambda x : len(x))

    if len(file_list) == 2:
        
        file = file_list[0]
        
        prefile = open("preprocessing.sh.example", "r")
        lines = prefile.readlines()

        for line in lines:

            if line[4:7] == "GEO":
                lines[lines.index(line)] = "    GEOMETRY=" + "\"" + folder + "\"" + " # The folder in which the iterations will be stored\n"
            elif line == "        # Shape Generation\n":
                lines[lines.index(line) + 1] = "        python3 shapemod/shape.py -w" + " ./grids/" + folder + "/" + file + "\n"
            elif line == "        # Indexing\n":
                lines[lines.index(line) + 1] = "        python3 ./generator/generate.py -n ./files/f$value/neighbour.txt -w" + " ./grids/" + folder + "/" + file + "\n"
            elif line == "        # Neighbour Generation\n":
                lines[lines.index(line) + 1] = "       ./quadtree/main ./grids/" + folder + "/" + file_list[0] + " ./adapted.txt ./shape_generated.txt ./blank.txt\n"

        new_file = open("preprocessing.sh", "w")
        for line in lines: 
            new_file.write(line)

        st = os.stat("preprocessing.sh")
        os.chmod("preprocessing.sh", st.st_mode | stat.S_IEXEC)

        log.info("Preprocessing File Updated")

        configData = dict(core.load_obj("config"))
        orientation_file = open("grids/" + folder + "/" + file, "r")
        if core.orientation(orientation_file, verbose=False) == "ccw":
            configData["global"]["wallPointOrientation"] = "ccw"
        else:
            configData["global"]["wallPointOrientation"] = "cw"
        orientation_file.close()
        core.save_obj(configData, "config", indent=4)
        log.info("Configuration File Updated")

    else:
        if shape_file: 
            file_order = file_list[-2].split("_")
        else:
            file_order = file_list[-1].split("_")
        prefile = open("preprocessing.sh.example", "r")
        lines = prefile.readlines()

        seg = ""	#constructing segment to write
        for string in file_order:
            seg += " ./grids/" + folder + "/" + string

        for line in lines:
            
            if line[4:7] == "GEO":
                lines[lines.index(line)] = "    GEOMETRY=" + "\"" + folder + "\"" + " # The folder in which the iterations will be stored\n"
            elif line == "        # Shape Generation\n":
                lines[lines.index(line) + 1] = "        python3 shapemod/shape.py -w" + seg + "\n"
            elif line == "        # Indexing\n":
                lines[lines.index(line) + 1] = "        python3 ./generator/generate.py -n ./files/f$value/neighbour.txt -w" + seg + "\n"
            elif line == "        # Neighbour Generation\n":
                lines[lines.index(line) + 1] = "       ./quadtree/main ./grids/" + folder + "/" + "{}".format(file_list[-2] if shape_file else file_list[-1]) + " ./adapted.txt ./shape_generated.txt\n"

        new_file = open("preprocessing.sh", "w")
        for line in lines: 
            new_file.write(line)

        st = os.stat("preprocessing.sh")
        os.chmod("preprocessing.sh", st.st_mode | stat.S_IEXEC)

        log.info("Preprocessing File Updated")

        orientation_file = open(os.path.join("grids", folder, file_order[0]))
        orient = core.orientation(orientation_file, verbose=False)
        orientation_file.close()
        
        for file in file_order[1:]:
            orientation_file = open("grids/" + folder + "/" + file)
            if core.orientation(orientation_file, verbose=False) != orient:
                log.info("Orientation of all grids are not same. Exiting.")
                exit()
            orientation_file.close()

        configData = dict(core.load_obj("config"))
        if orient == "ccw":
            configData["global"]["wallPointOrientation"] = "ccw"
        else:
            configData["global"]["wallPointOrientation"] = "cw"
        core.save_obj(configData, "config", indent=4)
        log.info("Configuration File Updated")

    if "adapted.txt" in os.listdir():
        choice = input("Do you want to remove adapted.txt? (Y/n): ").lower()
        if choice == 'y':
            os.remove("adapted.txt")

    if "wall.json" in os.listdir():
        choice = input("Do you want to remove wall.json? (Y/n): ").lower()
        if choice == 'y':
            os.remove("wall.json")


if __name__ == "__main__":
    import logging
    import os
    import json
    import logging.config
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    from shutil import copyfile
    
    default_path='logging.json'
    path = default_path
    try:
        from core import core
        level = core.getConfig()["global"]["logger"]["level"]
    except:
        if input("Configuration File Missing or invalid. Do you want to use the default settings? (Y/n): ").lower() == "y":
            try:
                copyfile("config.json.example", "config.json")
                from core import core
                level = core.getConfig()["global"]["logger"]["level"]
            except IOError:
                print("Default file missing or directory unwritable!")
                exit()
            except:
                print("Something wrong occurred and cannot be fixed.")
                exit()
        else:
            print("Default Configuration missing. Exiting!")
            exit()

    if level == "DEBUG":
        level = logging.DEBUG
    elif level == "INFO":
        level = logging.INFO
    elif level == "WARNING":
        level = logging.WARNING
    elif level == "ERROR":
        level = logging.ERROR
    else:
        level = logging.WARNING

    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=level,filename=core.getConfig()["global"]["logger"]["logPath"],format="%(asctime)s %(name)s %(levelname)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
    main()
