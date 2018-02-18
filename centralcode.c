#include "quadtree.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

int leaf_iter = 0;

void main_tree(int initial_coord_length, coords_t *coords_list, quadtree_node_t *leaf_array)
{
    quadtree_t *tree = quadtree_new(-5, -5, 5, 5);
    
    for(int i = 0; i < initial_coord_length; i++)
    {
        int success = quadtree_insert(tree, coords_list[i].x, coords_list[i].y);
        if(success == 0)
        {
            // Out of bounds
            printf("\n Problems with line %d, and points %lf & %lf", i+1, coords_list[i].x, coords_list[i].y);
        }
    }
    quadtree_walk(tree->root, descent, ascent);
    quadtree_leafwalk(tree->root, descent_leaf, ascent, leaf_array);
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
    quadtree_free(tree);
}

int main(int argc, char *argv[])
{
    coords_t *coords_list = malloc(sizeof(coords_t) * MAX);
    quadtree_node_t *leaf_array[MAX];
    printf("\nquadtree_t: %ld\n", sizeof(quadtree_t));
    char *filename = argv[1];
    int line_count;
    line_count = fileinput(coords_list, filename);
    main_tree(line_count, coords_list, leaf_array);
    printf("\n");
    return 0;
}

