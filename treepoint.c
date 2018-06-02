#include "quadtree.h"

// Initialiaze quadtree_point
quadtree_point_t *quadtree_point_new(double x, double y)
{
    quadtree_point_t *point;
    if (!(point = malloc(sizeof(*point))))
    {
        return NULL;
    }
    point->x = x;
    point->y = y;
    return point;
}

void quadtree_point_free(quadtree_point_t *point)
{
    free(point);
}

quadtree_node_t *reach_ancestor(quadtree_node_t *node, int patharray[41], int ancestor_pos)
{
    int path_step = 0;
    for (int i = 0; i < ancestor_pos; i++)
    {
        path_step = patharray[i];
        if (path_step == 1)
        {
            node = node->nw;
        }
        if (path_step == 2)
        {
            node = node->ne;
        }
        if (path_step == 3)
        {
            node = node->sw;
        }
        if (path_step == 4)
        {
            node = node->se;
        }
    }
    return node;
}

int east_ancestor(int patharray[41], int path_size)
{
    int ancestor_pos = -1;
    int pathstep;
    for (int i = path_size - 1; i >= 0; i--)
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
            printf("\n Some random value corrupted patharray");
            exit(2);
        }
    }
    return ancestor_pos;
}

int west_ancestor(int patharray[41], int path_size)
{
    int ancestor_pos = -1;
    int pathstep;
    for (int i = path_size - 1; i >= 0; i--)
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
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted patharray");
            exit(2);
        }
    }
    return ancestor_pos;    
}

int north_ancestor(int patharray[41], int path_size)
{
    int ancestor_pos = -1;
    int pathstep;
    for (int i = path_size - 1; i >= 0; i--)
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
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted patharray");
            exit(2);
        }
    }
    return ancestor_pos;    
}

int south_ancestor(int patharray[41], int path_size)
{
    int ancestor_pos = -1;
    int pathstep;
    for (int i = path_size - 1; i >= 0; i--)
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
    return ancestor_pos;    
}
