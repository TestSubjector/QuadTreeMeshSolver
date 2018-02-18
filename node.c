#include "quadtree.h"
#include <stdio.h>


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
    quadtree_leafwalk(root, descent_leaf, ascent, leaf_array);
    for(int i = 0; i < leaf_iter; i++)
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
