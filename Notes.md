# A few notes pertaining to the code

* The input file contains the boundary points of a shape
* The output file contains the points generated from the mesh (after blanking of non-aerodynamic points)
* The neighbourhood file contains both original and generated points and there neighbours
* The number of input points is limited to 10000 by variable *MAX*
* Variable *line_count* stores the number of input points
* Quadrant & node can be used interchangebly
* The **node_contains_** function specifies whether a point in the mesh is a descendant of a node or not