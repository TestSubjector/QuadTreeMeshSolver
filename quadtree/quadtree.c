#include "quadtree.h"
#include "bool.h"
#include <stdio.h>
#include <string.h>
#include <float.h>
#include <math.h>

int newoutputfile = 1;
int newneighboursetfile = 1;
coords_t main_coord;
int checker = 0;

// Declarations
static int split_leafnode_(quadtree_t *tree, quadtree_node_t *node);
static int node_contains_(quadtree_node_t *outer, quadtree_point_t *it);
static quadtree_node_t *get_quadrant_(quadtree_node_t *root, quadtree_point_t *point);

/* Static Definitions */
// This function return 1 if the specified point lies in the quadrant, else returns 0
static int node_contains_(quadtree_node_t *outer, quadtree_point_t *it)
{
    return outer->bounds != NULL && outer->bounds->nw->x <= it->x &&
           outer->bounds->nw->y >= it->y && outer->bounds->se->x >= it->x &&
           outer->bounds->se->y <= it->y;
}

static void reset_node_(quadtree_t *tree, quadtree_node_t *node)
{
    quadtree_node_reset(node);
}

// Decide which children to traverse into
static quadtree_node_t *get_quadrant_(quadtree_node_t *root, quadtree_point_t *point)
{
    if (node_contains_(root->nw, point))
    {
        return root->nw;
    }
    if (node_contains_(root->ne, point))
    {
        return root->ne;
    }
    if (node_contains_(root->sw, point))
    {
        return root->sw;
    }
    if (node_contains_(root->se, point))
    {
        return root->se;
    }
    return NULL;
}

static int split_leafnode_(quadtree_t *tree, quadtree_node_t *node)
{
    // Remove input point from node, create 4 children for it and set bounds for all of them
    // Then lastly insert the old input point into one of the children
    quadtree_node_t *nw = NULL;
    quadtree_node_t *ne = NULL;
    quadtree_node_t *sw = NULL;
    quadtree_node_t *se = NULL;
    quadtree_point_t *old = NULL;

    double x = node->bounds->nw->x;
    double y = node->bounds->nw->y;
    double hw = node->bounds->width / 2;
    double hh = node->bounds->height / 2;

    // minx,   miny,       maxx,       maxy
    if (!(nw = quadtree_node_with_bounds(x, y - hh, x + hw, y)))
        return 0;
    if (!(ne = quadtree_node_with_bounds(x + hw, y - hh, x + hw * 2, y)))
        return 0;
    if (!(sw = quadtree_node_with_bounds(x, y - hh * 2, x + hw, y - hh)))
        return 0;
    if (!(se = quadtree_node_with_bounds(x + hw, y - hh * 2, x + hw * 2, y - hh)))
        return 0;

    node->nw = nw;
    nw->height = node->height + 1;
    nw->direction = 1;
    node->ne = ne;
    ne->height = node->height + 1;
    ne->direction = 2;
    node->sw = sw;
    sw->height = node->height + 1;
    sw->direction = 3;
    node->se = se;
    se->height = node->height + 1;
    se->direction = 4;

    old = node->point;
    node->point = NULL;

    return insert_(tree, node, old);
}

