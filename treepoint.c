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