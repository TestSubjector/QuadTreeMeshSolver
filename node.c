#include "quadtree.h"
#include <stdio.h>

int patharray[21];
int path_iter = 0;

// Boolean is integer in C
int quadtree_node_ispointer(quadtree_node_t *node)
{
    return node->nw != NULL
    && node->ne != NULL
    && node->sw != NULL
    && node->se != NULL
    && !quadtree_node_isleaf(node);
}

// Check if quadrant is empty
int quadtree_node_isempty(quadtree_node_t *node)
{
    return node->nw == NULL
    && node->ne == NULL
    && node->sw == NULL
    && node->se == NULL
    && !quadtree_node_isleaf(node);
}

int quadtree_node_isleaf(quadtree_node_t *node)
{
    return node->point != NULL;
}

void quadtree_node_reset(quadtree_node_t* node)
{
    quadtree_point_free(node->point);
}


// Initialize
quadtree_node_t* quadtree_node_new()
{
    quadtree_node_t *node;
    if(!(node = malloc(sizeof(*node))))
        return NULL;
    node->ne     = NULL;
    node->nw     = NULL;
    node->se     = NULL;
    node->sw     = NULL;
    node->point  = NULL;
    node->bounds = NULL;
    return node;
}

quadtree_node_t* quadtree_node_with_bounds(double minx, double miny, double maxx, double maxy)
{
    quadtree_node_t* node;
    if(!(node = quadtree_node_new()))
    {
        return NULL;
    }
    if(!(node->bounds = quadtree_bounds_new()))
    {
        return NULL;
    }
    quadtree_bounds_extend(node->bounds, maxx, maxy);
    quadtree_bounds_extend(node->bounds, minx, miny);
    return node;
}

void quadtree_node_free(quadtree_node_t* node)
{
    if(node->nw != NULL) quadtree_node_free(node->nw);
    if(node->ne != NULL) quadtree_node_free(node->ne);
    if(node->sw != NULL) quadtree_node_free(node->sw);
    if(node->se != NULL) quadtree_node_free(node->se);

    quadtree_bounds_free(node->bounds);
    quadtree_node_reset(node);
    free(node);
}

void quadtree_leafnodes(quadtree_node_t *root, quadtree_node_t *leaf_array)
{
    // Get all leaf nodes
    quadtree_leafwalk(root, descent_leaf, ascent, leaf_array);
    // Print all the leaf nodes at this point
    int i = 0;
    for(i = 0; i < leaf_iter; i++)
    {
        quadtree_node_t *node = &leaf_array[i];
        if (node->bounds != NULL && quadtree_node_isempty(node)) {
            printf("\n %f %f", (node->bounds->nw->x + node->bounds->se->x) / 2,
                   (node->bounds->nw->y + node->bounds->se->y) / 2);
        }
        else if(quadtree_node_isleaf(node))
        {
            printf("\n%f %f", node->point->x, node->point->y);
        }
    }
}

static int node_contains_patharray(quadtree_node_t *outer, double x, double y) {
  return outer->bounds != NULL && outer->bounds->nw->x <= x &&
         outer->bounds->nw->y >= y && outer->bounds->se->x >= x &&
         outer->bounds->se->y <= y;
}


static quadtree_point_t *find_patharray(quadtree_node_t *node, double x, double y) {
    if (!node) {
        printf("\nSomething went wrong while finding neighbours\n");
    return NULL;
    }
    else if (quadtree_node_ispointer(node)) {
        quadtree_point_t test;
        test.x = x;
        test.y = y;
        return find_patharray(get_quadrant_patharray(node, x, y), x , y);
    }
    return NULL;
}

// Stores the descent path from root node to node whose neighbours we need to find
static quadtree_node_t *get_quadrant_patharray(quadtree_node_t *root,
                                      double x, double y) {
  if (node_contains_patharray(root->nw, x, y)) {
    // printf("1");
    patharray[path_iter] = 1;
    path_iter++;
    return root->nw;
  }
  if (node_contains_patharray(root->ne, x , y)) {
    // printf("2");
    patharray[path_iter] = 2;
    path_iter++;
    return root->ne;
  }
  if (node_contains_patharray(root->sw, x , y)) {
    // printf("3");
    patharray[path_iter] = 3;
    path_iter++;
    return root->sw;
  }
  if (node_contains_patharray(root->se, x, y)) {
    // printf("4");
    patharray[path_iter] = 4;
    path_iter++;
    return root->se;
  }
  return NULL;
}

