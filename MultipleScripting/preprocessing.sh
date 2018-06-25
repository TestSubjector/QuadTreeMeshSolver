#!/bin/bash

set -e

# Initial File Generation
cp -rlf ./input/neighbour.txt ./generator/neighbour.txt
cp -rlf ./input/cylinder.txt ./generator/cylinder.txt

python3 ./generator/generate.py -n ./generator/neighbour.txt -w ./generator/cylinder.txt
rm -r ./generator/neighbour.txt
rm -r ./generator/cylinder.txt

rm -r ./removal_flags.txt
rm -r ./log.txt

# Point Removal
python3 ./remover/trial.py 
python3 ./remover/trial2.py
python3 ./remover/trial3.py

rm -r ./removal_points.txt
rm -r ./removal_points2.txt 
rm -r ./removal_points3.txt

rm -r ./preprocessorfile.txt

python3 ./rechecker/rechecker.py -i ./preprocessorfile_pointremoval2.txt
rm -r ./preprocessorfile_pointremoval.txt