static quadtree_node_t *find_(quadtree_node_t *node, double x, double y)
{
    if (!node)
    {
        // printf("\n Start");
        return NULL;
    }
    if (quadtree_node_isleaf(node))
    {
        // printf("\n Start 1");
        // printf("\n Wanted %lf, %lf", x, y);
        // printf("\n Wanted %lf, %lf", node->point->x, node->point->y);
        if (node->point->x == x && node->point->y == y)
        {
            // printf("\n Start 2");
            return node;
        }
    }
    else if (quadtree_node_isempty(node))
    {
        if (fabs((node->bounds->nw->x + node->bounds->se->x) / 2 - x) < 0.0000000001 &&
            fabs((node->bounds->nw->y + node->bounds->se->y) / 2 - y) < 0.0000000001)
        {
            return node;
        }
        else if(x > (node->bounds->nw->x - 0.0000000001) &&
                x < (node->bounds->se->x + 0.0000000001) &&
                y > (node->bounds->se->y - 0.0000000001) &&
                y < (node->bounds->nw->y + 0.0000000001))
        {
            return node;
        }
        else
        {
            // printf("\n %.17g, %.17g", (node->bounds->nw->x + node->bounds->se->x) / 2, (node->bounds->nw->y + node->bounds->se->y)/2);
        }
    }
    else if (quadtree_node_ispointer(node))
    {
        // printf("\n Start 3");
        if (fabs((node->bounds->nw->x + node->bounds->se->x) / 2 - x) < 0.0000000001 &&
            fabs((node->bounds->nw->y + node->bounds->se->y) / 2 - y) < 0.0000000001)
        {
            return node;
        }
        quadtree_point_t test;
        test.x = x;
        test.y = y;
        return find_(get_quadrant_(node, &test), x, y);
    }
    return NULL;
}

static quadtree_node_t *parent_find_(quadtree_node_t *node, double x, double y, quadtree_node_t *parent_node)
{
    if (!node)
    {
        // printf("\n Start");
        return NULL;
    }
    if (quadtree_node_isleaf(node))
    {
        // printf("\n Start 1");
        // printf("\n Wanted %lf, %lf", x, y);
        // printf("\n Wanted %lf, %lf", node->point->x, node->point->y);
        if (node->point->x == x && node->point->y == y)
        {
            // printf("\n Start 2");
            return parent_node;
        }
    }
    else if (quadtree_node_isempty(node))
    {
        if (fabs((node->bounds->nw->x + node->bounds->se->x) / 2 - x) < 0.0000000001 &&
            fabs((node->bounds->nw->y + node->bounds->se->y) / 2 - y) < 0.0000000001)
        {
            return parent_node;
        }
        else
        {
            // printf("\n %.17g, %.17g", (node->bounds->nw->x + node->bounds->se->x) / 2, (node->bounds->nw->y + node->bounds->se->y)/2);
        }
    }
    else if (quadtree_node_ispointer(node))
    {
        // printf("\n Start 3");
        quadtree_point_t test;
        test.x = x;
        test.y = y;
        return parent_find_(get_quadrant_(node, &test), x, y, node);
    }
    return NULL;
}

/* Non-Static Definitions */

quadtree_t *quadtree_new(double minx, double miny, double maxx, double maxy)
{
    quadtree_t *tree;
    if (!(tree = malloc(sizeof(*tree))))
    {
        return NULL;
    }

    tree->root = quadtree_node_with_bounds(minx, miny, maxx, maxy);
    if (!(tree->root))
    {
        return NULL;
    }
    tree->length = 0;
    return tree;
}

quadtree_node_t *quadtree_search(double x, double y)
{
    return find_(tree->root, x, y);
}

quadtree_node_t *quadtree_parent_search(double x, double y)
{
    return parent_find_(tree->root, x, y, NULL);
}

void quadtree_free(quadtree_t *tree)
{
    quadtree_node_free(tree->root);
    free(tree);
}

// Create quadtree_point from an input point and use helper_function to insert into the tree
int quadtree_insert(quadtree_t *tree, double x, double y)
{
    quadtree_point_t *point;
    int insert_status;

    if (!(point = quadtree_point_new(x, y)))
    {
        return 0; // Point not created
    }
    if (!node_contains_(tree->root, point))
    {
        quadtree_point_free(point);
        return 0; // Point is out of defined bounds
    }

    // Using helper_function for point insertion
    if (!(insert_status = insert_(tree, tree->root, point)))
    {
        quadtree_point_free(point); // Simple memory cleanup
        return 0;
    }
    if (insert_status == 1)
    {
        tree->length++;
    }
    return insert_status;
    // Returns 1 if quadtree_point is successfully created, else returns 0
}

