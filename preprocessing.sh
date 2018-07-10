#!/bin/bash

set -e

# Adaptation Points
python3 ./adapter/adapter.py -i ./files/preprocessorfile_rechecker.txt -a ./sensor_flag.dat
cp -rlf ./pseudopoints.txt ./files/pseudopoints.txt
rm ./pseudopoints.txt

# Neighbour Generation
./quadtree/main ./quadtree/input/airfoil_flap.txt ./adapted.txt ./quadtree/input/shape_airfoil_flap.txt
cp -rlf ./neighbour.txt ./files/neighbour.txt
rm ./neighbour.txt

# Indexing 
python3 ./generator/generate.py -n ./files/neighbour.txt -w ./generator/twoshape/airfoil ./generator/twoshape/flap
cp -rlf ./output.txt ./files/output.txt
cp -rlf ./preprocessorfile.txt ./files/preprocessorfile.txt
rm ./output.txt
rm ./preprocessorfile.txt

# Pre Checks

python3 ./tools/pre.py -i ./files/preprocessorfile.txt
cp -rlf ./preprocessorfile_cleaned.txt ./files/preprocessorfile_cleaned.txt
rm ./preprocessorfile_cleaned.txt

# PseudoWall
python3 ./pseudowall/pwall.py -i ./files/preprocessorfile_cleaned.txt
cp -rlf ./removal_points.txt ./files/pseudowall_removal_points.txt
rm ./removal_points.txt

# PseudoWall Removal
python3 ./remover/trial.py -i ./files/preprocessorfile_cleaned.txt -r ./files/pseudowall_removal_points.txt
rm ./removal_points2.txt
cp -rlf ./preprocessorfile_pointremoval.txt ./files/preprocessorfile_pseudopointremoval.txt
rm ./preprocessorfile_pointremoval.txt

# Triangulation

python3 ./triangulate/triangulate.py -i ./files/preprocessorfile_pseudopointremoval.txt -a True True True
cp -rlf ./preprocessorfile_triangulate.txt ./files/preprocessorfile_triangulate.txt
rm ./preprocessorfile_triangulate.txt
cp -rlf ./removal_points.txt ./files/triangulation_removal_points.txt
rm ./removal_points.txt

# Triangulation Point Removal
python3 ./remover/trial.py -i ./files/preprocessorfile_triangulate.txt -r ./files/triangulation_removal_points.txt
rm ./removal_points2.txt
cp -rlf ./preprocessorfile_pointremoval.txt ./files/preprocessorfile_triangulationremoval.txt
rm ./preprocessorfile_pointremoval.txt

# Interior Rechecker and Balance

python3 ./rechecker/rechecker.py -i ./files/preprocessorfile_triangulationremoval.txt

# Wall Rechecker and Balance

python3 ./triangulate/triangulate.py -i ./preprocessorfile_rechecker.txt -a True True True
cp -rlf ./preprocessorfile_triangulate.txt ./files/preprocessorfile_triangulate.txt
rm ./removal_points.txt
rm ./preprocessorfile_rechecker.txt
mv ./preprocessorfile_triangulate.txt ./preprocessorfile_rechecker.txt
