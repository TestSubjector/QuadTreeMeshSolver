#include "quadtree.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

quadtree_t *tree; // The main tree structure for all our needs

coords_t *coords_list; // Stores all the input points
coords_t *adapted_list;

int leaf_iter = 0;
int line_count = 0;
int adapt_flag = 0;

void main_tree(int initial_coord_length, coords_t *coords_list, quadtree_node_t *leaf_array)
{
    tree = quadtree_new(-5, -5, 5, 5);
    if (tree == NULL)
    {
        printf("\n ERROR : Memory allocation to the main quad_tree was unsuccessful");
        exit(0);
    }

    int i = 0; // The iteration variable for this function

    for (i = 0; i < initial_coord_length; i++) // Inserting points into the tree one-by-one
    {
        int success = quadtree_insert(tree, coords_list[i].x, coords_list[i].y);
        if (success == 0) // Out of bounds
        {
            printf("\n Warning: On line %d points %lf & %lf are out of bounds or were not created", i + 1, coords_list[i].x, coords_list[i].y);
        }
    }

    // Adaptation section
    /*
    if (adapt_flag != 0)
    {
        for (int adapt_iter = 0; adapt_iter < adapt_flag; adapt_iter++)
        {
            if (adapt(tree, tree->root, adapted_list[adapt_iter].x, adapted_list[adapt_iter].y) == 0)
            {
                printf("\n ERROR : Point %lf %lf was not adapted successfully", adapted_list[adapt_iter].x, adapted_list[adapt_iter].y);
            }
        }
    }
    */

    quadtree_leafnodes(tree->root, leaf_array);

    for (i = 0; i < leaf_iter; i++)
    {
        // printf("\n Problems with address %p\n", &leaf_array[i]);
        find_neighbours(tree, common_ancestor(tree->root, &leaf_array[i]), leaf_array);
        if (i == 400)
        {
            leaf_iter -= 400;
            for (int j = 0; j <= 400; j++)
            {
                leaf_array[j] = leaf_array[j + 400];
            }
            i -= 400;
        }
    }
    quadtree_walk(tree->root, descent, ascent);
    quadtree_neighbourset(tree->root);
    // To get number of neighbours of last point
    neighbouroutput(1, "neighbour.txt", 1000, 1000);
    quadtree_free(tree);
}

int main(int argc, char *argv[])
{
    coords_list = malloc(sizeof(coords_t) * MAX);
    if (coords_list == NULL)
    {
        printf("\n ERROR : Memory allocation to coords_list was unsuccessful");
        exit(0);
    }

    quadtree_node_t *leaf_array = malloc(sizeof(quadtree_node_t) * MAX); // To store all the leaves (input and generated points)
    if (leaf_array == NULL)
    {
        printf("\n ERROR : Memory allocation to leaf_array was unsuccessful");
        exit(0);
    }
    char *filename = argv[1];                                            // This will be the file from which the input is taken
    line_count = fileinput(coords_list, filename);                       // Receives total number of input points

    printf("\nquadtree_t: %ld\n", sizeof(quadtree_t));

    main_tree(line_count, coords_list, leaf_array);
    printf("\n");

    /*
    // Max number of manual adaptations is set to 30
    adapted_list = malloc(sizeof(coords_t) * 30);
    char check;
   
    printf("\n Please press 'y' if you want to adapt points, else press anything: ");
    check = getchar();
    do
    {
        if (check != 'y')
        {
            printf("\n Thank you, terminating program");
            break;
        }
        else
        {
            printf("\n Enter x coordinte of the point to be adapted: ");
            scanf("%lf", &adapted_list[adapt_flag].x);
            printf("\n Enter y coordinte of the point to be adapted: ");
            scanf("%lf", &adapted_list[adapt_flag].y);
            adapt_flag++;
        }
        printf("\n Please press 'y' if you want to adapt points, else press anything: ");
        scanf(" %c", &check);
    } while (check == 'y');

    coords_list = realloc(coords_list, sizeof(coords_t) * MAX);
    leaf_array = realloc(sizeof(quadtree_node_t) * MAX)

    neighbouroutput(0, "neighbour.txt", 1000, 1000);
    main_tree(line_count, coords_list, leaf_array);
    */

    return 0;
}
