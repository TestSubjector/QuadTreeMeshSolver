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
        printf("\nSomething went wrong will finding neighbours\n");
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
    }
    else if (quadtree_node_isleaf(node)) 
    {
        // printf("\n Found boundary point \n");
        path_iter = 0;
        find_patharray(root, node->point->x, node->point->y);
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
    // Eastern Neighbour
    if(direction == 1)
    {
        int did_node_split = 0;
        // printf("\n Finding Eastern Neighbour");
        int i = neighbour_pos;
        for(i = neighbour_pos; i < patharray[20] - 2; i++)
        {
            quadtree_node_t *temp = NULL;
            path_step = patharray[i];
            if((root->bounds != NULL && quadtree_node_isempty(root))|| (quadtree_node_isleaf(root)))
            {
                // Analysis - Should give only a few outputs because only some nodes will have
                // neighbour not at the same level or one level higher
                printf("\n Neigbour split");
                split_node_(tree, root);
                did_node_split = 1;
                temp = root;

                if (path_step == 1) 
                {
                  root = root->ne;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp->ne);
                    leaf_iter++;
                }

                if (path_step == 2) 
                {
                  root = root->nw;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp->nw);
                    leaf_iter++;
                }

                if (path_step == 3) 
                {
                  root = root->se;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp->se);
                    leaf_iter++;
                }

                if (path_step == 4) 
                {
                  root = root->sw;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : East");
                    leaf_array[leaf_iter] = *(temp->sw);
                    leaf_iter++;
                }
                did_node_split = 0;
                break;
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

    if(direction == 2)
    {
        int did_node_split = 0;
        // printf("\n Finding Western Neighbour");
        int i = neighbour_pos;
        for(i = neighbour_pos; i < patharray[20] - 2; i++)
        {
            quadtree_node_t *temp = NULL;
            path_step = patharray[i];
            if((root->bounds != NULL && quadtree_node_isempty(root))|| (quadtree_node_isleaf(root)))
            {
                // Analysis - Should give only a few outputs because only some nodes will have
                // neighbour not at the same level or one level higher
                printf("\n Neigbour split");
                split_node_(tree, root);
                did_node_split = 1;
                temp = root;

                if (path_step == 1) 
                {
                  root = root->ne;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : West");
                    leaf_array[leaf_iter] = *(temp->ne);
                    leaf_iter++;
                }

                if (path_step == 2) 
                {
                  root = root->nw;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : West");
                    leaf_array[leaf_iter] = *(temp->nw);
                    leaf_iter++;
                }

                if (path_step == 3) 
                {
                  root = root->se;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : West");
                    leaf_array[leaf_iter] = *(temp->se);
                    leaf_iter++;
                }

                if (path_step == 4) 
                {
                  root = root->sw;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node: West");
                    leaf_array[leaf_iter] = *(temp->sw);
                    leaf_iter++;
                }
                did_node_split = 0;
                break;
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

    if(direction == 3)
    {
        int did_node_split = 0;
        printf("\n Finding Northern Neighbour");
        int i = neighbour_pos;
        for(i = neighbour_pos; i < patharray[20] - 2; i++)
        {
            quadtree_node_t *temp = NULL;
            path_step = patharray[i];
            if((root->bounds != NULL && quadtree_node_isempty(root))|| (quadtree_node_isleaf(root)))
            {
                // Analysis - Should give only a few outputs because only some nodes will have
                // neighbour not at the same level or one level higher
                printf("\n Neigbour split");
                split_node_(tree, root);
                did_node_split = 1;
                temp = root;

                if (path_step == 1) 
                {
                  root = root->sw;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : North");
                    leaf_array[leaf_iter] = *(temp->ne);
                    leaf_iter++;
                }

                if (path_step == 2) 
                {
                  root = root->se;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : North");
                    leaf_array[leaf_iter] = *(temp->nw);
                    leaf_iter++;
                }

                if (path_step == 3) 
                {
                  root = root->nw;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node: North");
                    leaf_array[leaf_iter] = *(temp->se);
                    leaf_iter++;
                }

                if (path_step == 4) 
                {
                  root = root->ne;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : North");
                    leaf_array[leaf_iter] = *(temp->sw);
                    leaf_iter++;
                }
                did_node_split = 0;
                break;
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

    if(direction == 4)
    {
        int did_node_split = 0;
        printf("\n Finding Southern Neighbour");
        int i = neighbour_pos;
        for(i = neighbour_pos; i < patharray[20] - 2; i++)
        {
            quadtree_node_t *temp = NULL;
            path_step = patharray[i];
            if((root->bounds != NULL && quadtree_node_isempty(root))|| (quadtree_node_isleaf(root)))
            {
                // Analysis - Should give only a few outputs because only some nodes will have
                // neighbour not at the same level or one level higher
                printf("\n Neigbour split");
                split_node_(tree, root);
                did_node_split = 1;
                temp = root;

                if (path_step == 1) 
                {
                  root = root->sw;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp->ne);
                    leaf_iter++;
                }

                if (path_step == 2) 
                {
                  root = root->se;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp->nw);
                    leaf_iter++;
                }

                if (path_step == 3) 
                {
                  root = root->nw;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp->se);
                    leaf_iter++;
                }

                if (path_step == 4) 
                {
                  root = root->ne;
                }
                else if(did_node_split == 1)
                {
                    printf("\n Created new neighbour node : South");
                    leaf_array[leaf_iter] = *(temp->sw);
                    leaf_iter++;
                }
                did_node_split = 0;
                break;
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
    
    int path_size = patharray[20];
    int i = 0;
    int pathstep = -1;
    int direction = 0;
    int neighbour_pos = -1;

    // NW - 1, NE - 2, SW - 3 , SE - 4

    // For eastern neighbour
    direction = 1;
    for(i = path_size - 1; i>= 0; i--)
    {
        pathstep = patharray[i];
        if(pathstep == 1)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Eastern neighbour");
            neighbour_pos = path_size-1 - i;
            break;
        }
        else if(pathstep == 2)
        {
            continue;
        }
        else if(pathstep == 3)
        {
            // printf("\n Found common ancestor for Eastern neighbour");
            neighbour_pos = path_size-1 - i;
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
            neighbour_pos = path_size-1 - i;
            break;
        }
        else if(pathstep == 3)
        {
            continue;
        }
        else if(pathstep == 4)
        {
            // printf("\n Found common ancestor for Western neighbour");
            neighbour_pos = path_size-1 - i;
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
            neighbour_pos = path_size-1 - i;
            break;
        }
        else if(pathstep == 4)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Northern neighbour");
            neighbour_pos = path_size-1 - i;
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
            neighbour_pos = path_size-1 - i;
            break;
        }
        else if(pathstep == 2)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Southern neighbour");
            neighbour_pos = path_size-1 - i;
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
