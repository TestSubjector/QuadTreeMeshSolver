#include "quadtree.h"

// Boolean is integer in C
int quadtree_node_ispointer(quadtree_node_t *node)
{
    return node->nw != NULL
    && node->ne != NULL
    && node->sw != NULL
    && node->se != NULL
    && !quadtree_node_isleaf(node);
}

// Check if node is empty and not a leaf
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
