#include "quadtree.h"

void quadtree_neighbourset(quadtree_node_t *root)
{
    char *filename = "neighbour.txt";
    FILE *fp = NULL;
    fp = fopen(filename, "w");
    quadtree_neighbourwalk(tree->root, descent_node, ascent, fp);
    fclose(fp);
}
