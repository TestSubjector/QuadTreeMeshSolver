#include "quadtree.h"
#include <stdio.h>

int patharray[41];
int path_iter = 0;
int diagonal_patharray[41];
int diagonal_path_iter;

/* It is a not a leaf but an actual node */
int quadtree_node_ispointer(quadtree_node_t *node)
{
    return node->nw != NULL && node->ne != NULL && node->sw != NULL && node->se != NULL && !quadtree_node_isleaf(node);
}

/* There is no input point in that leaf i.e empty leaf */
int quadtree_node_isempty(quadtree_node_t *node)
{
    return node->nw == NULL && node->ne == NULL && node->sw == NULL && node->se == NULL && !quadtree_node_isleaf(node);
}

/* There is an input point in that leaf i.e filled leaf */
int quadtree_node_isleaf(quadtree_node_t *node)
{
    return node->point != NULL;
}

void quadtree_node_reset(quadtree_node_t *node)
{
    quadtree_point_free(node->point);
}

/* Initialize a node */
quadtree_node_t *quadtree_node_new()
{
    quadtree_node_t *node;
    if (!(node = malloc(sizeof(*node))))
        return NULL;
    node->ne = NULL;
    node->nw = NULL;
    node->se = NULL;
    node->sw = NULL;
    node->point = NULL;
    node->bounds = NULL;
    node->height = 1;
    node->direction = 0;
    return node;
}

/* Give bounds of the quadrant to a node */
quadtree_node_t *quadtree_node_with_bounds(double minx, double miny, double maxx, double maxy)
{
    quadtree_node_t *node;
    if (!(node = quadtree_node_new()))
    {
        return NULL;
    }
    if (!(node->bounds = quadtree_bounds_new()))
    {
        return NULL;
    }
    quadtree_bounds_extend(node->bounds, maxx, maxy);
    quadtree_bounds_extend(node->bounds, minx, miny);
    return node;
}

void quadtree_node_free(quadtree_node_t *node)
{
    if (node->nw != NULL)
        quadtree_node_free(node->nw);
    if (node->ne != NULL)
        quadtree_node_free(node->ne);
    if (node->sw != NULL)
        quadtree_node_free(node->sw);
    if (node->se != NULL)
        quadtree_node_free(node->se);

    quadtree_bounds_free(node->bounds);
    quadtree_node_reset(node);
    free(node);
}

void quadtree_leafnodes(quadtree_node_t *root, quadtree_node_t *leaf_array)
{
    /* Get all leaf nodes */
    quadtree_leafwalk(root, descent_leaf, ascent, leaf_array);
    /* Print all the leaf nodes at this point */
    int i = 0;
    for (i = 0; i < leaf_iter; i++)
    {
        quadtree_node_t *node = &leaf_array[i];
        if (quadtree_node_isempty(node))
        {
            // printf("\n %f %f", (node->bounds->nw->x + node->bounds->se->x) / 2,
            //         (node->bounds->nw->y + node->bounds->se->y) / 2);
        }
        else if (quadtree_node_isleaf(node))
        {
            // printf("\n%f %f", node->point->x, node->point->y);
        }
    }
}

static int node_contains_patharray(quadtree_node_t *outer, double x, double y)
{
    return outer->bounds != NULL && outer->bounds->nw->x <= x &&
           outer->bounds->nw->y >= y && outer->bounds->se->x >= x &&
           outer->bounds->se->y <= y;
}

/* Inititator function for to bring descent and check for memory problems */
static quadtree_point_t *find_patharray(quadtree_node_t *node, double x, double y)
{
    if (!node)
    {
        printf("\n ERROR : Non-existent node encounted while finding patharray");
        exit(2);
    }
    else if (quadtree_node_ispointer(node))
    {
        return find_patharray(get_quadrant_patharray(node, x, y), x, y);
    }
    return NULL; // Stop when leaf is reached
}

// TODO - Remove this redundant fuction by an argument
static quadtree_point_t *find_patharray_diagonal(quadtree_node_t *node, double x, double y)
{
    if (!node)
    {
        printf("\n ERROR : Non-existent node encounted while finding patharray");
        exit(2);
    }
    else if (quadtree_node_ispointer(node))
    {
        return find_patharray_diagonal(get_quadrant_patharray_diagonal(node, x, y), x, y);
    }
    return NULL; // Stop when leaf is reached
}

/* Stores the descent path from root node to leaf whose neighbours we need to find */
static quadtree_node_t *get_quadrant_patharray(quadtree_node_t *root, double x, double y)
{
    if (node_contains_patharray(root->nw, x, y))
    {
        // printf("1");
        patharray[path_iter] = 1;
        path_iter++;
        return root->nw;
    }
    if (node_contains_patharray(root->ne, x, y))
    {
        // printf("2");
        patharray[path_iter] = 2;
        path_iter++;
        return root->ne;
    }
    if (node_contains_patharray(root->sw, x, y))
    {
        // printf("3");
        patharray[path_iter] = 3;
        path_iter++;
        return root->sw;
    }
    if (node_contains_patharray(root->se, x, y))
    {
        // printf("4");
        patharray[path_iter] = 4;
        path_iter++;
        return root->se;
    }
    printf("\n ERROR : During patharray, found node that does not belong to any quadrant");
    exit(2); // Returns the child of the node to which the leaf belongs
}

/* This function is for the diagonal neighbour findings. TODO - Make the path_array an argument, rather than two different functions */
static quadtree_node_t *get_quadrant_patharray_diagonal(quadtree_node_t *root, double x, double y)
{
    if (node_contains_patharray(root->nw, x, y))
    {
        // printf("1");
        diagonal_patharray[diagonal_path_iter] = 1;
        diagonal_path_iter++;
        return root->nw;
    }
    if (node_contains_patharray(root->ne, x, y))
    {
        // printf("2");
        diagonal_patharray[diagonal_path_iter] = 2;
        diagonal_path_iter++;
        return root->ne;
    }
    if (node_contains_patharray(root->sw, x, y))
    {
        // printf("3");
        diagonal_patharray[diagonal_path_iter] = 3;
        diagonal_path_iter++;
        return root->sw;
    }
    if (node_contains_patharray(root->se, x, y))
    {
        // printf("4");
        diagonal_patharray[diagonal_path_iter] = 4;
        diagonal_path_iter++;
        return root->se;
    }
    printf("\n ERROR : During patharray, found node that does not belong to any quadrant");
    exit(2); // Returns the child of the node to which the leaf belongs
}

int split_node_newpoints(quadtree_t *tree, quadtree_node_t *node)
{

    quadtree_node_t *nw = NULL;
    quadtree_node_t *ne = NULL;
    quadtree_node_t *sw = NULL;
    quadtree_node_t *se = NULL;
    quadtree_point_t *old;

    double x = node->bounds->nw->x;
    double y = node->bounds->nw->y;
    double hw = node->bounds->width / 2;
    double hh = node->bounds->height / 2;

    // minx,   miny,       maxx,       maxy
    if (!(nw = quadtree_node_with_bounds(x, y - hh, x + hw, y)))
    {
        printf("\n Warning: Problem occured while splitting node");
        return 0;
    }
    if (!(ne = quadtree_node_with_bounds(x + hw, y - hh, x + hw * 2, y)))
    {
        printf("\n Warning: Problem occured while splitting node");
        return 0;
    }
    if (!(sw = quadtree_node_with_bounds(x, y - hh * 2, x + hw, y - hh)))
    {
        printf("\n Warning: Problem occured while splitting node");
        return 0;
    }
    if (!(se = quadtree_node_with_bounds(x + hw, y - hh * 2, x + hw * 2, y - hh)))
    {
        printf("\n Warning: Problem occured while splitting node");
        return 0;
    }

    node->nw = nw;
    nw->height = node->height + 1;
    nw->direction = 1;
    node->ne = ne;
    ne->height = node->height + 1;
    ne->direction = 2;
    node->sw = sw;
    sw->height = node->height + 1;
    sw->direction = 3;
    node->se = se;
    se->height = node->height + 1;
    se->direction = 4;

    if (quadtree_node_isleaf(node))
    {
        old = node->point;
        // printf("\n For point %lf, %lf ", (node->bounds->nw->x + node->bounds->se->x) / 2, (node->bounds->nw->y + node->bounds->se->y) / 2);
        // printf("\n For point %lf, %lf ", node->point->x, node->point->y);
        node->point = NULL;
        return insert_(tree, node, old);
    }
    return 0;
}