// This does not find common ancestor, just the tree path from root to node
int* common_ancestor(quadtree_node_t *root, quadtree_node_t *node)
{
    int i = 0;
    for(i=0; i<21; i++)
    {
        patharray[i] = 0;
    }
    // For centroid leafs
    if(node->point == NULL)
    {
        //printf("\nFound centroid node\n");
        path_iter = 0;
        find_patharray(root, (node->bounds->nw->x + node->bounds->se->x) / 2, (node->bounds->nw->y + node->bounds->se->y) / 2);
        // printf("\n For point %lf, %lf ", (node->bounds->nw->x + node->bounds->se->x) / 2, (node->bounds->nw->y + node->bounds->se->y) / 2);
    }
    else if (quadtree_node_isleaf(node))
    {
        // printf("\n Found boundary point \n");
        path_iter = 0;
        find_patharray(root, node->point->x, node->point->y);
        // printf("\n For point %lf, %lf ", node->point->x, node->point->y);
    }
    patharray[20] = path_iter;
    return patharray;
}

void balance_neighbour(quadtree_t *tree, int patharray[21], int neighbour_pos, int direction, quadtree_node_t *leaf_array)
{

    // Direction
    // East - 1 , West - 2, North -3, South - 4

    quadtree_node_t *root = tree->root;
    int path_step = 0;
    int i = 0;
    for(i = 0; i< neighbour_pos; i++)
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
    if(neighbour_pos >= patharray[20] - 1)
    {
        // printf("\n No need for neighbour adjustment");
        return;
    }

    // Eastern Neighbour
    if(direction == 1)
    {
        int did_node_split = 0;
        // printf("\n Finding Eastern Neighbour");
        int i = neighbour_pos;
        for(i = neighbour_pos; i <= patharray[20] - 2; i++)
        {
            quadtree_node_t *temp1;
            path_step = patharray[i];
            if((root->bounds != NULL && (quadtree_node_isempty(root)))|| (quadtree_node_isleaf(root)))
            {
                // Analysis - Should give only a few outputs because only some nodes will have
                // neighbour not at the same level or one level higher
                // printf("\n Neighbour split: East");
                split_node_newpoints(tree, root);
                did_node_split = 1;
                temp1 = root;
                if (path_step == 1)
                {
                  root = root->ne;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp1->ne);
                    leaf_iter++;
                }

                if (path_step == 2)
                {
                  root = root->nw;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp1->nw);
                    leaf_iter++;
                }

                if (path_step == 3)
                {
                  root = root->se;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp1->se);
                    leaf_iter++;
                }

                if (path_step == 4)
                {
                  root = root->sw;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp1->sw);
                    leaf_iter++;
                }
                did_node_split = 0;
                continue;
            }

            if (path_step == 1 )
            {
              root = root->ne;
            }

            if (path_step == 2)
            {
              root = root->nw;
            }

            if (path_step == 3)
            {
              root = root->se;
            }

            if (path_step == 4)
            {
              root = root->sw;
            }
        }
    }

    // Western Neighbour
    if(direction == 2)
    {
        int did_node_split = 0;
        // printf("\n Finding Western Neighbour");
        int i = neighbour_pos;
        for(i = neighbour_pos; i <= patharray[20] - 2; i++)
        {
            quadtree_node_t *temp2;
            path_step = patharray[i];
            if((root->bounds != NULL && quadtree_node_isempty(root))|| (quadtree_node_isleaf(root)))
            {
                // Analysis - Should give only a few outputs because only some nodes will have
                // neighbour not at the same level or one level higher
                // printf("\n Neighbour split : West");
                split_node_newpoints(tree, root);
                did_node_split = 1;
                temp2 = root;

                if (path_step == 1)
                {
                  root = root->ne;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : West");
                    leaf_array[leaf_iter] = *(temp2->ne);
                    leaf_iter++;
                }

                if (path_step == 2)
                {
                  root = root->nw;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : West");
                    leaf_array[leaf_iter] = *(temp2->nw);
                    leaf_iter++;
                }

                if (path_step == 3)
                {
                  root = root->se;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : West");
                    leaf_array[leaf_iter] = *(temp2->se);
                    leaf_iter++;
                }

                if (path_step == 4)
                {
                  root = root->sw;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node: West");
                    leaf_array[leaf_iter] = *(temp2->sw);
                    leaf_iter++;
                }
                did_node_split = 0;
                continue;
            }
            if (path_step == 1)
            {
              root = root->ne;
            }

            if (path_step == 2)
            {
              root = root->nw;
            }

            if (path_step == 3)
            {
              root = root->se;
            }

            if (path_step == 4)
            {
              root = root->sw;
            }
        }
    }

    // Northern Neighbour
    if(direction == 3)
    {
        int did_node_split = 0;
        // printf("\n Finding Northern Neighbour");
        for(int i = neighbour_pos; i <= patharray[20] - 2; i++)
        {
            quadtree_node_t *temp3;
            path_step = patharray[i];
            if((root->bounds != NULL && quadtree_node_isempty(root))|| (quadtree_node_isleaf(root)))
            {
                // Analysis - Should give only a few outputs because only some nodes will have
                // neighbour not at the same level or one level higher
                // printf("\n Neighbour split : North");
                split_node_newpoints(tree, root);
                did_node_split = 1;
                temp3 = root;

                if (path_step == 1)
                {
                  root = root->sw;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : North");
                    leaf_array[leaf_iter] = *(temp3->sw);
                    leaf_iter++;
                }

                if (path_step == 2)
                {
                  root = root->se;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : North");
                    leaf_array[leaf_iter] = *(temp3->se);
                    leaf_iter++;
                }

                if (path_step == 3)
                {
                  root = root->nw;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node: North");
                    leaf_array[leaf_iter] = *(temp3->nw);
                    leaf_iter++;
                }

                if (path_step == 4)
                {
                  root = root->ne;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : North");
                    leaf_array[leaf_iter] = *(temp3->ne);
                    leaf_iter++;
                }
                did_node_split = 0;
                continue;
            }
            if (path_step == 1)
            {
              root = root->sw;
            }

            if (path_step == 2)
            {
              root = root->se;
            }

            if (path_step == 3)
            {
              root = root->nw;
            }

            if (path_step == 4)
            {
              root = root->ne;
            }
        }
    }

    // Southern Neighbour
    if(direction == 4)
    {
        int did_node_split = 0;
        // printf("\n Finding Southern Neighbour");
        int i = neighbour_pos;
        for(i = neighbour_pos; i <= patharray[20] - 2; i++)
        {
            quadtree_node_t *temp4;
            path_step = patharray[i];
            if((root->bounds != NULL && quadtree_node_isempty(root))|| (quadtree_node_isleaf(root)))
            {
                // Analysis - Should give only a few outputs because only some nodes will have
                // neighbour not at the same level or one level higher
                // printf("\n Neighbour split : South");
                // printf("\n In the if case %lf, %lf ", (root->bounds->nw->x + root->bounds->se->x) / 2, (root->bounds->nw->y + root->bounds->se->y) / 2);
                split_node_newpoints(tree, root);
                did_node_split = 1;
                temp4 = root;
                if (path_step == 1)
                {
                  root = root->sw;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp4->nw);
                    leaf_iter++;
                }

                if (path_step == 2)
                {
                  root = root->se;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp4->se);
                    leaf_iter++;
                }

                if (path_step == 3)
                {
                  root = root->nw;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp4->nw);
                    leaf_iter++;
                }

                if (path_step == 4)
                {
                  root = root->ne;
                }
                else if(did_node_split == 1)
                {
                    // printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp4->ne);
                    leaf_iter++;
                }
                did_node_split = 0;
                continue;
            }

            if (path_step == 1)
            {
              root = root->sw;
            }

            if (path_step == 2)
            {
              root = root->se;
            }

            if (path_step == 3)
            {
              root = root->nw;
            }

            if (path_step == 4)
            {
              root = root->ne;
            }
        }
    }
}

