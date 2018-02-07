#include "quadtree.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#define MAX 1000

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
    assert(quadtree_insert(tree, -30, -30) == 0);
    assert(quadtree_insert(tree, 110.0, 110.0) == 0);

    // Add a point in the rectangle, it becomes the root
    assert(quadtree_insert(tree, 0, 0) != 0);
    assert(tree->length == 1);
    assert(tree->root->point->x == 0);
    assert(tree->root->point->y == 0);

    // Add amother point, leading to branching
    assert(quadtree_insert(tree, -30.0, -15.0) == 0); /* failed insertion */
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

void main_tree(int initial_coord_length, coords_t *coords_list)
{
    quadtree_t *tree = quadtree_new(-10, -10, 10, 10);
    
    for(int i = 0; i < initial_coord_length; i++)
    {
        int success = quadtree_insert(tree, coords_list[i].x, coords_list[i].y);
        if(success == 0)
        {
            // Out of bounds
            printf("\n Problems with line %d, and points %lf & %lf", i+1, coords_list[i].x, coords_list[i].y);
        }
    }
    printf("\nTree length is %d", tree->length); 
    quadtree_free(tree);
}

int main(int argc, char *argv[])
{
    printf("\nquadtree_t: %ld\n", sizeof(quadtree_t));

    char *filename = argv[1];

    char *line = NULL;
    size_t n = 0;

    FILE *coordFile = fopen(filename, "r");

    coords_t *coords_list = malloc(sizeof(coords_t) * MAX);
    if(coords_list == NULL)
    {
        printf("\n Coord structure has memory problems");
        exit(0);
    }
    int line_count = 0;

    while(getline(&line, &n, coordFile) != -1 && line_count < MAX)
    {
        int items = sscanf(line, "%lf %lf", &coords_list[line_count].x, &coords_list[line_count].y);
        if(items != 2)
        {
            printf("\n File sanity check failed");
            exit(1);
        }
        line_count++;
    }

    fclose(coordFile);
    main_tree(line_count, coords_list);
    // test(tree);
    return 0;
}