/* This function does not find common ancestor, just the tree path from root to node */
int *common_treeroute(quadtree_node_t *root, quadtree_node_t *node)
{
    int i = 0;
    for (i = 0; i < 41; i++)
    {
        patharray[i] = 0;
    }
    /* If the leaf is empty */
    if (quadtree_node_isempty(node))
    {
        path_iter = 0;
        find_patharray(root, (node->bounds->nw->x + node->bounds->se->x) / 2, (node->bounds->nw->y + node->bounds->se->y) / 2);
        // printf("\n For point %lf, %lf ", (node->bounds->nw->x + node->bounds->se->x) / 2, (node->bounds->nw->y + node->bounds->se->y) / 2);
    }
    else if (quadtree_node_isleaf(node))
    {
        path_iter = 0;
        find_patharray(root, node->point->x, node->point->y);
        // printf("\n For point %lf, %lf ", node->point->x, node->point->y);
    }
    else
    {
        printf("ERROR: The leaf finding process encountered an error, you know what that means");
        exit(2);
    }
    patharray[40] = path_iter; // Store height from root to leaf
    return patharray;
}

/* TODO - Remove the redundant function with arguments */
int *common_ancestor_diagonal(quadtree_node_t *root, quadtree_node_t *node)
{
    int i = 0;
    for (i = 0; i < 41; i++)
    {
        diagonal_patharray[i] = 0;
    }
    /* If the leaf is empty */
    if (quadtree_node_isempty(node))
    {
        diagonal_path_iter = 0;
        find_patharray_diagonal(root, (node->bounds->nw->x + node->bounds->se->x) / 2, (node->bounds->nw->y + node->bounds->se->y) / 2);
        // printf("\n For point %lf, %lf ", (node->bounds->nw->x + node->bounds->se->x) / 2, (node->bounds->nw->y + node->bounds->se->y) / 2);
    }
    else if (quadtree_node_isleaf(node))
    {
        diagonal_path_iter = 0;
        find_patharray_diagonal(root, node->point->x, node->point->y);
        // printf("\n For point %lf, %lf ", node->point->x, node->point->y);
    }
    else
    {
        printf("\n ERROR: Not recieving leaves for the diagonal code");
    }
    diagonal_patharray[40] = diagonal_path_iter; // Store height from root to leaf
    if(checker == 1)
    {
        printf("Last element is %d", diagonal_path_iter);
    }
    return diagonal_patharray;
}

/* This function finds common_ancestor and takes the leaf(and its patharray) as input */
void find_neighbours(quadtree_t *tree, int patharray[41], quadtree_node_t *leaf_array)
{
    // printf("\n Start");

    int path_size = patharray[40]; // Specifies the height from the root to the leaf
    int i = 0;                     // Loop iterator
    int pathstep = -1;             // The check for common ancestor
    int direction = 0;             // Input to followup function specifying direction of neighbour
    int ancestor_pos = -1;         // Specifies the position of common ancestor

    // NW - 1, NE - 2, SW - 3 , SE - 4

    /*// To find path array
    for(i = path_size - 1; i>= 0; i--)
    {
        printf("\n The path point is %d", patharray[i]);
    }
    */

    direction = 1;                       // For Eastern neighbour
    ancestor_pos = east_ancestor(patharray, path_size);
    if (ancestor_pos != -1)
    {
        // printf("\n Found common ancestor for Eastern neighbour");
        balance_neighbours(tree, patharray, ancestor_pos, direction, leaf_array);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Eastern Neighbour does not exist");
    }

    direction = 2; // For Western Neighbour
    ancestor_pos = west_ancestor(patharray, path_size);
    if (ancestor_pos != -1)
    {
        balance_neighbours(tree, patharray, ancestor_pos, direction, leaf_array);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Western Neighbour does not exist");
    }

    direction = 3; // For Northern Neighbour
    ancestor_pos = north_ancestor(patharray, path_size);
    if (ancestor_pos != -1)
    {
        balance_neighbours(tree, patharray, ancestor_pos, direction, leaf_array);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Northern Neighbour does not exist");
    }

    direction = 4; // For Southern Neighbour
    ancestor_pos = south_ancestor(patharray, path_size);
    if (ancestor_pos != -1)
    {
        balance_neighbours(tree, patharray, ancestor_pos, direction, leaf_array);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Southern Neighbour does not exist");
    }
}