void find_neighbours(quadtree_t *tree, int patharray[21], quadtree_node_t *leaf_array)
{
    // printf("\n Start");

    int path_size = patharray[20];
    int i = 0;
    int pathstep = -1;
    int direction = 0;
    int neighbour_pos = -1;

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
    for(i = path_size - 1; i>= 0; i--)
    {
        pathstep = patharray[i];
        if(pathstep == 1)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Eastern neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 2)
        {
            continue;
        }
        else if(pathstep == 3)
        {
            // printf("\n Found common ancestor for Eastern neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 4)
        {
            continue;
        }
        else if(pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted pathaarray");
            // exit(1);
        }
    }
    if(neighbour_pos != -1)
    {
        // Neighbour exists
        // printf("\n Found common ancestor for Eastern neighbour");
        balance_neighbour(tree, patharray, neighbour_pos, direction, leaf_array);
        neighbour_pos = -1;
    }
    else
    {
        // printf("\n Eastern Neighbour does not exist");
    }

    // For Western Neighbour
    direction = 2;
    for(i = path_size - 1; i >= 0; i--)
    {
        pathstep = patharray[i];
        if(pathstep == 1)
        {
            continue;
        }
        else if(pathstep == 2)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Western neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 3)
        {
            continue;
        }
        else if(pathstep == 4)
        {
            // printf("\n Found common ancestor for Western neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted pathaarray");
            // exit(1);
        }
    }
    if(neighbour_pos != -1)
    {
        // Neighbour exists
        balance_neighbour(tree, patharray, neighbour_pos, direction, leaf_array);
        neighbour_pos = -1;
    }
    else
    {
        // printf("\n Western Neighbour does not exist");
    }

    // For Northern Neighbour
    direction = 3;
    for(i = path_size - 1; i>= 0; i--)
    {
        pathstep = patharray[i];
        if(pathstep == 1)
        {
            continue;
        }
        else if(pathstep == 2)
        {
            continue;
        }
        else if(pathstep == 3)
        {
            // printf("\n Found common ancestor for Northern neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 4)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Northern neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted pathaarray");
            // exit(1);
        }
    }
    if(neighbour_pos != -1)
    {
        // Neighbour exists
        balance_neighbour(tree, patharray, neighbour_pos, direction, leaf_array);
        neighbour_pos = -1;
    }
    else
    {
        // printf("\n Northern Neighbour does not exist");
    }

    // For Southern Neighbour
    direction = 4;
    for(i = path_size - 1; i>= 0; i--)
    {
        pathstep = patharray[i];
        if(pathstep == 1)
        {
            // printf("\n Found common ancestor for Southern neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 2)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Southern neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 3)
        {
            continue;
        }
        else if(pathstep == 4)
        {
            continue;
        }
        else if(pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted pathaarray");
            // exit(1);
        }
    }
    if(neighbour_pos != -1)
    {
        // Neighbour exists
        balance_neighbour(tree, patharray, neighbour_pos, direction, leaf_array);
        neighbour_pos = -1;
    }
    else
    {
        // printf("\n Southern Neighbour does not exist");
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

    if(quadtree_node_isleaf(node))
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
    int neighbour_pos = -1;

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
    for(i = path_size - 1; i>= 0; i--)
    {
        pathstep = patharray[i];
        if(pathstep == 1)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Eastern neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 2)
        {
            continue;
        }
        else if(pathstep == 3)
        {
            // printf("\n Found common ancestor for Eastern neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 4)
        {
            continue;
        }
        else if(pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted pathaarray");
            // exit(1);
        }
    }
    if(neighbour_pos != -1)
    {
        // Neighbour exists
        // printf("\n Found common ancestor for Eastern neighbour");
        balance_neighbourset(patharray, neighbour_pos, direction);
        neighbour_pos = -1;
    }
    else
    {
        // printf("\n Eastern Neighbour does not exist");
    }

    // For Western Neighbour
    direction = 2;
    for(i = path_size - 1; i >= 0; i--)
    {
        pathstep = patharray[i];
        if(pathstep == 1)
        {
            continue;
        }
        else if(pathstep == 2)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Western neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 3)
        {
            continue;
        }
        else if(pathstep == 4)
        {
            // printf("\n Found common ancestor for Western neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted pathaarray");
            // exit(1);
        }
    }
    if(neighbour_pos != -1)
    {
        // Neighbour exists
        balance_neighbourset(patharray, neighbour_pos, direction);
        neighbour_pos = -1;
    }
    else
    {
        // printf("\n Western Neighbour does not exist");
    }

    // For Northern Neighbour
    direction = 3;
    for(i = path_size - 1; i>= 0; i--)
    {
        pathstep = patharray[i];
        if(pathstep == 1)
        {
            continue;
        }
        else if(pathstep == 2)
        {
            continue;
        }
        else if(pathstep == 3)
        {
            // printf("\n Found common ancestor for Northern neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 4)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Northern neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted pathaarray");
            // exit(1);
        }
    }
    if(neighbour_pos != -1)
    {
        // Neighbour exists
        balance_neighbourset(patharray, neighbour_pos, direction);
        neighbour_pos = -1;
    }
    else
    {
        // printf("\n Northern Neighbour does not exist");
    }

    // For Southern Neighbour
    direction = 4;
    for(i = path_size - 1; i>= 0; i--)
    {
        pathstep = patharray[i];
        if(pathstep == 1)
        {
            // printf("\n Found common ancestor for Southern neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 2)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Southern neighbour");
            neighbour_pos = i;
            break;
        }
        else if(pathstep == 3)
        {
            continue;
        }
        else if(pathstep == 4)
        {
            continue;
        }
        else if(pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted pathaarray");
            // exit(1);
        }
    }
    if(neighbour_pos != -1)
    {
        // Neighbour exists
        balance_neighbourset(patharray, neighbour_pos, direction);
        neighbour_pos = -1;
    }
    else
    {
        // printf("\n Southern Neighbour does not exist");
    }
}