int insert_(quadtree_t *tree, quadtree_node_t *root, quadtree_point_t *point)
{
    if (quadtree_node_isempty(root)) // Insert point into empty leaf
    {
        root->point = point;
        return 1; /* Normal insertion flag */
    }
    else if (quadtree_node_isleaf(root)) // Insert point into leaf that has another input point
    {
        // The root point is same as new point to be inserted
        if (root->point->x == point->x && root->point->y == point->y)
        {
            reset_node_(tree, root);
            root->point = point;
            return 2; /* Replace insertion flag */
        }
        else
        {
            if (!split_leafnode_(tree, root)) // Points are different, split leaf into 4 leaves
            {
                return 0; /* Failed insertion flag */
            }
            return insert_(tree, root, point); // Insert input point into one of the new leaves created (may lead to further leaf splitting)
        }
    }
    else if (quadtree_node_ispointer(root)) // A node which has 4 children from which one will be traversed
    {
        quadtree_node_t *quadrant = get_quadrant_(root, point);
        return quadrant == NULL ? 0 : insert_(tree, quadrant, point);
    }
    return 0;
}

// Function to adapt specific point
int adapt(quadtree_t *tree, quadtree_node_t *node, double x, double y)
{
    if (!node)
    {
        return 0;
    }
    if (quadtree_node_isleaf(node))
    {
        if (node->point->x == x && node->point->y == y)
        {
            split_leafnode_(tree, node);
            return 1;
        }
    }
    else if (quadtree_node_ispointer(node))
    {
        quadtree_point_t test;
        test.x = x;
        test.y = y;
        return adapt(tree, get_quadrant_(node, &test), x, y);
    }
    return 0;
}

// Traversal for getting all the leaf nodes
void quadtree_leafwalk(quadtree_node_t *root, void (*descent_leaf)(quadtree_node_t *node, quadtree_node_t *leaf_array),
                       void (*ascent)(quadtree_node_t *node), quadtree_node_t *leaf_array)
{
    (*descent_leaf)(root, leaf_array);
    if (root->nw != NULL)
    {
        quadtree_leafwalk(root->nw, descent_leaf, ascent, leaf_array);
    }
    if (root->ne != NULL)
    {
        quadtree_leafwalk(root->ne, descent_leaf, ascent, leaf_array);
    }
    if (root->sw != NULL)
    {
        quadtree_leafwalk(root->sw, descent_leaf, ascent, leaf_array);
    }
    if (root->se != NULL)
    {
        quadtree_leafwalk(root->se, descent_leaf, ascent, leaf_array);
    }
    (*ascent)(root);
}

// The completing function for 'quadtree_leafwalk"
void descent_leaf(quadtree_node_t *node, quadtree_node_t *leaf_array)
{
    // If it is an leaf(empty or filled), then add to leaf array
    if ((quadtree_node_isempty(node)) || (quadtree_node_isleaf(node)))
    {
        leaf_array[leaf_iter] = *node;
        leaf_iter++;
        // printf("%d", leaf_iter);
    }
}

// Finding all the leaves one by one for neighbour set
void quadtree_neighbourwalk(quadtree_node_t *root, void (*descent_node)(quadtree_node_t *node),
                            void (*ascent)(quadtree_node_t *node))
{
    (*descent_node)(root);
    if (root->nw != NULL)
    {
        quadtree_neighbourwalk(root->nw, descent_node, ascent);
    }
    if (root->ne != NULL)
    {
        quadtree_neighbourwalk(root->ne, descent_node, ascent);
    }
    if (root->sw != NULL)
    {
        quadtree_neighbourwalk(root->sw, descent_node, ascent);
    }
    if (root->se != NULL)
    {
        quadtree_neighbourwalk(root->se, descent_node, ascent);
    }
    (*ascent)(root);
}