/* This function finds the nieghbour of a point in specified direction */
void balance_neighbours(quadtree_t *tree, int patharray[41], int ancestor_pos, int direction, quadtree_node_t *leaf_array)
{

    // Direction
    // East - 1 , West - 2, North -3, South - 4

    quadtree_node_t *root = tree->root; // Done simply for convienience
    int path_step = 0;                  // Stores the current path value
    int i = 0;                          // Loop iterator
    quadtree_node_t *temp;

    root = reach_ancestor(root, patharray, ancestor_pos);

    // Eastern Neighbour
    if (direction == 1)
    {
        // printf("\n Finding Eastern Neighbour");
        int i = ancestor_pos;
        for (i = ancestor_pos; i <= patharray[40] - 2; i++) // -2 because the neighbour can be one level higher
        {
            path_step = patharray[i];
            // If we have reached a leaf empty or filled) before we should have
            if (quadtree_node_isempty(root) || (quadtree_node_isleaf(root)))
            {
                // Analysis - Should give only a few outputs because only some nodes will have
                // neighbour not at the same level or one level higher
                // printf("\n Neighbour split: East");
                split_node_newpoints(tree, root);
                temp = root;
                if (path_step != 1 || (i == patharray[40] -2))
                {
                    // printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp->ne);
                    leaf_iter++;
                }

                if (path_step != 2 || (i == patharray[40] -2))
                {
                    // printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp->nw);
                    leaf_iter++;
                }

                if (path_step != 3 || (i == patharray[40] -2))
                {
                    // printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp->se);
                    leaf_iter++;
                }

                if (path_step != 4 || (i == patharray[40] -2))
                {
                    // printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp->sw);
                    leaf_iter++;
                }

            }

            if (path_step == 1)
            {
                root = root->ne;
            }
            else if (path_step == 2)
            {
                root = root->nw;
            }
            else if (path_step == 3)
            {
                root = root->se;
            }
            else if (path_step == 4)
            {
                root = root->sw;
            }
        }

        if((quadtree_node_isempty(root) || (quadtree_node_isleaf(root))) && (patharray[patharray[40] - 1] == 2 || patharray[patharray[40] - 1] == 4))
        {
            // printf("\n Finding/Balancing NorthEast Neighbour");
            common_ancestor_diagonal(tree->root, root);

            int diagonal_path_size = diagonal_patharray[40];
            int j = 0;
            int diagonal_pathstep = -1;
            int ancestor_pos = -1;
            if(patharray[patharray[40] - 1] == 2)
            {
                for (j = diagonal_path_size - 1; j >= 0; j--)
                {
                    diagonal_pathstep = diagonal_patharray[j];
                    if (diagonal_pathstep == 1)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 2)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 3)
                    {
                        // printf("\n Found common ancestor for NorthEast neighbour");
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 4)
                    {
                        // printf("\n Found common ancestor for NorthEast neighbour");
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 0)
                    {
                        // TODO - Fix this problem 
                        //  printf("\n Warning - Diagonal_Patharray has zero value problems");
                    }
                    else
                    {
                        printf("\n ERROR - Some random value corrupted patharray");
                        exit(2);
                    }
                }
            }
            else if(patharray[patharray[40] - 1] == 4)
            {
                for (j = diagonal_path_size - 1; j >= 0; j--)
                {
                    diagonal_pathstep = diagonal_patharray[j];
                    if (diagonal_pathstep == 1)
                    {
                        // printf("\n Found common ancestor for SouthEast neighbour");
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 2)
                    {
                        // printf("\n Found common ancestor for SouthEast neighbour");
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 3)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 4)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 0)
                    {
                        //  printf("\n Warning - Diagonal_Patharray has zero value problems");
                    }
                    else
                    {
                        printf("\n ERROR - Some random value corrupted patharray");
                        exit(2);
                    }
                }
            }

            root = tree->root;
            j = ancestor_pos;
            int diagonal_path_step = 0;

            root = reach_ancestor(root, diagonal_patharray, ancestor_pos);

            for (j = ancestor_pos; j <= patharray[40] - 2; j++)
            {
                diagonal_path_step = diagonal_patharray[j];
                if ((quadtree_node_isempty(root)) || (quadtree_node_isleaf(root)))
                {
                    // printf("\n In the if case %lf, %lf ", (root->bounds->nw->x + root->bounds->se->x) / 2, (root->bounds->nw->y + root->bounds->se->y) / 2);
                    split_node_newpoints(tree, root);
                    temp = root;
                    if (diagonal_path_step != 1 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->sw);
                        leaf_iter++;
                    }

                    if (diagonal_path_step != 2 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->se);
                        leaf_iter++;
                    }

                    if (diagonal_path_step != 3 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->nw);
                        leaf_iter++;
                    }

                    if (diagonal_path_step != 4 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->ne);
                        leaf_iter++;
                    }
                }

                if (diagonal_path_step == 1)
                {
                    root = root->sw;
                }
                else if (diagonal_path_step == 2)
                {
                    root = root->se;
                }
                else if (diagonal_path_step == 3)
                {
                    root = root->nw;
                }
                else if (diagonal_path_step == 4)
                {
                    root = root->ne;
                }
            }
        }
    }

    // Western Neighbour
    if (direction == 2)
    {
        // printf("\n Finding Western Neighbour");
        int i = ancestor_pos;
        for (i = ancestor_pos; i <= patharray[40] - 2; i++)
        {
            path_step = patharray[i];
            if ((quadtree_node_isempty(root)) || (quadtree_node_isleaf(root)))
            {
                // printf("\n Neighbour split : West");
                split_node_newpoints(tree, root);
                temp = root;

                if (path_step != 1 || (i == patharray[40] - 2))
                {
                    // printf("\n Created new neighbour node : West");
                    leaf_array[leaf_iter] = *(temp->ne);
                    leaf_iter++;
                }

                if (path_step != 2 || (i == patharray[40] - 2))
                {
                    // printf("\n Created new neighbour node : West");
                    leaf_array[leaf_iter] = *(temp->nw);
                    leaf_iter++;
                }

                if (path_step != 3 || (i == patharray[40] - 2))
                {
                    // printf("\n Created new neighbour node : West");
                    leaf_array[leaf_iter] = *(temp->se);
                    leaf_iter++;
                }

                if (path_step != 4 || (i == patharray[40] - 2))
                {
                    // printf("\n Created new neighbour node: West");
                    leaf_array[leaf_iter] = *(temp->sw);
                    leaf_iter++;
                }
            }
            if (path_step == 1)
            {
                root = root->ne;
            }
            else if (path_step == 2)
            {
                root = root->nw;
            }
            else if (path_step == 3)
            {
                root = root->se;
            }
            else if (path_step == 4)
            {
                root = root->sw;
            }
        }

        if((quadtree_node_isempty(root) || (quadtree_node_isleaf(root))) && (patharray[patharray[40] - 1] == 1 || patharray[patharray[40] - 1] == 3))
        {
            // printf("\n Finding/Balancing NorthWest Neighbour");
            common_ancestor_diagonal(tree->root, root);

            int diagonal_path_size = diagonal_patharray[40];
            int j = 0;
            int diagonal_pathstep = -1;
            int ancestor_pos = -1;

            if(patharray[patharray[40] - 1] == 1)
            {
                for (j = diagonal_path_size - 1; j >= 0; j--)
                {
                    diagonal_pathstep = diagonal_patharray[j];
                    if (diagonal_pathstep == 1)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 2)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 3)
                    {
                        // printf("\n Found common ancestor for NorthWest neighbour");
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 4)
                    {
                        // printf("\n Found common ancestor for NorthWest neighbour");
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 0)
                    {
                        //  printf("\n Warning - Diagonal_Patharray has zero value problems");
                    }
                    else
                    {
                        printf("\n ERROR - Some random value corrupted patharray");
                        exit(2);
                    }
                }
            }
            else if(patharray[patharray[40] - 1] == 3)
            {
                for (j = diagonal_path_size - 1; j >= 0; j--)
                {
                    diagonal_pathstep = diagonal_patharray[j];
                    if (diagonal_pathstep == 1)
                    {
                        // printf("\n Found common ancestor for SouthWest neighbour");
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 2)
                    {
                        // printf("\n Found common ancestor for SouthWest neighbour");
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 3)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 4)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 0)
                    {
                        //  printf("\n Warning - Diagonal_Patharray has zero value problems");
                    }
                    else
                    {
                        printf("\n ERROR - Some random value corrupted patharray");
                        exit(2);
                    }
                }
            }
            
            root = tree->root;
            j = ancestor_pos;
            int diagonal_path_step = 0;

            root = reach_ancestor(root, diagonal_patharray, ancestor_pos);

            for (j = ancestor_pos; j <= patharray[40] - 2; j++)
            {
                diagonal_path_step = diagonal_patharray[j];
                if ((quadtree_node_isempty(root)) || (quadtree_node_isleaf(root)))
                {
                    // printf("\n Neighbour split : NorthWest");
                    // printf("\n In the if case %lf, %lf ", (root->bounds->nw->x + root->bounds->se->x) / 2, (root->bounds->nw->y + root->bounds->se->y) / 2);
                    split_node_newpoints(tree, root);
                    temp = root;
                    if (diagonal_path_step != 1 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->sw);
                        leaf_iter++;
                    }

                    if (diagonal_path_step != 2 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->se);
                        leaf_iter++;
                    }

                    if (diagonal_path_step != 3 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->nw);
                        leaf_iter++;
                    }

                    if (diagonal_path_step != 4 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->ne);
                        leaf_iter++;
                    }
                }

                if (diagonal_path_step == 1)
                {
                    root = root->sw;
                }
                else if (diagonal_path_step == 2)
                {
                    root = root->se;
                }
                else if (diagonal_path_step == 3)
                {
                    root = root->nw;
                }
                else if (diagonal_path_step == 4)
                {
                    root = root->ne;
                }
            }
        }
    }

    // Northern Neighbour
    if (direction == 3)
    {
        // printf("\n Finding Northern Neighbour");
        for (int i = ancestor_pos; i <= patharray[40] - 2; i++)
        {
            path_step = patharray[i];
            if ((quadtree_node_isempty(root)) || (quadtree_node_isleaf(root)))
            {
                // printf("\n Neighbour split : North");
                split_node_newpoints(tree, root);
                temp = root;

                if (path_step != 1 || (i == patharray[40] -2))
                {
                    // printf("\n Created new neighbour node : North");
                    leaf_array[leaf_iter] = *(temp->sw);
                    leaf_iter++;
                }

                if (path_step != 2 || (i == patharray[40] -2))
                {
                    // printf("\n Created new neighbour node : North");
                    leaf_array[leaf_iter] = *(temp->se);
                    leaf_iter++;
                }

                if (path_step != 3 || (i == patharray[40] -2))
                {
                    // printf("\n Created new neighbour node: North");
                    leaf_array[leaf_iter] = *(temp->nw);
                    leaf_iter++;
                }

                if (path_step != 4 || (i == patharray[40] -2))
                {
                    // printf("\n Created new neighbour node : North");
                    leaf_array[leaf_iter] = *(temp->ne);
                    leaf_iter++;
                }
            }
            if (path_step == 1)
            {
                root = root->sw;
            }
            else if (path_step == 2)
            {
                root = root->se;
            }
            else if (path_step == 3)
            {
                root = root->nw;
            }
            else if (path_step == 4)
            {
                root = root->ne;
            }
        }

        if((quadtree_node_isempty(root) || (quadtree_node_isleaf(root))) && (patharray[patharray[40] - 1] == 1 || patharray[patharray[40] - 1] == 2))
        {
            common_ancestor_diagonal(tree->root, root);

            int diagonal_path_size = diagonal_patharray[40];
            int j = 0;
            int diagonal_pathstep = -1;
            int ancestor_pos = -1;
            if(patharray[patharray[40] - 1] == 1)
            {
                for (j = diagonal_path_size - 1; j >= 0; j--)
                {
                    diagonal_pathstep = diagonal_patharray[j];
                    if (diagonal_pathstep == 1)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 2)
                    {
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 3)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 4)
                    {
                        // printf("\n Found common ancestor for NorthEast neighbour");
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 0)
                    {
                        //  printf("\n Warning - Diagonal_Patharray has zero value problems");
                    }
                    else
                    {
                        printf("\n ERROR - Some random value corrupted patharray");
                        exit(2);
                    }
                }
            }
            else if(patharray[patharray[40] - 1] == 2)
            {
                for (j = diagonal_path_size - 1; j >= 0; j--)
                {
                    diagonal_pathstep = diagonal_patharray[j];
                    if (diagonal_pathstep == 1)
                    {
                        // printf("\n Found common ancestor for SouthEast neighbour");
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 2)
                    {
                        // printf("\n Found common ancestor for SouthEast neighbour");
                        continue;
                    }
                    else if (diagonal_pathstep == 3)
                    {
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 4)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 0)
                    {
                        //  printf("\n Warning - Diagonal_Patharray has zero value problems");
                    }
                    else
                    {
                        printf("\n ERROR - Some random value corrupted patharray");
                        exit(2);
                    }
                }
            }

            root = tree->root;
            j = ancestor_pos;
            int diagonal_path_step = 0;

            root = reach_ancestor(root, diagonal_patharray, ancestor_pos);

            for (j = ancestor_pos; j <= patharray[40] - 2; j++)
            {
                diagonal_path_step = diagonal_patharray[j];
                if ((quadtree_node_isempty(root)) || (quadtree_node_isleaf(root)))
                {
                    // printf("\n In the if case %lf, %lf ", (root->bounds->nw->x + root->bounds->se->x) / 2, (root->bounds->nw->y + root->bounds->se->y) / 2);
                    split_node_newpoints(tree, root);
                    temp = root;
                    if (diagonal_path_step != 1 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->ne);
                        leaf_iter++;
                    }

                    if (diagonal_path_step != 2 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->nw);
                        leaf_iter++;
                    }

                    if (diagonal_path_step != 3 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->se);
                        leaf_iter++;
                    }

                    if (diagonal_path_step != 4 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->sw);
                        leaf_iter++;
                    }
                }

                if (diagonal_path_step == 1)
                {
                    root = root->ne;
                }
                else if (diagonal_path_step == 2)
                {
                    root = root->nw;
                }
                else if (diagonal_path_step == 3)
                {
                    root = root->se;
                }
                else if (diagonal_path_step == 4)
                {
                    root = root->sw;
                }
            }
        }
    }

    // Southern Neighbour
    if (direction == 4)
    {
        // printf("\n Finding Southern Neighbour");
        int i = ancestor_pos;
        for (i = ancestor_pos; i <= patharray[40] - 2; i++)
        {
            path_step = patharray[i];
            if ((quadtree_node_isempty(root)) || (quadtree_node_isleaf(root)))
            {
                // printf("\n Neighbour split : South");
                // printf("\n In the if case %lf, %lf ", (root->bounds->nw->x + root->bounds->se->x) / 2, (root->bounds->nw->y + root->bounds->se->y) / 2);
                split_node_newpoints(tree, root);
                temp = root;
                if (path_step != 1 || (i == patharray[40] -2))
                {
                    // printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp->sw);
                    leaf_iter++;
                }

                if (path_step != 2 || (i == patharray[40] -2))
                {
                    // printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp->se);
                    leaf_iter++;
                }

                if (path_step != 3 || (i == patharray[40] -2))
                {
                    // printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp->nw);
                    leaf_iter++;
                }

                if (path_step != 4 || (i == patharray[40] -2))
                {
                    // printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp->ne);
                    leaf_iter++;
                }
            }

            if (path_step == 1)
            {
                root = root->sw;
            }
            else if (path_step == 2)
            {
                root = root->se;
            }
            else if (path_step == 3)
            {
                root = root->nw;
            }
            else if (path_step == 4)
            {
                root = root->ne;
            }
        }

        if((quadtree_node_isempty(root) || (quadtree_node_isleaf(root))) && (patharray[patharray[40] - 1] == 3 || patharray[patharray[40] - 1] == 4))
        {
            common_ancestor_diagonal(tree->root, root);

            int diagonal_path_size = diagonal_patharray[40];
            int j = 0;
            int diagonal_pathstep = -1;
            int ancestor_pos = -1;
            if(patharray[patharray[40] - 1] == 3)
            {
                for (j = diagonal_path_size - 1; j >= 0; j--)
                {
                    diagonal_pathstep = diagonal_patharray[j];
                    if (diagonal_pathstep == 1)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 2)
                    {
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 3)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 4)
                    {
                        // printf("\n Found common ancestor for NorthEast neighbour");
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 0)
                    {
                        //  printf("\n Warning - Diagonal_Patharray has zero value problems");
                    }
                    else
                    {
                        printf("\n ERROR - Some random value corrupted patharray");
                        exit(2);
                    }
                }
            }
            else if(patharray[patharray[40] - 1] == 4)
            {
                for (j = diagonal_path_size - 1; j >= 0; j--)
                {
                    diagonal_pathstep = diagonal_patharray[j];
                    if (diagonal_pathstep == 1)
                    {
                        // printf("\n Found common ancestor for SouthEast neighbour");
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 2)
                    {
                        // printf("\n Found common ancestor for SouthEast neighbour");
                        continue;
                    }
                    else if (diagonal_pathstep == 3)
                    {
                        ancestor_pos = j;
                        break;
                    }
                    else if (diagonal_pathstep == 4)
                    {
                        continue;
                    }
                    else if (diagonal_pathstep == 0)
                    {
                        //  printf("\n Warning - Diagonal_Patharray has zero value problems");
                    }
                    else
                    {
                        printf("\n ERROR - Some random value corrupted patharray");
                        exit(2);
                    }
                }
            }

            root = tree->root;
            j = ancestor_pos;
            int diagonal_path_step = 0;

            root = reach_ancestor(root, diagonal_patharray, ancestor_pos);

            for (j = ancestor_pos; j <= patharray[40] - 2; j++)
            {
                diagonal_path_step = diagonal_patharray[j];
                if ((quadtree_node_isempty(root)) || (quadtree_node_isleaf(root)))
                {
                    // printf("\n In the if case %lf, %lf ", (root->bounds->nw->x + root->bounds->se->x) / 2, (root->bounds->nw->y + root->bounds->se->y) / 2);
                    split_node_newpoints(tree, root);
                    temp = root;
                    if (diagonal_path_step != 1 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->ne);
                        leaf_iter++;
                    }

                    if (diagonal_path_step != 2 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->nw);
                        leaf_iter++;
                    }

                    if (diagonal_path_step != 3 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->se);
                        leaf_iter++;
                    }

                    if (diagonal_path_step != 4 || (i == diagonal_patharray[40] -2))
                    {
                        leaf_array[leaf_iter] = *(temp->sw);
                        leaf_iter++;
                    }
                }

                if (diagonal_path_step == 1)
                {
                    root = root->ne;
                }
                else if (diagonal_path_step == 2)
                {
                    root = root->nw;
                }
                else if (diagonal_path_step == 3)
                {
                    root = root->se;
                }
                else if (diagonal_path_step == 4)
                {
                    root = root->sw;
                }
            }
        }
    }
}

