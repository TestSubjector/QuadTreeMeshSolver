#!/bin/bash

set -e

# Backup Files
if [ $1 -eq 1 ]
then
    cp -rf ./files/neighbour.txt ./backup_files/neighbour.txt
    cp -rf ./files/output.txt ./backup_files/output.txt
    cp -rf ./files/preprocessorfile_cleaned.txt ./backup_files/preprocessorfile_cleaned.txt
    cp -rf ./files/preprocessorfile_rechecker.txt ./backup_files/preprocessorfile_rechecker.txt
    cp -rf ./files/preprocessorfile.txt ./backup_files/preprocessorfile.txt
    # cp -rf ./files/preprocessorfile_normal.txt ./backup_files/preprocessorfile_normal.txt
    cp -rf wall.json ./backup_files/wall.json
    echo Backup completed
# Reinstate Backup Files
elif [ $1 -eq 2 ]
then
    cp -rf ./backup_files/neighbour.txt ./files/neighbour.txt
    cp -rf ./backup_files/output.txt ./files/output.txt
    cp -rf ./backup_files/preprocessorfile_cleaned.txt ./files/preprocessorfile_cleaned.txt
    cp -rf ./backup_files/preprocessorfile_rechecker.txt ./files/preprocessorfile_rechecker.txt
    cp -rf ./backup_files/preprocessorfile.txt ./files/preprocessorfile.txt
    cp -rf ./backup_files/preprocessorfile_normal.txt ./files/preprocessorfile_normal.txt
    cp -rf ./backup_files/wall.json wall.json

    echo Backup reinstated
# Clean directory
elif [ $1 -eq 3 ]
then
    rm -rf files
    rm -rf backup_files
    rm -f wall.json
    rm -f adapted.txt
    touch adapted.txt
    mkdir files
    mkdir backup_files
    make clean -f ./quadtree/Makefile
    make -f ./quadtree/Makefile
    echo Everything wiped
# Adaptation
elif [ $1 -eq 4 ]
then
    # Adaptation Points
    python3 ./adapter/adapter.py -i ./files/preprocessorfile_normal.txt -a ./sensor_flag.dat
    # cp -rlf ./pseudopoints.txt ./files/pseudopoints.txt
    # rm ./pseudopoints.txt
    echo Adaptation points added
elif [ $1 -eq 5 ]
then
    # Iteration Backup
    # Run as ./preprocessing.sh 5 Iteration_Number Folder{1,2,3,4,5 from the required f1,f2,f3,f4,f5 folder}_Number
    GEOMETRY="airfoil_320" # The folder in which the iterations will be stored
    mkdir ./backup_files/$GEOMETRY/$2
    cp -rf ./files/f$3/neighbour.txt ./backup_files/$GEOMETRY/$2/neighbour.txt
    cp -rf ./files/f$3/output.txt ./backup_files/$GEOMETRY/$2/output.txt
    cp -rf ./files/f$3/preprocessorfile_cleaned.txt ./backup_files/$GEOMETRY/$2/preprocessorfile_cleaned.txt
    cp -rf ./files/f$3/preprocessorfile_rechecker.txt ./backup_files/$GEOMETRY/$2/preprocessorfile_rechecker.txt
    cp -rf ./files/f$3/preprocessorfile_normal.txt ./backup_files/$GEOMETRY/$2/preprocessorfile_normal.txt
    cp -rf ./files/f$3/preprocessorfile.txt ./backup_files/$GEOMETRY/$2/preprocessorfile.txt
    cp -rf ./files/f$3/preprocessorfile.poly ./backup_files/$GEOMETRY/$2/preprocessorfile.poly
    cp -rf ./files/f$3/adapted.txt ./backup_files/$GEOMETRY/$2/adapted.txt
    cp -rf ./files/f$3/wall.json ./backup_files/$GEOMETRY/$2/wall.json
else
    for value in {1..5}
    do

        echo $value Iteration

        cp -rf ./adapted.txt ./files/f$value/adapted.txt | touch adapted.txt && echo "Creating Adaption File"

        #Shape Generation
        python3 shapemod/shape.py -w ./grids/airfoil_coarse_320/airfoil_320

        # Neighbour Generation
        ./quadtree/main ./grids/airfoil_coarse_320/airfoil_320 ./adapted.txt ./shape_generated.txt
        cp -rlf ./neighbour.txt ./files/f$value/neighbour.txt
        rm ./neighbour.txt

        # Indexing
        python3 ./generator/generate.py -n ./files/f$value/neighbour.txt -w ./grids/airfoil_coarse_320/airfoil_320
        cp -rlf ./output.txt ./files/f$value/output.txt
        cp -rlf ./preprocessorfile.txt ./files/f$value/preprocessorfile.txt
        rm ./output.txt
        rm ./preprocessorfile.txt

        # Pre Checks

        python3 ./tools/pre.py -i ./files/f$value/preprocessorfile.txt
        cp -rlf ./preprocessorfile_cleaned.txt ./files/f$value/preprocessorfile_cleaned.txt
        cp -rlf ./preprocessorfile.poly ./files/f$value/preprocessorfile.poly
        rm ./preprocessorfile.poly
        rm ./preprocessorfile_cleaned.txt

        python3 ./triangulate/triangulate.py -i ./files/f$value/preprocessorfile_cleaned.txt -a False True True
        cp -rlf ./preprocessorfile_triangulate.txt ./files/f$value/preprocessorfile_triangulate.txt
        rm ./preprocessorfile_triangulate.txt

        python3 ./rechecker/rechecker.py -i ./files/f$value/preprocessorfile_triangulate.txt
        cp -rlf ./preprocessorfile_rechecker.txt ./files/f$value/preprocessorfile_rechecker.txt
        rm ./preprocessorfile_rechecker.txt

        python3 ./normal/normal.py -i ./files/f$value/preprocessorfile_rechecker.txt
        cp -rlf ./preprocessorfile_normal.txt ./files/f$value/preprocessorfile_normal.txt
        rm ./preprocessorfile_normal.txt

        python3 ./bspline/bspline.py -i ./files/f$value/preprocessorfile_normal.txt -p True -q True -s True
        cp -rf ./wall.json ./files/f$value/wall.json

    done
    echo All Done
fi
