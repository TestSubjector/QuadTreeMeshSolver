#include "quadtree.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

quadtree_t *tree; // The main tree structure for all our needs

coords_t *coords_list;  // Stores all the input points
coords_t *adapted_list; // Stores all the adapted points

int leaf_iter = 0;
int line_count = 0;
int adapted_line_count = 0;
int height_of_tree = 0;

void main_tree(int initial_coord_length, coords_t *coords_list, coords_t *adapted_list, quadtree_node_t *leaf_array)
{
    tree = quadtree_new(-10, -10, 10, 10);
    if (tree == NULL)
    {
        printf("\n ERROR : Memory allocation to the main quad_tree was unsuccessful");
        exit(0);
    }

    int i = 0; // The iteration variable for this function
    int j = 0;

    for (i = 0; i < initial_coord_length; i++) // Inserting points into the tree one-by-one
    {
        int success = quadtree_insert(tree, coords_list[i].x, coords_list[i].y);
        if (success == 0) // Out of bounds
        {
            printf("\n Warning: On line %d points %lf & %lf are out of bounds or were not created", i + 1, coords_list[i].x, coords_list[i].y);
        }
    }

    if(second_poly != 0)
    {
        printf("\nStatus: Please note that it is being assumed that the input file has multiple geometries.");
    }

    quadtree_leafnodes(tree->root, leaf_array);

    for (i = 0; i < leaf_iter; i++)
    {
        find_neighbours(tree, common_treeroute(tree->root, &leaf_array[i]), leaf_array);
        if (i == 400)
        {
            leaf_iter -= 400;
            for (int j = 0; j < leaf_iter; j++)
            {
                leaf_array[j] = leaf_array[j + 400];
            }
            i -= 400;
        }
    }
    height_of_tree = maxDepth(tree->root);

    // quadtree_valleywalk(tree->root, descent_valley, ascent);

    // free(leaf_array);
    // leaf_array = malloc(sizeof(quadtree_node_t) * MAX);
    // leaf_iter = 0;
    // quadtree_leafnodes(tree->root, leaf_array);
    // for (i = 0; i < leaf_iter; i++)
    // {
    //     find_neighbours(tree, common_treeroute(tree->root, &leaf_array[i]), leaf_array);
    //     if (i == 400)
    //     {
    //         leaf_iter -= 400;
    //         for (int j = 0; j < leaf_iter; j++)
    //         {
    //             leaf_array[j] = leaf_array[j + 400];
    //         }
    //         i -= 400;
    //     }
    // }

    // quadtree_refinementwalk(tree->root, descent_refinement, ascent);
    // quadtree_refinementwalk(tree->root, descent_refinement, ascent);
    quadtree_walk(tree->root, descent, ascent);
    printf("\n Max Depth of tree is %d", maxDepth(tree->root));

    quadtree_neighbourset(tree->root);

    // To get number of neighbours of last point
    neighbouroutput(1, "neighbour.txt", 1000, 1000);

    // Adaptation section
    if(adapted_line_count != 0)
    {
         quadtree_node_t *refined_node = NULL;
        for(j= 0; j < adapted_line_count; j++)
        {
            if(adapted_list[j].x == 1000 && adapted_list[j].y == 1000)
            {
                printf("\n Freedom");
                free(leaf_array);
                leaf_array = malloc(sizeof(quadtree_node_t) * MAX);
                leaf_iter = 0;
                quadtree_leafnodes(tree->root, leaf_array);
                // printf("\n Leaf iter is %d", leaf_iter);
                for (i = 0; i < leaf_iter; i++)
                {
                    find_neighbours(tree, common_treeroute(tree->root, &leaf_array[i]), leaf_array);
                    if (i == 400)
                    {
                        leaf_iter -= 400;
                        for (int j = 0; j < leaf_iter; j++)
                        {
                            leaf_array[j] = leaf_array[j + 400];
                        }
                        i -= 400;
                    }
                }
                continue;
            }
            refined_node = quadtree_search(adapted_list[j].x, adapted_list[j].y);
            // printf("\n %lf, %lf", adapted_list[j].x, adapted_list[j].y);
            if(refined_node == NULL)
            {
                printf("\n Warning - Point to be adapted not found");
                // printf("\n %.17g, %.17g", adapted_list[j].x, adapted_list[j].y);
                continue;
            }
            else
            {
                // printf("\n %d", j);
                split_node_newpoints(tree->root, refined_node);
            }
        }
        newoutputfile = 1;  // Clean file and write new generated files
        newneighboursetfile = 1; // Write the fresh-er version of neighbours
        serial_number = 1;
        quadtree_walk(tree->root, descent, ascent);
        quadtree_neighbourset(tree->root);
        // To get number of neighbours of last point
        neighbouroutput(1, "neighbour.txt", 1000, 1000);
    }
    
    free(leaf_array);
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
    char *filename = argv[1];                      // This will be the file from which the input is taken
    line_count = fileinput(coords_list, filename); // Receives total number of input points

    adapted_list = malloc(sizeof(coords_t) * MAX);
    if (adapted_list == NULL)
    {
        printf("\n ERROR : Memory allocation to adapted_list was unsuccessful");
        exit(0);
    }
    char *adapted_filename = argv[2];
    adapted_line_count = adaptation_fileinput(adapted_list, adapted_filename);
    // printf("\n %d", adapted_line_count);

    main_tree(line_count, coords_list, adapted_list, leaf_array);

    printf("\nQuadtree_t: %ld\n", sizeof(quadtree_t));
    printf("\n");
    free(coords_list);
    free(adapted_list);
    return 0;
}