void balance_neighbourset(int patharray[21], int neighbour_pos, int direction)
{

    // Direction
    // East - 1 , West - 2, North -3, South - 4

    quadtree_node_t *node = tree->root;
    int path_step = 0;
    int i = 0;
    char *filename = "neighbour.txt";

    // printf("\n The patharray is %d and neighbour pos is %d", patharray[20], neighbour_pos);
    for(i = 0; i< neighbour_pos; i++)
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

    if(!(node))
    {
        printf("\n ERROR : Ghost of the past, tree traversal went awry");
    }

    // Eastern Neighbour
    if(direction == 1)
    {
        // printf("\n Finding Eastern Neighbour");
        int i = neighbour_pos;
        // printf("\n The neighbour pos is %d", i);
        for(i = neighbour_pos; i <= patharray[20] - 1; i++)
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
            else if(quadtree_node_isleaf(node))
            {
                neighbourset(1, filename, node->point->x, node->point->y);
                printf("(%lf,%lf) ", node->point->x, node->point->y);
                break;
            }
            // The neighbours are two
            else if(i == patharray[20] - 1)
            {
                if (node->nw->bounds != NULL && quadtree_node_isempty(node->nw))
                {
                    double xcord = (node->nw->bounds->nw->x + node->nw->bounds->se->x) / 2;
                    double ycord = (node->nw->bounds->nw->y + node->nw->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    printf("(%lf,%lf) ", xcord, ycord);
                }
                else if(quadtree_node_isleaf(node->nw))
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
                else if(quadtree_node_isleaf(node->sw))
                {
                    neighbourset(1, filename, node->sw->point->x, node->sw->point->y);
                    printf("(%lf,%lf) ", node->sw->point->x, node->sw->point->y);
                }
                break;
            }
        }
    }

    // Western Neighbour
    if(direction == 2)
    {
        // printf("\n Finding Western Neighbour");
        int i = neighbour_pos;
        for(i = neighbour_pos; i <= patharray[20] - 1; i++)
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

            if(node->bounds != NULL && quadtree_node_isempty(node))
            {
                double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
                double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
                neighbourset(1, filename, xcord, ycord);
                printf("(%lf,%lf) ", xcord, ycord);
                break;
            }
            else if(quadtree_node_isleaf(node))
            {
                neighbourset(1, filename, node->point->x, node->point->y);
                printf("(%lf,%lf) ", node->point->x, node->point->y);
                break;
            }
            else if(i == patharray[20] - 1)
            {
                if (node->ne->bounds != NULL && quadtree_node_isempty(node->ne))
                {
                    double xcord = (node->ne->bounds->nw->x + node->ne->bounds->se->x) / 2;
                    double ycord = (node->ne->bounds->nw->y + node->ne->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    printf("(%lf,%lf) ", xcord, ycord);
                }
                else if(quadtree_node_isleaf(node->ne))
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
                else if(quadtree_node_isleaf(node->se))
                {
                    neighbourset(1, filename, node->se->point->x, node->se->point->y);
                    printf("(%lf,%lf) ", node->se->point->x, node->se->point->y);
                }
                break;
            }
        }
    }

    // Northern Neighbour
    if(direction == 3)
    {
        // printf("\n Finding Northern Neighbour");
        int i = neighbour_pos;
        for(i = neighbour_pos; i <= patharray[20] - 1; i++)
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

            if(node->bounds != NULL && quadtree_node_isempty(node))
            {
                double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
                double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
                neighbourset(1, filename, xcord, ycord);
                printf("(%lf,%lf) ", xcord, ycord);
                break;
            }
            else if(quadtree_node_isleaf(node))
            {
                neighbourset(1, filename, node->point->x, node->point->y);
                printf("(%lf,%lf) ", node->point->x, node->point->y);
                break;
            }
            else if(i == patharray[20] - 1)
            {
                if (node->se->bounds != NULL && quadtree_node_isempty(node->se))
                {
                    double xcord = (node->se->bounds->nw->x + node->se->bounds->se->x) / 2;
                    double ycord = (node->se->bounds->nw->y + node->se->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    printf("(%lf,%lf) ", xcord, ycord);
                }
                else if(quadtree_node_isleaf(node->se))
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
                else if(quadtree_node_isleaf(node->sw))
                {
                    neighbourset(1, filename, node->sw->point->x, node->sw->point->y);
                    printf("(%lf,%lf) ", node->sw->point->x, node->sw->point->y);
                }
                break;
            }
        }
    }

    // Southern Neighbour
    if(direction == 4)
    {
        // printf("\n Finding Southern Neighbour");
        int i = neighbour_pos;
        for(i = neighbour_pos; i <= patharray[20] - 1; i++)
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

            if(node->bounds != NULL && quadtree_node_isempty(node))
            {
                double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
                double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
                neighbourset(1, filename, xcord, ycord);
                printf("(%lf,%lf) ", xcord, ycord);
                break;
            }
            else if(quadtree_node_isleaf(node))
            {
                neighbourset(1, filename, node->point->x, node->point->y);
                printf("(%lf,%lf) ", node->point->x, node->point->y);
                break;
            }
            else if(i == patharray[20] - 1)
            {
                
                if (node->nw->bounds != NULL && quadtree_node_isempty(node->nw))
                {
                    double xcord = (node->nw->bounds->nw->x + node->nw->bounds->se->x) / 2;
                    double ycord = (node->nw->bounds->nw->y + node->nw->bounds->se->y) / 2;
                    neighbourset(1, filename, xcord, ycord);
                    printf("(%lf,%lf) ", xcord, ycord);
                }
                else if(quadtree_node_isleaf(node->nw))
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
                else if(quadtree_node_isleaf(node->ne))
                {
                    neighbourset(1, filename, node->ne->point->x, node->ne->point->y);
                    printf("(%lf,%lf) ", node->ne->point->x, node->ne->point->y);
                }
                break;
            }
        }
    }
}