void find_neighbourset(int patharray[41], quadtree_node_t *node)
{
    int path_size = patharray[40];
    int i = 0;
    int pathstep = -1;
    int direction = 0;
    int ancestor_pos = -1;

    // NW - 1, NE - 2, SW - 3 , SE - 4

    // To find path array
    /*
    for(i = path_size - 1; i>= 0; i--)
    {
        printf("\n The path point is %d", patharray[i]);
    }
    */
    // For Eastern neighbour
    direction = 1;
    ancestor_pos = east_ancestor(patharray, path_size);
    if (ancestor_pos != -1)
    {
        // Neighbour exists
        // printf("\n Found common ancestor for Eastern neighbour");
        balance_neighboursset(patharray, ancestor_pos, direction);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Eastern Neighbour does not exist");
    }

    // For Western Neighbour
    direction = 2;
    ancestor_pos = west_ancestor(patharray, path_size);
    if (ancestor_pos != -1)
    {
        // Neighbour exists
        balance_neighboursset(patharray, ancestor_pos, direction);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Western Neighbour does not exist");
    }

    // For Northern Neighbour
    direction = 3;
    ancestor_pos = north_ancestor(patharray, path_size);
    if (ancestor_pos != -1)
    {
        // Neighbour exists
        balance_neighboursset(patharray, ancestor_pos, direction);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Northern Neighbour does not exist");
    }

    // For Southern Neighbour
    direction = 4;
    ancestor_pos = south_ancestor(patharray, path_size);
    if (ancestor_pos != -1)
    {
        // Neighbour exists
        balance_neighboursset(patharray, ancestor_pos, direction);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Southern Neighbour does not exist");
    }
}

