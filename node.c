#include "quadtree.h"
#include <stdio.h>

int patharray[21];
int path_iter = 0;

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
            printf("\n %f %f", (node->bounds->nw->x + node->bounds->se->x) / 2,
                   (node->bounds->nw->y + node->bounds->se->y) / 2);
        }
        else if (quadtree_node_isleaf(node))
        {
            printf("\n%f %f", node->point->x, node->point->y);
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

/* This function does not find common ancestor, just the tree path from root to node */
int *common_ancestor(quadtree_node_t *root, quadtree_node_t *node)
{
    int i = 0;
    for (i = 0; i < 21; i++)
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
    patharray[20] = path_iter; // Store height from root to leaf
    return patharray;
}

/* This function finds common_ancestor and takes the leaf(and its patharray) as input */
void find_neighbours(quadtree_t *tree, int patharray[21], quadtree_node_t *leaf_array)
{
    // printf("\n Start");

    int path_size = patharray[20]; // Specifies the height from the root to the leaf
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
    for (i = path_size - 1; i >= 0; i--) // Traversing from leaf to root of tree
    {
        pathstep = patharray[i];
        if (pathstep == 1)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Eastern neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 2)
        {
            continue;
        }
        else if (pathstep == 3)
        {
            // printf("\n Found common ancestor for Eastern neighbour");
            ancestor_pos = i;
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
        // printf("\n Found common ancestor for Eastern neighbour");
        balance_neighbour(tree, patharray, ancestor_pos, direction, leaf_array);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Eastern Neighbour does not exist");
    }

    direction = 2; // For Western Neighbour
    for (i = path_size - 1; i >= 0; i--)
    {
        pathstep = patharray[i];
        if (pathstep == 1)
        {
            continue;
        }
        else if (pathstep == 2)
        {
            // printf("\n Found common ancestor for Western neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 3)
        {
            continue;
        }
        else if (pathstep == 4)
        {
            // printf("\n Found common ancestor for Western neighbour");
            ancestor_pos = i;
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
        balance_neighbour(tree, patharray, ancestor_pos, direction, leaf_array);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Western Neighbour does not exist");
    }

    direction = 3; // For Northern Neighbour
    for (i = path_size - 1; i >= 0; i--)
    {
        pathstep = patharray[i];
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
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 4)
        {
            // printf("\n Found common ancestor for Northern neighbour");
            ancestor_pos = i;
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
        balance_neighbour(tree, patharray, ancestor_pos, direction, leaf_array);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Northern Neighbour does not exist");
    }

    direction = 4; // For Southern Neighbour
    for (i = path_size - 1; i >= 0; i--)
    {
        pathstep = patharray[i];
        if (pathstep == 1)
        {
            // printf("\n Found common ancestor for Southern neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 2)
        {
            // printf("\n Found common ancestor for Southern neighbour");
            ancestor_pos = i;
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
        balance_neighbour(tree, patharray, ancestor_pos, direction, leaf_array);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Southern Neighbour does not exist");
    }
}

/* This function finds the nieghbour of a point in specified direction */
void balance_neighbour(quadtree_t *tree, int patharray[21], int ancestor_pos, int direction, quadtree_node_t *leaf_array)
{

    // Direction
    // East - 1 , West - 2, North -3, South - 4

    quadtree_node_t *root = tree->root; // Done simply for convienience
    int path_step = 0;                  // Stores the current path value
    int i = 0;                          // Loop iterator
    quadtree_node_t *temp;

    for (i = 0; i < ancestor_pos; i++) // We quickly traverse from the root to the common ancestor of leaf
    {
        path_step = patharray[i];
        if (path_step == 1)
        {
            root = root->nw;
        }
        if (path_step == 2)
        {
            root = root->ne;
        }
        if (path_step == 3)
        {
            root = root->sw;
        }
        if (path_step == 4)
        {
            root = root->se;
        }
    }
    if (ancestor_pos == patharray[20] - 1) // When the leaf is the common ancestor
    {
        // printf("\n No need for neighbour adjustment,");
        return;
    }

    // Eastern Neighbour
    if (direction == 1)
    {
        // printf("\n Finding Eastern Neighbour");
        int i = ancestor_pos;
        for (i = ancestor_pos; i <= patharray[20] - 2; i++) // -2 because the neighbour can be one level higher
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
                if (path_step == 1)
                {
                    root = root->ne;
                }
                else
                {
                    // printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp->ne);
                    leaf_iter++;
                }

                if (path_step == 2)
                {
                    root = root->nw;
                }
                else
                {
                    // printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp->nw);
                    leaf_iter++;
                }

                if (path_step == 3)
                {
                    root = root->se;
                }
                else
                {
                    // printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp->se);
                    leaf_iter++;
                }

                if (path_step == 4)
                {
                    root = root->sw;
                }
                else
                {
                    // printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp->sw);
                    leaf_iter++;
                }
                continue;
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
    }

    // Western Neighbour
    if (direction == 2)
    {
        // printf("\n Finding Western Neighbour");
        int i = ancestor_pos;
        for (i = ancestor_pos; i <= patharray[20] - 2; i++)
        {
            path_step = patharray[i];
            if ((quadtree_node_isempty(root)) || (quadtree_node_isleaf(root)))
            {
                // printf("\n Neighbour split : West");
                split_node_newpoints(tree, root);
                temp = root;

                if (path_step == 1)
                {
                    root = root->ne;
                }
                else
                {
                    // printf("\n Created new neighbour node : West");
                    leaf_array[leaf_iter] = *(temp->ne);
                    leaf_iter++;
                }

                if (path_step == 2)
                {
                    root = root->nw;
                }
                else
                {
                    // printf("\n Created new neighbour node : West");
                    leaf_array[leaf_iter] = *(temp->nw);
                    leaf_iter++;
                }

                if (path_step == 3)
                {
                    root = root->se;
                }
                else
                {
                    // printf("\n Created new neighbour node : West");
                    leaf_array[leaf_iter] = *(temp->se);
                    leaf_iter++;
                }

                if (path_step == 4)
                {
                    root = root->sw;
                }
                else
                {
                    // printf("\n Created new neighbour node: West");
                    leaf_array[leaf_iter] = *(temp->sw);
                    leaf_iter++;
                }
                continue;
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
    }

    // Northern Neighbour
    if (direction == 3)
    {
        // printf("\n Finding Northern Neighbour");
        for (int i = ancestor_pos; i <= patharray[20] - 2; i++)
        {
            path_step = patharray[i];
            if ((quadtree_node_isempty(root)) || (quadtree_node_isleaf(root)))
            {
                // printf("\n Neighbour split : North");
                split_node_newpoints(tree, root);
                temp = root;

                if (path_step == 1)
                {
                    root = root->sw;
                }
                else
                {
                    // printf("\n Created new neighbour node : North");
                    leaf_array[leaf_iter] = *(temp->sw);
                    leaf_iter++;
                }

                if (path_step == 2)
                {
                    root = root->se;
                }
                else
                {
                    // printf("\n Created new neighbour node : North");
                    leaf_array[leaf_iter] = *(temp->se);
                    leaf_iter++;
                }

                if (path_step == 3)
                {
                    root = root->nw;
                }
                else
                {
                    // printf("\n Created new neighbour node: North");
                    leaf_array[leaf_iter] = *(temp->nw);
                    leaf_iter++;
                }

                if (path_step == 4)
                {
                    root = root->ne;
                }
                else
                {
                    // printf("\n Created new neighbour node : North");
                    leaf_array[leaf_iter] = *(temp->ne);
                    leaf_iter++;
                }
                continue;
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
    }

    // Southern Neighbour
    if (direction == 4)
    {
        // printf("\n Finding Southern Neighbour");
        int i = ancestor_pos;
        for (i = ancestor_pos; i <= patharray[20] - 2; i++)
        {
            path_step = patharray[i];
            if ((quadtree_node_isempty(root)) || (quadtree_node_isleaf(root)))
            {
                // printf("\n Neighbour split : South");
                // printf("\n In the if case %lf, %lf ", (root->bounds->nw->x + root->bounds->se->x) / 2, (root->bounds->nw->y + root->bounds->se->y) / 2);
                split_node_newpoints(tree, root);
                temp = root;
                if (path_step == 1)
                {
                    root = root->sw;
                }
                else
                {
                    // printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp->nw);
                    leaf_iter++;
                }

                if (path_step == 2)
                {
                    root = root->se;
                }
                else
                {
                    // printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp->se);
                    leaf_iter++;
                }

                if (path_step == 3)
                {
                    root = root->nw;
                }
                else
                {
                    // printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp->nw);
                    leaf_iter++;
                }

                if (path_step == 4)
                {
                    root = root->ne;
                }
                else
                {
                    // printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp->ne);
                    leaf_iter++;
                }
                continue;
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
    }
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
        return 0;
    if (!(ne = quadtree_node_with_bounds(x + hw, y - hh, x + hw * 2, y)))
        return 0;
    if (!(sw = quadtree_node_with_bounds(x, y - hh * 2, x + hw, y - hh)))
        return 0;
    if (!(se = quadtree_node_with_bounds(x + hw, y - hh * 2, x + hw * 2, y - hh)))
        return 0;

    node->nw = nw;
    node->ne = ne;
    node->sw = sw;
    node->se = se;

    if (quadtree_node_isleaf(node))
    {
        old = node->point;
        // printf("\n For point %lf, %lf ", (node->bounds->nw->x + node->bounds->se->x) / 2, (node->bounds->nw->y + node->bounds->se->y) / 2);
        // printf("\n For point %lf, %lf ", node->point->x, node->point->y);
        node->point = NULL;
        return insert_(tree, node, old);
    }
    else
    {
        printf("\n ERROR : New node not created in balancing operation");
        return 0;
    }
}

void find_neighbourset(int patharray[21], quadtree_node_t *node)
{
    // printf("\n Start");
    int path_size = patharray[20];
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
    for (i = path_size - 1; i >= 0; i--)
    {
        pathstep = patharray[i];
        if (pathstep == 1)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Eastern neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 2)
        {
            continue;
        }
        else if (pathstep == 3)
        {
            // printf("\n Found common ancestor for Eastern neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 4)
        {
            continue;
        }
        else if (pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted pathaarray");
            // exit(1);
        }
    }
    if (ancestor_pos != -1)
    {
        // Neighbour exists
        // printf("\n Found common ancestor for Eastern neighbour");
        balance_neighbourset(patharray, ancestor_pos, direction);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Eastern Neighbour does not exist");
    }

    // For Western Neighbour
    direction = 2;
    for (i = path_size - 1; i >= 0; i--)
    {
        pathstep = patharray[i];
        if (pathstep == 1)
        {
            continue;
        }
        else if (pathstep == 2)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Western neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 3)
        {
            continue;
        }
        else if (pathstep == 4)
        {
            // printf("\n Found common ancestor for Western neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted pathaarray");
            // exit(1);
        }
    }
    if (ancestor_pos != -1)
    {
        // Neighbour exists
        balance_neighbourset(patharray, ancestor_pos, direction);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Western Neighbour does not exist");
    }

    // For Northern Neighbour
    direction = 3;
    for (i = path_size - 1; i >= 0; i--)
    {
        pathstep = patharray[i];
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
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 4)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Northern neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted pathaarray");
            // exit(1);
        }
    }
    if (ancestor_pos != -1)
    {
        // Neighbour exists
        balance_neighbourset(patharray, ancestor_pos, direction);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Northern Neighbour does not exist");
    }

    // For Southern Neighbour
    direction = 4;
    for (i = path_size - 1; i >= 0; i--)
    {
        pathstep = patharray[i];
        if (pathstep == 1)
        {
            // printf("\n Found common ancestor for Southern neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 2)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Southern neighbour");
            ancestor_pos = i;
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
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted pathaarray");
            // exit(1);
        }
    }
    if (ancestor_pos != -1)
    {
        // Neighbour exists
        balance_neighbourset(patharray, ancestor_pos, direction);
        ancestor_pos = -1;
    }
    else
    {
        // printf("\n Southern Neighbour does not exist");
    }
}

void balance_neighbourset(int patharray[21], int ancestor_pos, int direction)
{

    // Direction
    // East - 1 , West - 2, North -3, South - 4

    quadtree_node_t *node = tree->root;
    int path_step = 0;
    int i = 0;
    char *filename = "neighbour.txt";

    // printf("\n The patharray is %d and neighbour pos is %d", patharray[20], ancestor_pos);
    for (i = 0; i < ancestor_pos; i++)
    {
        // printf("\n The i is %d", i);
        path_step = patharray[i];
        if (path_step == 1)
        {
            // printf("\n1");
            node = node->nw;
        }
        if (path_step == 2)
        {
            // printf("\n2");
            node = node->ne;
        }
        if (path_step == 3)
        {
            // printf("\n3");
            node = node->sw;
        }
        if (path_step == 4)
        {
            // printf("\n4");
            node = node->se;
        }
    }

    if (!(node))
    {
        printf("\n ERROR : Ghost of the past, tree traversal went awry");
    }

    // Eastern Neighbour
    if (direction == 1)
    {
        // printf("\n Finding Eastern Neighbour");
        int i = ancestor_pos;
        // printf("\n The neighbour pos is %d", i);
        for (i = ancestor_pos; i <= patharray[20] - 1; i++)
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
            }
            // printf("\n The newer i is %d", i);
            if (node->bounds != NULL && quadtree_node_isempty(node))
            {
                double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
                double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
                neighbourset(1, filename, xcord, ycord);
                printf("(%lf,%lf) ", xcord, ycord);
                break;
            }
            else if (quadtree_node_isleaf(node))
            {
                neighbourset(1, filename, node->point->x, node->point->y);
                printf("(%lf,%lf) ", node->point->x, node->point->y);
                break;
            }
            // The neighbours are two
            else if (i == patharray[20] - 1)
            {
                if (node->nw->bounds != NULL && quadtree_node_isempty(node->nw))
                {
                    double xcord = (node->nw->bounds->nw->x + node->nw->bounds->se->x) / 2;
                    double ycord = (node->nw->bounds->nw->y + node->nw->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->nw))
                {
                    neighbourset(1, filename, node->nw->point->x, node->nw->point->y);
                    printf("(%lf,%lf) ", node->nw->point->x, node->nw->point->y);
                }

                if (node->sw->bounds != NULL && quadtree_node_isempty(node->sw))
                {
                    double xcord = (node->sw->bounds->nw->x + node->sw->bounds->se->x) / 2;
                    double ycord = (node->sw->bounds->nw->y + node->sw->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->sw))
                {
                    neighbourset(1, filename, node->sw->point->x, node->sw->point->y);
                    printf("(%lf,%lf) ", node->sw->point->x, node->sw->point->y);
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
        for (i = ancestor_pos; i <= patharray[20] - 1; i++)
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

            if (node->bounds != NULL && quadtree_node_isempty(node))
            {
                double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
                double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
                neighbourset(1, filename, xcord, ycord);
                printf("(%lf,%lf) ", xcord, ycord);
                break;
            }
            else if (quadtree_node_isleaf(node))
            {
                neighbourset(1, filename, node->point->x, node->point->y);
                printf("(%lf,%lf) ", node->point->x, node->point->y);
                break;
            }
            else if (i == patharray[20] - 1)
            {
                if (node->ne->bounds != NULL && quadtree_node_isempty(node->ne))
                {
                    double xcord = (node->ne->bounds->nw->x + node->ne->bounds->se->x) / 2;
                    double ycord = (node->ne->bounds->nw->y + node->ne->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->ne))
                {
                    neighbourset(1, filename, node->ne->point->x, node->ne->point->y);
                    printf("(%lf,%lf) ", node->ne->point->x, node->ne->point->y);
                }

                if (node->se->bounds != NULL && quadtree_node_isempty(node->se))
                {
                    double xcord = (node->se->bounds->nw->x + node->se->bounds->se->x) / 2;
                    double ycord = (node->se->bounds->nw->y + node->se->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->se))
                {
                    neighbourset(1, filename, node->se->point->x, node->se->point->y);
                    printf("(%lf,%lf) ", node->se->point->x, node->se->point->y);
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
        for (i = ancestor_pos; i <= patharray[20] - 1; i++)
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

            if (node->bounds != NULL && quadtree_node_isempty(node))
            {
                double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
                double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
                neighbourset(1, filename, xcord, ycord);
                printf("(%lf,%lf) ", xcord, ycord);
                break;
            }
            else if (quadtree_node_isleaf(node))
            {
                neighbourset(1, filename, node->point->x, node->point->y);
                printf("(%lf,%lf) ", node->point->x, node->point->y);
                break;
            }
            else if (i == patharray[20] - 1)
            {
                if (node->se->bounds != NULL && quadtree_node_isempty(node->se))
                {
                    double xcord = (node->se->bounds->nw->x + node->se->bounds->se->x) / 2;
                    double ycord = (node->se->bounds->nw->y + node->se->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->se))
                {
                    neighbourset(1, filename, node->se->point->x, node->se->point->y);
                    printf("(%lf,%lf) ", node->se->point->x, node->se->point->y);
                }

                if (node->sw->bounds != NULL && quadtree_node_isempty(node->sw))
                {
                    double xcord = (node->sw->bounds->nw->x + node->sw->bounds->se->x) / 2;
                    double ycord = (node->sw->bounds->nw->y + node->sw->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->sw))
                {
                    neighbourset(1, filename, node->sw->point->x, node->sw->point->y);
                    printf("(%lf,%lf) ", node->sw->point->x, node->sw->point->y);
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
        for (i = ancestor_pos; i <= patharray[20] - 1; i++)
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

            if (node->bounds != NULL && quadtree_node_isempty(node))
            {
                double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
                double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
                neighbourset(1, filename, xcord, ycord);
                printf("(%lf,%lf) ", xcord, ycord);
                break;
            }
            else if (quadtree_node_isleaf(node))
            {
                neighbourset(1, filename, node->point->x, node->point->y);
                printf("(%lf,%lf) ", node->point->x, node->point->y);
                break;
            }
            else if (i == patharray[20] - 1)
            {

                if (node->nw->bounds != NULL && quadtree_node_isempty(node->nw))
                {
                    double xcord = (node->nw->bounds->nw->x + node->nw->bounds->se->x) / 2;
                    double ycord = (node->nw->bounds->nw->y + node->nw->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->nw))
                {
                    neighbourset(1, filename, node->nw->point->x, node->nw->point->y);
                    printf("(%lf,%lf) ", node->nw->point->x, node->nw->point->y);
                }

                if (node->ne->bounds != NULL && quadtree_node_isempty(node->ne))
                {
                    double xcord = (node->ne->bounds->nw->x + node->ne->bounds->se->x) / 2;
                    double ycord = (node->ne->bounds->nw->y + node->ne->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    printf("(%lf,%lf) ", xcord, ycord);
                }
                else if (quadtree_node_isleaf(node->ne))
                {
                    neighbourset(1, filename, node->ne->point->x, node->ne->point->y);
                    printf("(%lf,%lf) ", node->ne->point->x, node->ne->point->y);
                }
                break;
            }
        }
    }
}