// The completing funtion for 'quadtree_neighbourwalk'
// It will fed all the nodes present in the tree and find neighbourset for the leaves
void descent_node(quadtree_node_t *node)
{
    char *filename = "neighbour.txt";
    if (quadtree_node_isempty(node)) // For empty leaf
    {
        double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
        double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
        main_coord.x = xcord;
        main_coord.y = ycord;
        // The commented out code below is to check for specific points
        // if(xcord == 8.75 && ycord == 8.75)
        // {
        //   checker = 1;
        // }
        // else
        // {
        //   checker = 0;
        // }
        if (checker == 1)
        {
            printf("\n ABC");
        }
        if (pnpoly(shape_line_count, shape_list, xcord, ycord))
        {
            if (newneighboursetfile == 1)
            {
                neighbouroutput(0, filename, xcord, ycord, node->height, node->direction);
                newneighboursetfile = 0;
            }
            else
            {
                neighbouroutput(1, filename, xcord, ycord, node->height, node->direction);
            }
            extraoutput(1, filename,
                        node->bounds->nw->x, node->bounds->nw->y,
                        node->bounds->se->x, node->bounds->se->y, 0);
            // printf("\n %lf %lf has neighbours\t", xcord, ycord);
            find_neighbourset(common_treeroute(tree->root, node), node);
        }
    }
    else if (quadtree_node_isleaf(node)) // For filled leaf
    {
        checker = 0;
        main_coord.x = node->point->x;
        main_coord.y = node->point->y;
        if (newneighboursetfile == 1)
        {
            neighbouroutput(0, filename, node->point->x, node->point->y, node->height, node->direction);
            newneighboursetfile = 0;
        }
        else
        {
            neighbouroutput(1, filename, node->point->x, node->point->y, node->height, node->direction);
        }
        extraoutput(1, filename,
                    node->bounds->nw->x, node->bounds->nw->y,
                    node->bounds->se->x, node->bounds->se->y, 0);
        // printf("\n %lf %lf has neighbours\t", node->point->x, node->point->y);
        find_neighbourset(common_treeroute(tree->root, node), node);
    }
    else if (quadtree_node_ispointer(node) && node->height > 1 && only_leaf_flag == 0)
    {
        double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
        double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
        int flag = 0;
        // flag = non_leaf_immediate_neighbours_check(node);

        if (pnpoly(shape_line_count, shape_list, xcord, ycord) && flag == 0)
        {
            if (newneighboursetfile == 1)
            {
                neighbouroutput(0, filename, xcord, ycord, node->height, node->direction);
                newneighboursetfile = 0;
            }
            else
            {
                neighbouroutput(1, filename, xcord, ycord, node->height, node->direction);
            }
            extraoutput(1, filename,
                        node->bounds->nw->x, node->bounds->nw->y,
                        node->bounds->se->x, node->bounds->se->y, 1);
            // printf("\n %lf %lf has neighbours\t", xcord, ycord);
            non_leaf_neighbours(node);
        }
    }

}

void quadtree_walk(quadtree_node_t *root,
                   void (*descent)(quadtree_node_t *node),
                   void (*ascent)(quadtree_node_t *node))
{
    (*descent)(root);
    if (root->nw != NULL)
    {
        quadtree_walk(root->nw, descent, ascent);
    }
    if (root->ne != NULL)
    {
        quadtree_walk(root->ne, descent, ascent);
    }
    if (root->sw != NULL)
    {
        quadtree_walk(root->sw, descent, ascent);
    }
    if (root->se != NULL)
    {
        quadtree_walk(root->se, descent, ascent);
    }
    (*ascent)(root);
}

void descent(quadtree_node_t *node)
{

    if (quadtree_node_isempty(node))
    {
        char *filename = "output.txt";
        double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
        double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
        if (newoutputfile == 1)
        {
            fileoutput(0, filename, xcord, ycord);
            newoutputfile = 0;
        }
        else
        {
            fileoutput(1, filename, xcord, ycord);
        }
    }
}

void ascent(quadtree_node_t *node)
{
    // printf("\n");
}

void quadtree_refinementwalk(quadtree_node_t *root, void (*descent_refinement)(quadtree_node_t *node),
                             void (*ascent)(quadtree_node_t *node))
{
    // printf("\n 0");
    if (root->nw != NULL)
    {
        quadtree_refinementwalk(root->nw, descent_refinement, ascent);
    }
    if (root->ne != NULL)
    {
        quadtree_refinementwalk(root->ne, descent_refinement, ascent);
    }
    if (root->sw != NULL)
    {
        quadtree_refinementwalk(root->sw, descent_refinement, ascent);
    }
    if (root->se != NULL)
    {
        quadtree_refinementwalk(root->se, descent_refinement, ascent);
    }
    (*descent_refinement)(root);
    (*ascent)(root);
}

