# A few notes pertaining to the code

1. The input file contains the boundary points of a shape
2. The output file contains the points generated from the mesh (after blanking of non-aerodynamic points)
3. The neighbourhood file contains both original and generated points and there neighbours
4. The number of input points is limited to 10000 by variable *MAX*
5. Variable *line_count* stores the number of input points
6. Quadrant & node can be used interchangebly
7. The **node_contains_** function specifies whether a point in the mesh is a descendant of a node or not
8. **In the code, **quadtree_node_isleaf** means than an input point is stored in that leaf. **quadtree_node_isempty** means than an input point is not stored in that leaf. **quadtree_node_ispointer** means that the pointer is not a leaf.**
9. The **node_ispointer** are actual nodes (non-leaves)
10. The leaf_array stores all the empty and filled leaves of the quadtree
