#!/bin/bash

set -e

# Backup Files
if [ $1 -eq 1 ]
then
    cp -rlf ./files/neighbour.txt ./backup_files/neighbour.txt
    cp -rlf ./files/output.txt ./backup_files/output.txt 
    cp -rlf ./files/preprocessorfile_cleaned.txt ./backup_files/preprocessorfile_cleaned.txt 
    cp -rlf ./files/preprocessorfile_rechecker.txt ./backup_files/preprocessorfile_rechecker.txt
    cp -rlf ./files/preprocessorfile.txt ./backup_files/preprocessorfile.txt
    cp -rlf wall.json ./backup_files/wall.json 

# Reinstate Backup Files
elif [ $1 -eq 2]
then 
    cp -rlf ./backup_files/neighbour.txt ./files/neighbour.txt
    cp -rlf ./backup_files/output.txt ./files/output.txt 
    cp -rlf ./backup_files/preprocessorfile_cleaned.txt ./files/preprocessorfile_cleaned.txt
    cp -rlf ./backup_files/preprocessorfile_rechecker.txt ./files/preprocessorfile_rechecker.txt
    cp -rlf ./backup_files/preprocessorfile.txt ./files/preprocessorfile.txt
    cp -rlf ./backup_files/wall.json wall.json
elif [ $1 -eq 3 ]
then
    rm -rf files
    rm -rf backup_files
    rm -f wall.json
    rm -f adapted.txt
    touch adapted.txt
# Adaptation
elif [ $1 -eq 4 ]
then
    # Adaptation Points
    python3 ./adapter/adapter.py -i ./files/preprocessorfile_rechecker.txt -a ./sensor_flag.dat
    cp -rlf ./pseudopoints.txt ./files/pseudopoints.txt
    rm ./pseudopoints.txt

else
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

    python3 ./triangulate/triangulate.py -i ./files/preprocessorfile_cleaned.txt -a False True True
    cp -rlf ./preprocessorfile_triangulate.txt ./files/preprocessorfile_triangulate.txt
    rm ./preprocessorfile_triangulate.txt

    python3 ./rechecker/rechecker.py -i ./files/preprocessorfile_triangulate.txt
    cp -rlf ./preprocessorfile_rechecker.txt ./files/preprocessorfile_rechecker.txt
    rm ./preprocessorfile_rechecker.txt
fi