void descent_refinement(quadtree_node_t *node)
{
    // printf("\n 1");
    if ((quadtree_node_isempty(node)) || (quadtree_node_isleaf(node)))
    {
        split_node_newpoints(tree, node);
    }
}

void quadtree_valleywalk(quadtree_node_t *root, void (*descent_valley)(quadtree_node_t *node),
                         void (*ascent)(quadtree_node_t *node))
{
    if (root->nw != NULL)
    {
        quadtree_valleywalk(root->nw, descent_valley, ascent);
    }
    if (root->ne != NULL)
    {
        quadtree_valleywalk(root->ne, descent_valley, ascent);
    }
    if (root->sw != NULL)
    {
        quadtree_valleywalk(root->sw, descent_valley, ascent);
    }
    if (root->se != NULL)
    {
        quadtree_valleywalk(root->se, descent_valley, ascent);
    }
    (*descent_valley)(root);
    (*ascent)(root);
}

void descent_valley(quadtree_node_t *node)
{
    if ((quadtree_node_isempty(node)) || (quadtree_node_isleaf(node)))
    {
        // double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
        // double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
        // if(xcord == 0.966796875 && (ycord == -0.029296875 || ycord == 0.029296875))
        // {
        //   checker = 2;
        //   printf("\n Yabba Dabba");
        // }
        // else
        // {
        //   checker = 0;
        // }
        valley_refinement(node, 1);
    }
}

void quadtree_foreignwalk(quadtree_node_t *root, void (*descent_foreign)(quadtree_node_t *node, coords_t *shape_list),
                          void (*ascent)(quadtree_node_t *node), coords_t *shape_list)
{
    if (root->nw != NULL)
    {
        quadtree_foreignwalk(root->nw, descent_foreign, ascent, shape_list);
    }
    if (root->ne != NULL)
    {
        quadtree_foreignwalk(root->ne, descent_foreign, ascent, shape_list);
    }
    if (root->sw != NULL)
    {
        quadtree_foreignwalk(root->sw, descent_foreign, ascent, shape_list);
    }
    if (root->se != NULL)
    {
        quadtree_foreignwalk(root->se, descent_foreign, ascent, shape_list);
    }
    (*descent_foreign)(root, shape_list);
    (*ascent)(root);
}

void descent_foreign(quadtree_node_t *node, coords_t *shape_list)
{
    if (quadtree_node_isleaf(node))
    {
        int centroid_flag = 0;
        int i = 0;
        for (i = 0; i < shape_line_count; i++)
        {
            if (node->point->x == shape_list[i].x && node->point->y == shape_list[i].y)
            {
                centroid_flag = 1;
                break;
            }
        }
        if (centroid_flag != 1)
        {
            node->point = NULL;
        }
        else
        {
            // printf("0\n");
        }
    }
}

void quadtree_hillwalk(quadtree_node_t *root, void (*descent_hill)(quadtree_node_t *node),
                       void (*ascent)(quadtree_node_t *node))
{
    if (root->nw != NULL)
    {
        quadtree_hillwalk(root->nw, descent_hill, ascent);
    }
    if (root->ne != NULL)
    {
        quadtree_hillwalk(root->ne, descent_hill, ascent);
    }
    if (root->sw != NULL)
    {
        quadtree_hillwalk(root->sw, descent_hill, ascent);
    }
    if (root->se != NULL)
    {
        quadtree_hillwalk(root->se, descent_hill, ascent);
    }
    (*descent_hill)(root);
    (*ascent)(root);
}

void descent_hill(quadtree_node_t *node)
{
    if ((quadtree_node_isempty(node)))
    {
        hill_derefinement(node, 1);
    }
}
