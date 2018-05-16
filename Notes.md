# A few notes pertaining to the code

1. The input file contains the boundary points of a shape.
2. The output file contains the points generated from the mesh (after blanking of non-aerodynamic points).
3. The neighbourhood file contains both original and generated points and there neighbours.
4. The number of input points is limited to 10000 by variable *MAX*.
5. Variable *line_count* stores the number of input points.
6. Quadrant & node can be used interchangebly.
7. The **node_contains_** function specifies whether a point in the mesh is a descendant of a node or not.
8. **In the code, **quadtree_node_isleaf** means than an input point is stored in that leaf. **quadtree_node_isempty** means than an input point is not stored in that leaf. **quadtree_node_ispointer** means that the pointer is not a leaf.**
9. The **node_ispointer** are actual nodes (non-leaves).
10. The leaf_array stores all the empty and filled leaves of the quadtree.
11. The patharray is set at 21, i.e it is assumed that heigh of tree won't be greater than 20.
12. patharray[20] stores the actual height from root to leaf.
13. In **find_neighbours** we go reverse, from the leaf to the common ancestor so the patharray is traversed backwards. Additionally, the function one by one checks whether the point has neighbours in the east,west, nort, south direction.
14. You can't find eastern neighbour(And therefore common ancestor) for a point that is located in root->NE->NE-NE... or root->SE->SE->SE... or root->NE->SE->NE... And the same argument holds for other directions too.
15. There are two functions for the neighbour file. The **neighbouroutput** puts the serial no, point whose neighbours will be given and the number of neighbours found into the file. It also checks whether the point should be blanked or not.
16. The neighbour_counter is updated by the second function when it runs( since we get total number of neighbours only after we search for those neighbours). So it is put into the file as the last integer of the line and then the file pointer is shifted to the new line.
17. TODO - Check if *second_poly* is working as it should with small examples.
18. The second function **neighbourset**...*work in progress*
19. The neighbour file has a blank first line because of append (a+) usage.