#include "quadtree.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

quadtree_t *tree; // The main tree structure for all our needs

coords_t *coords_list;  // Stores all the input points
coords_t *adapted_list; // Stores all the adapted points
coords_t *shape_list;
coords_t *derefined_list; // Stores segments of points to be derefined
coords_t *non_leaf_blank_list; // Store non=leaf points to be blanked

int leaf_iter = 0;
int line_count = 0;
int adapted_line_count = 0;
int shape_line_count = 0;
int non_leaf_blank_line_count = 0;
int height_of_tree = 0;
int wallpoint_insert_flag = 0;
int hills_and_valleys_block_flag = 0;
int insertion_success;
int foreign_flag = 1;
int only_leaf_flag = 0;

void main_tree(int initial_coord_length, coords_t *coords_list, coords_t *adapted_list, coords_t *shape_list, quadtree_node_t *leaf_array)
{
    tree = quadtree_new(-20, -20, 20, 20);
    if (tree == NULL)
    {
        printf("\n ERROR : Memory allocation to the main quad_tree was unsuccessful");
        exit(0);
    }

    int i = 0; // The iteration variable for this function
    int j = 0;

    printf("\n Conducting Point Insertion");
    for (i = 0; i < initial_coord_length; i++) // Inserting points into the tree one-by-one
    {
        insertion_success = quadtree_insert(tree, coords_list[i].x, coords_list[i].y);
        if (insertion_success == 0) // Out of bounds
        {
            printf("\n Warning: On line %d points %lf & %lf are out of bounds or were not created", i + 1, coords_list[i].x, coords_list[i].y);
        }
    }

    if(second_poly != 0)
    {
        printf("\nStatus: Please note that it is being assumed that the input file has multiple geometries.");
    }

    if(foreign_flag != 0)
    {
        printf("\n Centroidifying | Foreign Flag !0 ");
        centroidify(tree->root, shape_list);
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

    if(hills_and_valleys_block_flag == 0)
    {
        printf("\n Hills & Valleys | Hill & Valleys Flag !0 ");
        quadtree_valleywalk(tree->root, descent_valley, ascent);
        quadtree_hillwalk(tree->root, descent_hill, ascent);
    }
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

    printf("\n Output.txt Creation | Currently Commented Out");
    // quadtree_walk(tree->root, descent, ascent);
    printf("\nMax Depth of tree is %d", maxDepth(tree->root));

    // Adaptation section
    if(adapted_line_count != 0)
    {
        printf("\n Inside the Adaptation Section");
        int derefine_counter = 0;
        quadtree_node_t *refined_node = NULL;

        for(j = 0; j < adapted_line_count; j++)
        {

            if(adapted_list[j].x == 4000 && adapted_list[j].y == 4000)
            {
                printf("\n Stop Hill & Valleys Usage");
                hills_and_valleys_block_flag = 1;
                // wallpoint_insert_flag == 3;
                continue;
            }

            if(adapted_list[j].x == 5000 && adapted_list[j].y == 5000)
            {
                printf("\n Restart Hill & Valleys Usage");
                hills_and_valleys_block_flag = 0;
                // wallpoint_insert_flag == 3;
                continue;
            }

            if(adapted_list[j].x == 1000 && adapted_list[j].y == 1000)
            {
                printf("\n Adapting Points");
                wallpoint_insert_flag = 0;
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

                if(hills_and_valleys_block_flag == 0)
                {
                    quadtree_valleywalk(tree->root, descent_valley, ascent);
                    quadtree_hillwalk(tree->root, descent_hill, ascent);
                }
                continue;
            }

            if(adapted_list[j].x == 2000 && adapted_list[j].y == 2000)
            {
                printf("\n Bsplining Points");
                wallpoint_insert_flag = 1;
                continue;
            }

            if(adapted_list[j].x == 3000 && adapted_list[j].y == 3000)
            {
                if(wallpoint_insert_flag == 2)
                {
                    derefine_fromlist(derefined_list, derefine_counter);
                    free(derefined_list);
                    printf("\n Derefining Points");
                }
                else
                {
                    derefine_counter = 0;
                    derefined_list = malloc(sizeof(coords_t) * (MAX));
                    wallpoint_insert_flag = 2;
                }
                continue;
            }

            if(wallpoint_insert_flag == 0)
            {
                refined_node = quadtree_search(adapted_list[j].x, adapted_list[j].y);
                // printf("\n %lf, %lf", adapted_list[j].x, adapted_list[j].y);
                if(refined_node == NULL)
                {
                    printf("\n Warning - Point to be adapted not found");
                    // printf("\n %.17g, %.17g", adapted_list[j].x, adapted_list[j].y);
                    continue;
                }
                else if(quadtree_node_ispointer(refined_node))
                {
                    // Point to be adapted is not a leaf
                    continue;
                }
                else
                {
                    // printf("\n %d", j);
                    split_node_newpoints(tree, refined_node);
                }
            }
            else if(wallpoint_insert_flag == 1)
            {
                insertion_success = quadtree_insert(tree, adapted_list[j].x, adapted_list[j].y);
                // printf("\n Successful ping");
                if (insertion_success == 0) // Out of bounds
                {
                    printf("\n Warning: On line %d points %lf & %lf are out of bounds or were not created during adaptation stage", i + 1, adapted_list[j].x, adapted_list[j].y);
                }
            }
            else if(wallpoint_insert_flag == 2)
            {
                derefined_list[derefine_counter].x = adapted_list[j].x;
                derefined_list[derefine_counter].y = adapted_list[j].y;
                derefine_counter++;
            }
        }

        printf("\nNeighbour file creation operations have started [In adaptation Branch].");

        newoutputfile = 1;  // Clean file and write new generated files
        newneighboursetfile = 1; // Write the fresh-er version of neighbours
        serial_number = 1;
        quadtree_walk(tree->root, descent, ascent);
        quadtree_neighbourset(tree->root);
        // To get number of neighbours of last point
        neighbouroutput(1, "neighbour.txt", 1000, 1000, 1000, 1000);
    }
    else
    {
        printf("\nNeighbour file creation operations have started for base [In non-adaptation Branch].");
        quadtree_neighbourset(tree->root);
        // To get number of neighbours of last point
        neighbouroutput(1, "neighbour.txt", 1000, 1000, 1000, 1000);
    }

    height_of_tree = maxDepth(tree->root);
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

    shape_list = malloc(sizeof(coords_t) * MAX);
    if (coords_list == NULL)
    {
        printf("\n ERROR : Memory allocation to shape_list was unsuccessful");
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

    char *shape_filename = argv[3];
    shape_line_count = fileinput(shape_list, shape_filename);

    non_leaf_blank_list = malloc(sizeof(coords_t) * MAX);
    if (coords_list == NULL)
    {
        printf("\n ERROR : Memory allocation to non_leaf_blank_list was unsuccessful");
        exit(0);
    }

    char *non_leaf_blank_filename = argv[4];
    non_leaf_blank_line_count = fileinput(non_leaf_blank_list, non_leaf_blank_filename);

    main_tree(line_count, coords_list, adapted_list, shape_list, leaf_array);

    printf("\nQuadtree_t: %ld\n", sizeof(quadtree_t));
    printf("\n");
    free(coords_list);
    free(adapted_list);
    free(shape_list);
    return 0;
}
