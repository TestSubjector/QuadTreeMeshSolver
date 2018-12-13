# Command File

## To do bspline

* python3 ./bspline/bspline.py -i <INPUT FILE>

## To fix Wall Points based on Largest Angle

* python3 ./tools/tools.py -i <INPUT FILE>
* Type "wcc!"

## To run tools.py

* python3 ./tools/tools.py -i <INPUT FILE>

## wcc
* wcc -> To check bad wall points and adapt them
* wcc!! -> To check bad wall points and try adapting them using bsplines (Sensor Flag is generated rerun adapter.py)
* wcc!!! -> To check bad wall points and try adapting it's neighbours (Sensor Flag is generated rerun adapter.py)


## plotting with indices
* plot 'preprocessorfile_normal.txt' using 2:3:(sprintf("%d",$1)) with labels notitle

## To cut a file
* sed -n '1,<wall points end line>p' preprocessorfile_cleaned.txt > wall

## Geometry
* Each polygon is saved as an individual file. The delimiter between x and y co-ordinates is a tab (\t)

## To change from clockwise to anticlockwise and vice versa
* config.json -> global -> wallPointOrientation -> cw (ccw)

## FIRST TIME INSTRUCTIONS
* Rename config.json.example -> config.json
  
# Remember that shape generates modified shape file.
* python3 ./shapemod/shape.py -w <Path to First Geometry File> <Path to second Geometry File>
* ALWAYS ADD THIS BEFORE ANY POINT GENERATION. A file called shape_generated.txt is generated. Quadtree should use this file instead of it's usual shape text file.