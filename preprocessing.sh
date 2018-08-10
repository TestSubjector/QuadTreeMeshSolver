#!/bin/bash

set -e

# Adaptation Points
# python3 ./adapter/adapter.py -i ./files/preprocessorfile_rechecker.txt -a ./sensor_flag.dat
# cp -rlf ./pseudopoints.txt ./files/pseudopoints.txt
# rm ./pseudopoints.txt

# Neighbour Generation
./quadtree/main ./quadtree/input/airfoil_640.txt ./adapted.txt ./quadtree/input/airfoil_640.txt
cp -rlf ./neighbour.txt ./files/neighbour.txt
rm ./neighbour.txt

# Indexing 
python3 ./generator/generate.py -n ./files/neighbour.txt -w ./generator/airfoil/airfoil_640
cp -rlf ./output.txt ./files/output.txt
cp -rlf ./preprocessorfile.txt ./files/preprocessorfile.txt
rm ./output.txt
rm ./preprocessorfile.txt

# Pre Checks

python3 ./tools/pre.py -i ./files/preprocessorfile.txt
cp -rlf ./preprocessorfile_cleaned.txt ./files/preprocessorfile_cleaned.txt
rm ./preprocessorfile_cleaned.txt
