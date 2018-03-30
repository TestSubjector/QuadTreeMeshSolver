#include "quadtree.h"

void quadtree_neighbourset(quadtree_node_t *root)
{
    quadtree_neighbourwalk(root, descent_node, ascent);
}

