#include "quadtree.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

int leaf_iter = 0;
coords_t *coords_list;
coords_t *adapted_list;
int line_count = 0;
quadtree_t *tree;
int adapt_flag = 0;

void main_tree(int initial_coord_length, coords_t *coords_list, quadtree_node_t *leaf_array)
{
    tree = quadtree_new(-5, -5, 5, 5);
    // double xcord = (tree->root->bounds->nw->x + tree->root->bounds->se->x) / 2;
    // double ycord = (tree->root->bounds->nw->y + tree->root->bounds->se->y) / 2;
    // printf("\n ********This could be a horrow show (%lf,%lf) ", xcord, ycord);
    int i = 0;
    for (i = 0; i < initial_coord_length; i++)
    {
        int success = quadtree_insert(tree, coords_list[i].x, coords_list[i].y);
        if (success == 0)
        {
            // Out of bounds
            printf("\n Problems with line %d, and points %lf & %lf", i + 1, coords_list[i].x, coords_list[i].y);
        }
    }

    // Adaptation section
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
    quadtree_node_t *leaf_array[MAX];
    printf("\nquadtree_t: %ld\n", sizeof(quadtree_t));

    char *filename = argv[1];
    line_count = fileinput(coords_list, filename);

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

    line_count = fileinput(coords_list, filename);
    serial_number = 1;
    neighbouroutput(0, "neighbour.txt", 1000, 1000);
    main_tree(line_count, coords_list, leaf_array);
    */
   
    return 0;
}
