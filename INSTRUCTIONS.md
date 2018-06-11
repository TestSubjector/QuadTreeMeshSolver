A Short Guide on How Not To Mess

** For Quadtree
The code is in the **quadtree** folder 
- Run by -> ./main input/airfoil_320.txt input/adapted.txt
- Output ->> neighbour.txt

** For Initial Indexing
The code is in the **generator** folder
- Run by -> python3 generate.py -n neighbour.txt -w airfoil_320.txt
- Uses weighted square matrices as of now
- *setPosDeltaFlags* is where the prpoblem points(to be removed) are decided
- Output ->> preprocessorfile.txt (important to send this to **remover** folder)
         ->> removal_flags.txt (used by Sir in his code to remove points, dont use unless asked by him)
         ->> removal_points.txt (stores indexes of the points to be removed, send to **remover** folder)

** For Removing Points
The code is in the  **remover** folder
- Run by -> python3 trial.py
- Just make sure to update the preprocessor and removal_points text file before running this.

** For Rechecking Points

The code is in the **rechecker** folder
- Run by -> python3 rechecker.py -i preprocessorfile.txt
- Just make sure to update the preprocessor file before running this.
- Output ->> preprocessorfile_rechecker.txt (conditional Value fix for Interior Points)