void balance_neighboursset(int patharray[41], int ancestor_pos, int direction)
{
    // Direction
    // East - 1 , West - 2, North -3, South - 4
    // printf("\n Start 1");
    quadtree_node_t *node = tree->root;
    int path_step = 0;
    int i = 0;
    char *filename = "neighbour.txt";

    // printf("\n The patharray is %d and neighbour pos is %d", patharray[40], ancestor_pos);
    node = reach_ancestor(node, patharray, ancestor_pos);

    if (!(node))
    {
        printf("\n ERROR : Ghost of the past, tree traversal went awry");
        exit(2);
    }

    // Eastern Neighbour
    if (direction == 1)
    {
        // printf("\n Finding Eastern Neighbour");
        int i = ancestor_pos;
        // printf("\n The neighbour pos is %d", i);
        for (i = ancestor_pos; i <= patharray[40] - 1; i++)
        {
            path_step = patharray[i];
            if (path_step == 1)
            {
                // printf("\n1");
                node = node->ne;
            }
            else if (path_step == 2)
            {
                // printf("\n2");
                node = node->nw;
            }
            else if (path_step == 3)
            {
                // printf("\n3");
                node = node->se;
            }
            else if (path_step == 4)
            {
                // printf("\n4");
                node = node->sw;
            }
            else
            {
                printf("ERROR : 2nd stage path traversal for neighbour set went awry");
                exit(2);
            }
            // printf("\n The newer i is %d", i);
            if (quadtree_node_isempty(node))
            {
                double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
                double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
                neighbourset(1, filename, xcord, ycord);
                // printf("\n Point A1 - (%lf,%lf) ", xcord, ycord);
                northern_diagonal_neighbourset(node, 1);
                southern_diagonal_neighbourset(node, 1);
                break;
            }
            else if (quadtree_node_isleaf(node))
            {
                neighbourset(1, filename, node->point->x, node->point->y);
                // printf("\n Point B1 - (%lf,%lf) ", node->point->x, node->point->y);
                northern_diagonal_neighbourset(node, 1);
                southern_diagonal_neighbourset(node, 1);
                break;
            }
            // The neighbours are two
            else if (i == patharray[40] - 1)
            {
                if (quadtree_node_isempty(node->nw))
                {
                    double xcord = (node->nw->bounds->nw->x + node->nw->bounds->se->x) / 2;
                    double ycord = (node->nw->bounds->nw->y + node->nw->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    northern_diagonal_neighbourset(node->nw, 1);
                    // printf("\n Point A - (%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->nw))
                {
                    neighbourset(1, filename, node->nw->point->x, node->nw->point->y);
                    // printf("\n Point B- (%lf,%lf) ", node->nw->point->x, node->nw->point->y);
                    northern_diagonal_neighbourset(node->nw, 1);
                }

                if (quadtree_node_isempty(node->sw))
                {
                    double xcord = (node->sw->bounds->nw->x + node->sw->bounds->se->x) / 2;
                    double ycord = (node->sw->bounds->nw->y + node->sw->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    southern_diagonal_neighbourset(node->sw, 1);
                    // printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->sw))
                {
                    neighbourset(1, filename, node->sw->point->x, node->sw->point->y);
                    // printf("(%lf,%lf) ", node->sw->point->x, node->sw->point->y);
                    southern_diagonal_neighbourset(node->sw, 1);
                }
                break;
            }
        }
    }

    // Western Neighbour
    if (direction == 2)
    {
        // printf("\n Finding Western Neighbour");
        int i = ancestor_pos;
        for (i = ancestor_pos; i <= patharray[40] - 1; i++)
        {
            path_step = patharray[i];

            if (path_step == 1)
            {
                node = node->ne;
            }
            else if (path_step == 2)
            {
                node = node->nw;
            }
            else if (path_step == 3)
            {
                node = node->se;
            }
            else if (path_step == 4)
            {
                node = node->sw;
            }

            if (quadtree_node_isempty(node))
            {
                double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
                double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
                neighbourset(1, filename, xcord, ycord);
                // printf("(%lf,%lf) ", xcord, ycord);
                northern_diagonal_neighbourset(node, 2);
                southern_diagonal_neighbourset(node, 2);
                break;
            }
            else if (quadtree_node_isleaf(node))
            {
                neighbourset(1, filename, node->point->x, node->point->y);
                northern_diagonal_neighbourset(node, 2);
                southern_diagonal_neighbourset(node, 2);
                break;
            }
            else if (i == patharray[40] - 1)
            {
                if (quadtree_node_isempty(node->ne))
                {
                    double xcord = (node->ne->bounds->nw->x + node->ne->bounds->se->x) / 2;
                    double ycord = (node->ne->bounds->nw->y + node->ne->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    northern_diagonal_neighbourset(node->ne, 2);
                    // printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->ne))
                {
                    neighbourset(1, filename, node->ne->point->x, node->ne->point->y);
                    northern_diagonal_neighbourset(node->ne, 2);
                }

                if (quadtree_node_isempty(node->se))
                {
                    double xcord = (node->se->bounds->nw->x + node->se->bounds->se->x) / 2;
                    double ycord = (node->se->bounds->nw->y + node->se->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    // printf("(%lf,%lf) ", xcord, ycord);
                    southern_diagonal_neighbourset(node->se, 2);
                }
                else if (quadtree_node_isleaf(node->se))
                {
                    neighbourset(1, filename, node->se->point->x, node->se->point->y);
                    southern_diagonal_neighbourset(node->se, 2);
                }
                break;
            }
        }
    }

    // Northern Neighbour
    if (direction == 3)
    {
        // printf("\n Finding Northern Neighbour");
        int i = ancestor_pos;
        for (i = ancestor_pos; i <= patharray[40] - 1; i++)
        {
            path_step = patharray[i];
            if (path_step == 1)
            {
                node = node->sw;
            }
            else if (path_step == 2)
            {
                node = node->se;
            }
            else if (path_step == 3)
            {
                node = node->nw;
            }
            else if (path_step == 4)
            {
                node = node->ne;
            }

            if (quadtree_node_isempty(node))
            {
                double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
                double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
                neighbourset(1, filename, xcord, ycord);
                // printf("(%lf,%lf) ", xcord, ycord);
                eastern_diagonal_neighbourset(node, 1);
                western_diagonal_neighbourset(node, 1);
                break;
            }
            else if (quadtree_node_isleaf(node))
            {
                neighbourset(1, filename, node->point->x, node->point->y);
                eastern_diagonal_neighbourset(node, 1);
                western_diagonal_neighbourset(node, 1);
                break;
            }
            else if (i == patharray[40] - 1)
            {
                if (quadtree_node_isempty(node->se))
                {
                    double xcord = (node->se->bounds->nw->x + node->se->bounds->se->x) / 2;
                    double ycord = (node->se->bounds->nw->y + node->se->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    eastern_diagonal_neighbourset(node->se, 1);
                    // printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->se))
                {
                    neighbourset(1, filename, node->se->point->x, node->se->point->y);
                    eastern_diagonal_neighbourset(node->se, 1); 
                }

                if (quadtree_node_isempty(node->sw))
                {
                    double xcord = (node->sw->bounds->nw->x + node->sw->bounds->se->x) / 2;
                    double ycord = (node->sw->bounds->nw->y + node->sw->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    western_diagonal_neighbourset(node->sw, 1);
                    // printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->sw))
                {
                    neighbourset(1, filename, node->sw->point->x, node->sw->point->y);
                    western_diagonal_neighbourset(node->sw, 1);
                }
                break;
            }
        }
    }

    // Southern Neighbour
    if (direction == 4)
    {
        // printf("\n Finding Southern Neighbour");
        int i = ancestor_pos;
        for (i = ancestor_pos; i <= patharray[40] - 1; i++)
        {
            path_step = patharray[i];

            if (path_step == 1)
            {
                node = node->sw;
            }
            else if (path_step == 2)
            {
                node = node->se;
            }
            else if (path_step == 3)
            {
                node = node->nw;
            }
            else if (path_step == 4)
            {
                node = node->ne;
            }

            if (quadtree_node_isempty(node))
            {
                double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
                double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
                neighbourset(1, filename, xcord, ycord);
                // printf("(%lf,%lf) ", xcord, ycord);
                eastern_diagonal_neighbourset(node, 1);
                western_diagonal_neighbourset(node, 1);
                break;
            }
            else if (quadtree_node_isleaf(node))
            {
                neighbourset(1, filename, node->point->x, node->point->y);
                eastern_diagonal_neighbourset(node, 1);
                western_diagonal_neighbourset(node, 1);
                break;
            }
            else if (i == patharray[40] - 1)
            {
                if (quadtree_node_isempty(node->nw))
                {
                    double xcord = (node->nw->bounds->nw->x + node->nw->bounds->se->x) / 2;
                    double ycord = (node->nw->bounds->nw->y + node->nw->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    western_diagonal_neighbourset(node->nw, 1);
                    // printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->nw))
                {
                    neighbourset(1, filename, node->nw->point->x, node->nw->point->y);
                    western_diagonal_neighbourset(node->nw, 1);
                }

                if (quadtree_node_isempty(node->ne))
                {
                    double xcord = (node->ne->bounds->nw->x + node->ne->bounds->se->x) / 2;
                    double ycord = (node->ne->bounds->nw->y + node->ne->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    eastern_diagonal_neighbourset(node->ne, 1);
                    // printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->ne))
                {
                    neighbourset(1, filename, node->ne->point->x, node->ne->point->y);
                    eastern_diagonal_neighbourset(node->ne, 1);
                }
                break;
            }
        }
    }
}

void eastern_diagonal_neighbourset(quadtree_node_t *node, int mainnode_direction)
{
    common_ancestor_diagonal(tree->root, node);
    quadtree_node_t *root = tree->root;
    int diagonal_path_size = diagonal_patharray[40];
    int j = 0;
    int diagonal_pathstep = -1;
    int ancestor_pos = -1;
    char *filename = "neighbour.txt";

    for (j = diagonal_path_size - 1; j >= 0; j--)
    {
        diagonal_pathstep = diagonal_patharray[j];
        if (diagonal_pathstep == 1)
        {
            ancestor_pos = j;
            break;
        }
        else if (diagonal_pathstep == 2)
        {
            continue;
        }
        else if (diagonal_pathstep == 3)
        {
            ancestor_pos = j;
            break;
        }
        else if (diagonal_pathstep == 4)
        {
            continue;
        }
        else if (diagonal_pathstep == 0)
        {
            printf("\n Warning - Diagonal_Patharray has zero value problems");
            continue;
        }
        else
        {
            printf("\n ERROR - Some random value corrupted patharray");
            exit(2);
        }
    }
    if (ancestor_pos == -1)
    {
        return;
    }

    j = ancestor_pos;
    int diagonal_path_step = 0;
    root = reach_ancestor(root, diagonal_patharray, ancestor_pos);

    for (j = ancestor_pos; j <= diagonal_patharray[40] - 1; j++)
    {
        diagonal_path_step = diagonal_patharray[j];
        if (diagonal_path_step == 1)
        {
            root = root->ne;
        }
        else if (diagonal_path_step == 2)
        {
            root = root->nw;
        }
        else if (diagonal_path_step == 3)
        {
            root = root->se;
        }
        else if (diagonal_path_step == 4)
        {
            root = root->sw;
        }
        else
        {
            printf("ERROR : 2nd stage path traversal for east diagonal_neighbour went awry");
            exit(2);
        }
        if (quadtree_node_isempty(root))
        {
            double xcord = (root->bounds->nw->x + root->bounds->se->x) / 2;
            double ycord = (root->bounds->nw->y + root->bounds->se->y) / 2;
            neighbourset(1, filename, xcord, ycord);
            break;
        }
        else if (quadtree_node_isleaf(root))
        {
            neighbourset(1, filename, root->point->x, root->point->y);
            break;
        }
        else if (j == patharray[40] - 1)
        {
            if(mainnode_direction == 1)
            {
                if (quadtree_node_isempty(root->sw))
                {
                    double xcord = (root->sw->bounds->nw->x + root->sw->bounds->se->x) / 2;
                    double ycord = (root->sw->bounds->nw->y + root->sw->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                }
                else if (quadtree_node_isleaf(root->sw))
                {
                    neighbourset(1, filename, root->sw->point->x, root->sw->point->y);
                }
            }
            if(mainnode_direction == 2)
            {
                if (quadtree_node_isempty(root->nw))
                {
                    double xcord = (root->nw->bounds->nw->x + root->nw->bounds->se->x) / 2;
                    double ycord = (root->nw->bounds->nw->y + root->nw->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    // printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(root->nw))
                {
                    neighbourset(1, filename, root->nw->point->x, root->nw->point->y);
                }
            }
            break;
        }
    }
}

void western_diagonal_neighbourset(quadtree_node_t *node, int mainnode_direction)
{
    common_ancestor_diagonal(tree->root, node);
    quadtree_node_t *root = tree->root;
    int diagonal_path_size = diagonal_patharray[40];
    int j = 0;
    int diagonal_pathstep = -1;
    int ancestor_pos = -1;
    char *filename = "neighbour.txt";

    for (j = diagonal_path_size - 1; j >= 0; j--)
    {
        diagonal_pathstep = diagonal_patharray[j];
        if (diagonal_pathstep == 1)
        {
            continue;
        }
        else if (diagonal_pathstep == 2)
        {
            ancestor_pos = j;
            break;
        }
        else if (diagonal_pathstep == 3)
        {
            continue;
        }
        else if (diagonal_pathstep == 4)
        {
            ancestor_pos = j;
            break;
        }
        else if (diagonal_pathstep == 0)
        {
            printf("\n Warning - Diagonal_Patharray has zero value problems");
            continue;
        }
        else
        {
            printf("\n ERROR - Some random value corrupted patharray");
            exit(2);
        }
    }
    if (ancestor_pos == -1)
    {
        return;
    }

    j = ancestor_pos;
    int diagonal_path_step = 0;
    root = reach_ancestor(root, diagonal_patharray, ancestor_pos);

    for (j = ancestor_pos; j <= diagonal_patharray[40] - 1; j++)
    {
        diagonal_path_step = diagonal_patharray[j];
        if (diagonal_path_step == 1)
        {
            root = root->ne;
        }
        else if (diagonal_path_step == 2)
        {
            root = root->nw;
        }
        else if (diagonal_path_step == 3)
        {
            root = root->se;
        }
        else if (diagonal_path_step == 4)
        {
            root = root->sw;
        }
        else
        {
            printf("ERROR : 2nd stage path traversal for east diagonal_neighbour went awry");
            exit(2);
        }
        if (quadtree_node_isempty(root))
        {
            double xcord = (root->bounds->nw->x + root->bounds->se->x) / 2;
            double ycord = (root->bounds->nw->y + root->bounds->se->y) / 2;
            neighbourset(1, filename, xcord, ycord);
            break;
        }
        else if (quadtree_node_isleaf(root))
        {
            neighbourset(1, filename, root->point->x, root->point->y);
            break;
        }
        else if (j == patharray[40] - 1)
        {
            if(mainnode_direction == 1)
            {
                if (quadtree_node_isempty(root->se))
                {
                    double xcord = (root->se->bounds->nw->x + root->se->bounds->se->x) / 2;
                    double ycord = (root->se->bounds->nw->y + root->se->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                }
                else if (quadtree_node_isleaf(root->se))
                {
                    neighbourset(1, filename, root->se->point->x, root->se->point->y);
                }
            }
            if(mainnode_direction == 2)
            {
                if (quadtree_node_isempty(root->ne))
                {
                    double xcord = (root->ne->bounds->nw->x + root->ne->bounds->se->x) / 2;
                    double ycord = (root->ne->bounds->nw->y + root->ne->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    // printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(root->ne))
                {
                    neighbourset(1, filename, root->ne->point->x, root->ne->point->y);
                }
            }
            break;
        }
    }
}

void northern_diagonal_neighbourset(quadtree_node_t *node, int mainnode_direction)
{
    common_ancestor_diagonal(tree->root, node);
    quadtree_node_t *root = tree->root;
    int diagonal_path_size = diagonal_patharray[40];
    int j = 0;
    int diagonal_pathstep = -1;
    int ancestor_pos = -1;
    char *filename = "neighbour.txt";
    if(checker == 1)
    {
        printf("\n Start 2");
        printf("\n Common ancestor is %d", diagonal_patharray[40]);
    }

    for (j = diagonal_path_size - 1; j >= 0; j--)
    {
        diagonal_pathstep = diagonal_patharray[j];
        if (diagonal_pathstep == 1)
        {
            continue;
        }
        else if (diagonal_pathstep == 2)
        {
            continue;
        }
        else if (diagonal_pathstep == 3)
        {
            // printf("\n Found common ancestor for NorthEast neighbour");
            ancestor_pos = j;
            break;
        }
        else if (diagonal_pathstep == 4)
        {
            // printf("\n Found common ancestor for NorthEast neighbour");
            ancestor_pos = j;
            break;
        }
        else if (diagonal_pathstep == 0)
        {
            //  printf("\n Warning - Diagonal_Patharray has zero value problems");
        }
        else
        {
            printf("\n ERROR - Some random value corrupted patharray");
            exit(2);
        }
    }
    if (ancestor_pos == -1)
    {
        return;
    }

    j = ancestor_pos;
    if(checker == 1)
    {
        printf("\n %d is ancestor pos", j);
    }
    int diagonal_path_step = 0;

    root = reach_ancestor(root, diagonal_patharray, ancestor_pos);

    for (j = ancestor_pos; j <= diagonal_patharray[40] - 1; j++)
    {
        diagonal_path_step = diagonal_patharray[j];
        if (diagonal_path_step == 1)
        {
            root = root->sw;
        }
        else if (diagonal_path_step == 2)
        {
            root = root->se;
        }
        else if (diagonal_path_step == 3)
        {
            root = root->nw;
        }
        else if (diagonal_path_step == 4)
        {
            // printf("\n Reached proper area - 2");
            root = root->ne;
            // double xcord = (root->bounds->nw->x + root->bounds->se->x) / 2;
            // double ycord = (root->bounds->nw->y + root->bounds->se->y) / 2;
            // printf("\n Special neighbour hope - (%lf,%lf) ", xcord, ycord);
        }
        if (quadtree_node_isempty(root))
        {
            double xcord = (root->bounds->nw->x + root->bounds->se->x) / 2;
            double ycord = (root->bounds->nw->y + root->bounds->se->y) / 2;
            neighbourset(1, filename, xcord, ycord);
            if(checker == 1)
            {
                printf("\n Special neighbour 1 - (%lf,%lf) ", xcord, ycord);
            }
            break;
        }
        else if (quadtree_node_isleaf(root))
        {
            if(checker == 1)
            {
                printf("\n Special Neighbour 2 - (%lf,%lf) ",root->sw->point->x, root->sw->point->y);
            }
            neighbourset(1, filename, root->point->x, root->point->y);
            break;
        }
        else if (j == patharray[40] - 1)
        {
            if(checker == 1)
            {
                printf("\n Start 2a");
            }
            if(mainnode_direction == 1)
            {
                if (quadtree_node_isempty(root->sw))
                {
                    double xcord = (root->sw->bounds->nw->x + root->sw->bounds->se->x) / 2;
                    double ycord = (root->sw->bounds->nw->y + root->sw->bounds->se->y) / 2;
                    // printf("\n Special Neighbour 3 - (%lf,%lf) ", xcord, ycord);
                    neighbourset(1, filename, xcord, ycord);
                }
                else if (quadtree_node_isleaf(root->sw))
                {
                    // printf("\n Special Neighbour 4 - (%lf,%lf) ", root->sw->point->x, root->sw->point->y);
                    neighbourset(1, filename, root->sw->point->x, root->sw->point->y);
                }
            }
            if(mainnode_direction == 2)
            {
                if (quadtree_node_isempty(root->se))
                {
                    double xcord = (root->se->bounds->nw->x + root->se->bounds->se->x) / 2;
                    double ycord = (root->se->bounds->nw->y + root->se->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    // printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(root->se))
                {
                    neighbourset(1, filename, root->se->point->x, root->se->point->y);
                }
            }
            break;
        }
    }
}

void southern_diagonal_neighbourset(quadtree_node_t *node, int mainnode_direction)
{
    if(checker == 1)
    {
        printf("\n Start 3");
    }
    common_ancestor_diagonal(tree->root, node);
    quadtree_node_t *root = tree->root;
    int diagonal_path_size = diagonal_patharray[40];
    int j = 0;
    int diagonal_pathstep = -1;
    int ancestor_pos = -1;
    char *filename = "neighbour.txt";

    for (j = diagonal_path_size - 1; j >= 0; j--)
    {
        diagonal_pathstep = diagonal_patharray[j];
        if (diagonal_pathstep == 1)
        {
            // printf("\n Found common ancestor for SouthEast neighbour");
            ancestor_pos = j;
            break;
        }
        else if (diagonal_pathstep == 2)
        {
            // printf("\n Found common ancestor for SouthEast neighbour");
            ancestor_pos = j;
            break;
        }
        else if (diagonal_pathstep == 3)
        {
            continue;
        }
        else if (diagonal_pathstep == 4)
        {
            continue;
        }
        else if (diagonal_pathstep == 0)
        {
            //  printf("\n Warning - Diagonal_Patharray has zero value problems");
        }
        else
        {
            printf("\n ERROR - Some random value corrupted patharray");
            exit(2);
        }
    }
    if (ancestor_pos == -1)
    {
        return;
    }

    j = ancestor_pos;
    // printf("\n %d is ancestor pos", j);
    int diagonal_path_step = 0;

    root = reach_ancestor(root, diagonal_patharray, ancestor_pos);

    for (j = ancestor_pos; j <= diagonal_patharray[40] - 1; j++)
    {
        diagonal_path_step = diagonal_patharray[j];
        if (diagonal_path_step == 1)
        {
            root = root->sw;
        }
        else if (diagonal_path_step == 2)
        {
            root = root->se;
        }
        else if (diagonal_path_step == 3)
        {
            root = root->nw;
        }
        else if (diagonal_path_step == 4)
        {
            // printf("\n Reached proper area - 2");
            root = root->ne;
        }
        if (quadtree_node_isempty(root))
        {
            double xcord = (root->bounds->nw->x + root->bounds->se->x) / 2;
            double ycord = (root->bounds->nw->y + root->bounds->se->y) / 2;
            neighbourset(1, filename, xcord, ycord);
            if(checker == 1)
            {
                printf("\n Special neighbour 3 - (%lf,%lf) ", xcord, ycord);
            }
            break;
        }
        else if (quadtree_node_isleaf(root))
        {
            if(checker == 1)
            {
                printf("\n Special Neighbour 4 - (%lf,%lf) ",root->sw->point->x, root->sw->point->y);
            }
            neighbourset(1, filename, root->point->x, root->point->y);
            break;
        }
        else if (j == patharray[40] - 1)
        {
            if(checker == 1)
            {
                printf("\n Start 5");
            }
            if(mainnode_direction == 1)
            {
                if (quadtree_node_isempty(root->nw))
                {
                    double xcord = (root->nw->bounds->nw->x + root->nw->bounds->se->x) / 2;
                    double ycord = (root->nw->bounds->nw->y + root->nw->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    // printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(root->nw))
                {
                    neighbourset(1, filename, root->nw->point->x, root->nw->point->y);
                }
            }    

            if(mainnode_direction == 2)
            {
                if (quadtree_node_isempty(root->ne))
                {
                    double xcord = (root->ne->bounds->nw->x + root->ne->bounds->se->x) / 2;
                    double ycord = (root->ne->bounds->nw->y + root->ne->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    // printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(root->ne))
                {
                    neighbourset(1, filename, root->ne->point->x, root->ne->point->y);
                }
            }    
            break;
        }
    }
}

void valley_refinement(quadtree_node_t *valley_node, int flag)
{
    common_treeroute(tree->root, valley_node);
    int path_size = patharray[40];
    double xcord = (valley_node->bounds->nw->x + valley_node->bounds->se->x) / 2;
    double ycord = (valley_node->bounds->nw->y + valley_node->bounds->se->y) / 2;
    // if(xcord == 0.966796875 && (ycord == -0.029296875 || ycord == 0.029296875))
    // {
    //   checker = 2;
    //   printf("\n Yabba Dabba Doo");
    //   printf("\n Pathsize is %d", path_size);
    //   printf("\n Height of tree is %d", height_of_tree);
    // }
    // else
    // {
    //     checker = 0;
    // }

    // if(path_size < height_of_tree -5 && flag == 1)
    // {
    //     return;
    // }
    // if(checker == 2)
    // {
    //     printf("\n Strange bug");
    // }
    int k = 0;                     
    int pathstep = -1;              
    int direction = 0;             
    int ancestor_pos = -1;
    int north = 0;
    int east = 0;
    int south = 0;
    int west = 0;
    int north_check = 0;
    int south_check = 0;
    int east_check = 0;
    int west_check = 0;
    quadtree_node_t *north_node = NULL;
    quadtree_node_t *east_node = NULL;
    quadtree_node_t *south_node = NULL;
    quadtree_node_t *west_node = NULL;

    for (k = path_size - 1; k >= 0; k--) // Traversing from leaf to root of tree
    {
        pathstep = patharray[k];
        if (pathstep == 1)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Eastern neighbour");
            ancestor_pos = k;
            break;
        }
        else if (pathstep == 2)
        {
            continue;
        }
        else if (pathstep == 3)
        {
            // printf("\n Found common ancestor for Eastern neighbour");
            ancestor_pos = k;
            break;
        }
        else if (pathstep == 4)
        {
            continue;
        }
        else if (pathstep == 0)
        {
            printf("\n Warning - Patharray has zero value problems");
        }
        else
        {
            printf("\n ERROR - Some random value corrupted patharray");
            exit(2);
        }
    }
    if (ancestor_pos != -1)
    {
        quadtree_node_t *node = tree->root;
        int path_step = 0;
        int i = 0;
        
        node = reach_ancestor(node, patharray, ancestor_pos);

        for (i = ancestor_pos; i <= patharray[40] - 1; i++)
        {
            path_step = patharray[i];
            if (path_step == 1)
            {
                node = node->ne;
            }
            else if (path_step == 2)
            {
                node = node->nw;
            }
            else if (path_step == 3)
            {
                node = node->se;
            }
            else if (path_step == 4)
            {
                node = node->sw;
            }
            else
            {
                printf("ERROR : 2nd stage path traversal for neighbour set went awry");
            }
            // printf("\n The newer i is %d", i);
            if (quadtree_node_isempty(node))
            {
                break;
            }
            else if (quadtree_node_isleaf(node))
            {
                break;
            }
            // The neighbours are two
            else if (i == patharray[40] - 1)
            {
                east = 1;
                // printf("\n Easst one");
                break;
            }
        }
    }

    for (k = path_size - 1; k >= 0; k--)
    {
        pathstep = patharray[k];
        if (pathstep == 1)
        {
            continue;
        }
        else if (pathstep == 2)
        {
            // printf("\n Found common ancestor for Western neighbour");
            ancestor_pos = k;
            break;
        }
        else if (pathstep == 3)
        {
            continue;
        }
        else if (pathstep == 4)
        {
            // printf("\n Found common ancestor for Western neighbour");
            ancestor_pos = k;
            break;
        }
        else if (pathstep == 0)
        {
            printf("\n Warning - Patharray has zero value problems");
        }
        else
        {
            printf("\n ERROR - Some random value corrupted patharray");
            exit(2);
        }
    }
    if (ancestor_pos != -1)
    {
        quadtree_node_t *node = tree->root;
        int path_step = 0;
        int i = 0;
        
        node = reach_ancestor(node, patharray, ancestor_pos);
        for (i = ancestor_pos; i <= patharray[40] - 1; i++)
        {
            path_step = patharray[i];
            if (path_step == 1)
            {
                node = node->ne;
            }
            else if (path_step == 2)
            {
                node = node->nw;
            }
            else if (path_step == 3)
            {
                node = node->se;
            }
            else if (path_step == 4)
            {
                node = node->sw;
            }
            else
            {
                printf("ERROR : 2nd stage path traversal for neighbour set went awry");
            }
            // printf("\n The newer i is %d", i);
            if (quadtree_node_isempty(node))
            {
                break;
            }
            else if (quadtree_node_isleaf(node))
            {
                break;
            }
            // The neighbours are twoif(south_node)
            else if (i == patharray[40] - 1)
            {
                west = 1;
                // printf("\n West one");
                break;
            }
        }
    }

    for (k = path_size - 1; k >= 0; k--)
    {
        pathstep = patharray[k];
        if (pathstep == 1)
        {
            continue;
        }
        else if (pathstep == 2)
        {
            continue;
        }
        else if (pathstep == 3)
        {
            // printf("\n Found common ancestor for Northern neighbour");
            ancestor_pos = k;
            break;
        }
        else if (pathstep == 4)
        {
            // printf("\n Found common ancestor for Northern neighbour");
            ancestor_pos = k;
            break;
        }
        else if (pathstep == 0)
        {
            printf("\n Warning - Patharray has zero value problems");
        }
        else
        {
            printf("\n ERROR - Some random value corrupted patharray");
            exit(2);
        }
    }
    if (ancestor_pos != -1)
    {
        quadtree_node_t *node = tree->root;
        int path_step = 0;
        int i = 0;
        
        node = reach_ancestor(node, patharray, ancestor_pos);

        for (i = ancestor_pos; i <= patharray[40] - 1; i++)
        {
            path_step = patharray[i];
            if (path_step == 1)
            {
                node = node->sw;
            }
            else if (path_step == 2)
            {
                node = node->se;
            }
            else if (path_step == 3)
            {
                node = node->nw;
            }
            else if (path_step == 4)
            {
                node = node->ne;
            }
            else
            {
                printf("ERROR : 2nd stage path traversal for neighbour set went awry");
            }
            // printf("\n The newer i is %d", i);
            if (quadtree_node_isempty(node))
            {
                break;
            }
            else if (quadtree_node_isleaf(node))
            {
                break;
            }
            // The neighbours are two
            else if (i == patharray[40] - 1)
            {
                north = 1;
                break;
            }
        }
    }

    for (k = path_size - 1; k >= 0; k--)
    {
        pathstep = patharray[k];
        if (pathstep == 1)
        {
            // printf("\n Found common ancestor for Southern neighbour");
            ancestor_pos = k;
            break;
        }
        else if (pathstep == 2)
        {
            // printf("\n Found common ancestor for Southern neighbour");
            ancestor_pos = k;
            break;
        }
        else if (pathstep == 3)
        {
            continue;
        }
        else if (pathstep == 4)
        {
            continue;
        }
        else if (pathstep == 0)
        {
            printf("\n Warning - Patharray has zero value problems");
        }
        else
        {
            printf("\n ERROR - Some random value corrupted patharray");
            exit(2);
        }
    }
    if (ancestor_pos != -1)
    {
        quadtree_node_t *node = tree->root;
        int path_step = 0;
        int i = 0;
        
        node = reach_ancestor(node, patharray, ancestor_pos);
        for (i = ancestor_pos; i <= patharray[40] - 1; i++)
        {
            path_step = patharray[i];
            if (path_step == 1)
            {
                node = node->sw;
            }
            else if (path_step == 2)
            {
                node = node->se;
            }
            else if (path_step == 3)
            {
                node = node->nw;
            }
            else if (path_step == 4)
            {
                node = node->ne;
            }
            else
            {
                printf("ERROR : 2nd stage path traversal for neighbour set went awry");
            }
            // printf("\n The newer i is %d", i);
            if (quadtree_node_isempty(node))
            {
                break;
            }
            else if (quadtree_node_isleaf(node))
            {
                break;
            }
            // The neighbours are two
            else if (i == patharray[40] - 1)
            {
                south = 1;
                // printf("\n South one");
                break;
            }
        }
    }

    if(north + east + south + west >= 1)
    {
        // printf("\n ABCD");
        split_node_newpoints(tree->root, valley_node);
    }
}

int maxDepth(quadtree_node_t *node)
{
    if (!node) 
        return 0;
    else
    {
        int nwDepth = maxDepth(node->nw);
        int neDepth = maxDepth(node->ne);
        int swDepth = maxDepth(node->sw);
        int seDepth = maxDepth(node->se);
    
        if (nwDepth >= neDepth && nwDepth >= swDepth && nwDepth >= seDepth) 
            return(nwDepth+1);
        else if (neDepth >= nwDepth && neDepth >= swDepth && nwDepth >= seDepth)
            return(neDepth+1);
        else if (swDepth >= nwDepth && swDepth >= neDepth && swDepth >= seDepth)
            return(swDepth+1);
        else
        {
            return (seDepth + 1);
        }
    }
}
