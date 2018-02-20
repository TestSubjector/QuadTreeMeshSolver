#ifndef __QUADTREE_H__
#define __QUADTREE_H__

#include <stdlib.h>
#include <math.h>
#include "bool.h"

#define MAX 10000

// A point information
// Stores x,y and maybe z later (so we get an octree)!
typedef struct quadtree_point
{
    double x;
    double y;
    double z; // For 3-D
}
quadtree_point_t;

quadtree_point_t* quadtree_point_new(double x, double y);

void quadtree_point_free(quadtree_point_t *point);


// Bounds, useful for detecting whether a point lies in a quadrant or not
typedef struct quadtree_bounds
{
    double width;
    double height;
    quadtree_point_t *nw;
    quadtree_point_t *se;
}
quadtree_bounds_t;

quadtree_bounds_t* quadtree_bounds_new();

void quadtree_bounds_extend(quadtree_bounds_t *bounds, double x, double y);

void quadtree_bounds_free(quadtree_bounds_t *bounds);


// The main node
typedef struct quadtree_node
{
    struct quadtree_node *ne;
    struct quadtree_node *nw;
    struct quadtree_node *se;
    struct quadtree_node *sw;
    quadtree_bounds_t *bounds;
    quadtree_point_t *point;
}
quadtree_node_t;

quadtree_node_t* quadtree_node_new();

void quadtree_node_free(quadtree_node_t *node);

int quadtree_node_ispointer(quadtree_node_t *node);

int quadtree_node_isempty(quadtree_node_t *node);

int quadtree_node_isleaf(quadtree_node_t *node);

void quadtree_node_reset(quadtree_node_t* node);

quadtree_node_t* quadtree_node_with_bounds(double minx, double miny, double maxx, double maxy);


// The main quadtree structure
typedef struct quadtree
{
    quadtree_node_t *root;
    unsigned int length;
}
quadtree_t;


quadtree_t* quadtree_new(double minx, double miny, double maxx, double maxy);

void quadtree_free(quadtree_t *tree);

quadtree_point_t* quadtree_search(quadtree_t *tree, double x, double y);

int quadtree_insert(quadtree_t *tree, double x, double y);

void quadtree_walk(quadtree_node_t *root, void (*descent)(quadtree_node_t *node),
                    void (*ascent)(quadtree_node_t *node));

int quadtree_print(quadtree_node_t *node);
void descent(quadtree_node_t *node);
void ascent(quadtree_node_t *node);

typedef struct coords 
{
    double x; 
    double y;
}
coords_t;

int fileinput(coords_t *coords_list, char *filename);
void fileoutput(int append, char *filename, double xcord, double ycord);
void double_to_char(double f,char *buffer);

void quadtree_leafwalk(quadtree_node_t *root, void (*descent_leaf)(quadtree_node_t *node, quadtree_node_t *leaf_array),
                    void (*ascent)(quadtree_node_t *node), quadtree_node_t *leaf_array);
void descent_leaf(quadtree_node_t *node, quadtree_node_t *leaf_array);

void quadtree_leafnodes(quadtree_node_t *root, quadtree_node_t *leaf_array);

extern int leaf_iter;


static int node_contains_patharray(quadtree_node_t *outer, double x, double y);

static quadtree_point_t *find_patharray(quadtree_node_t *node, double x, double y);

static quadtree_node_t *get_quadrant_patharray(quadtree_node_t *root,
                                      double x, double y);

int* common_ancestor(quadtree_node_t *tree, quadtree_node_t *node);

#endif