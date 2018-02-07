#include "quadtree.h"
#include <stdio.h>
#include <assert.h>

#define test(fn) \
    printf("\x1b[33m" # fn "\x1b[0m "); \
    test_##fn(); \
    puts("\x1b[1;32m ✓ \x1b[0m");

static void test_tree()
{
    quadtree_t *tree = quadtree_new(-10, -10, 10, 10);
    assert(tree->root->bounds->nw->x == -10.0);
    assert(tree->root->bounds->nw->y == 10.0);
    assert(tree->root->bounds->se->x == 10.0);
    assert(tree->root->bounds->se->y == -10.0);
    
    /*
         ------|x,y|
         --       --
         --       --
         |x,y|------
    */

    // Specifies that we cant ad points that are out of bound
    assert(quadtree_insert(tree, 0, 0) == 0);
    assert(quadtree_insert(tree, 110.0, 110.0) == 0);

    // Add a point in the rectangle, it becomes the root
    assert(quadtree_insert(tree, 8.0, 2.0) != 0);
    assert(tree->length == 1);
    assert(tree->root->point->x == 8.0);
    assert(tree->root->point->y == 2.0);

    // Add amother point, leading to branching
    assert(quadtree_insert(tree, 0.0, 1.0) == 0); /* failed insertion */
    assert(quadtree_insert(tree, 2.0, 3.0) == 1); /* normal insertion */
    assert(quadtree_insert(tree, 2.0, 3.0) == 2); /* replacement insertion */
    assert(tree->length == 2);
    assert(tree->root->point == NULL);

    // Another branching
    assert(quadtree_insert(tree, 3.0, 1.1) == 1);
    assert(tree->length == 3);
    // Search for point
    assert(quadtree_search(tree, 3.0, 1.1)->x == 3.0);

    // quadtree_walk(tree->root, ascent, descent);
    // printf("\nquadtree_t1: %ld\n", sizeof(*tree));
    
    quadtree_free(tree);
}


int main(int argc, const char *argv[])
{
    printf("\nquadtree_t: %ld\n", sizeof(quadtree_t));
    test(tree);   
    return 0;
}

