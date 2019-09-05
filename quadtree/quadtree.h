#ifndef __QUADTREE_H__
#define __QUADTREE_H__

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "bool.h"

#define MAX 700000

// A point information
// Stores x,y and maybe z later (so we get an octree)!
typedef struct quadtree_point
{
    double x;
    double y;
    // double z; // For 3-D
} quadtree_point_t;

quadtree_point_t *quadtree_point_new(double x, double y);

void quadtree_point_free(quadtree_point_t *point);

// Bounds, useful for detecting whether a point lies in a quadrant or not
typedef struct quadtree_bounds
{
    double width;
    double height;
    quadtree_point_t *nw;
    quadtree_point_t *se;
} quadtree_bounds_t;

quadtree_bounds_t *quadtree_bounds_new();

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
    int height;
    int direction;
    int blank;
} quadtree_node_t;

quadtree_node_t *quadtree_node_new();

void quadtree_node_free(quadtree_node_t *node);

int quadtree_node_ispointer(quadtree_node_t *node);

int quadtree_node_isempty(quadtree_node_t *node);

int quadtree_node_isleaf(quadtree_node_t *node);

void quadtree_node_reset(quadtree_node_t *node);

quadtree_node_t *quadtree_node_with_bounds(double minx, double miny, double maxx, double maxy);

// The main quadtree structure
typedef struct quadtree
{
    quadtree_node_t *root;
    unsigned int length;
} quadtree_t;

quadtree_t *quadtree_new(double minx, double miny, double maxx, double maxy);

void quadtree_free(quadtree_t *tree);

quadtree_node_t *quadtree_search(double x, double y);

int quadtree_insert(quadtree_t *tree, double x, double y);

void quadtree_walk(quadtree_node_t *root, void (*descent)(quadtree_node_t *node),
                   void (*ascent)(quadtree_node_t *node));

int quadtree_print(quadtree_node_t *node);
void descent(quadtree_node_t *node);
void ascent(quadtree_node_t *node);

//Struct that stores all input points for file handling
typedef struct coords
{
    double x;
    double y;
} coords_t;

int fileinput(coords_t *coords_list, char *filename);
void fileoutput(int append, char *filename, double xcord, double ycord);
void double_to_char(double f, char *buffer);

void quadtree_leafwalk(quadtree_node_t *root, void (*descent_leaf)(quadtree_node_t *node, quadtree_node_t *leaf_array),
                       void (*ascent)(quadtree_node_t *node), quadtree_node_t *leaf_array);
void descent_leaf(quadtree_node_t *node, quadtree_node_t *leaf_array);

void quadtree_leafnodes(quadtree_node_t *root, quadtree_node_t *leaf_array);

extern int leaf_iter;

int node_contains_patharray(quadtree_node_t *outer, double x, double y);

quadtree_point_t *find_patharray(quadtree_node_t *node, double x, double y);

quadtree_point_t *find_patharray_diagonal(quadtree_node_t *node, double x, double y);

quadtree_node_t *get_quadrant_patharray(quadtree_node_t *root,
                                               double x, double y);

quadtree_node_t *get_quadrant_patharray_diagonal(quadtree_node_t *root, double x, double y);

int *common_treeroute(quadtree_node_t *tree, quadtree_node_t *node);

int *common_ancestor_diagonal(quadtree_node_t *root, quadtree_node_t *node);

void find_neighbours(quadtree_t *tree, int patharray[41], quadtree_node_t *leaf_array);

void balance_neighbours(quadtree_t *tree, int patharray[41], int ancestor_pos, int direction, quadtree_node_t *leaf_array);

int split_node_newpoints(quadtree_t *tree, quadtree_node_t *node);

int insert_(quadtree_t *tree, quadtree_node_t *root,
            quadtree_point_t *point);

// For blanking of points
double main_pointy;

int pnpoly(int nvert, coords_t *shape_list, double testx, double testy);

extern coords_t *coords_list;
extern coords_t *shape_list;
extern int line_count;
extern int shape_line_count;

// For finding neighbour_set of points

void quadtree_neighbourset(quadtree_node_t *root);

void quadtree_neighbourwalk(quadtree_node_t *root,
                            void (*descent_node)(quadtree_node_t *node, FILE *fp),
                            void (*ascent)(quadtree_node_t *node), FILE *fp);

void descent_node(quadtree_node_t *node, FILE *fp);

extern quadtree_t *tree;

void quadtree_refinementwalk(quadtree_node_t *root,
                             void (*descent_refinement)(quadtree_node_t *node),
                             void (*ascent)(quadtree_node_t *node));

void descent_refinement(quadtree_node_t *node);

void find_neighbourset(int patharray[41], quadtree_node_t *node, FILE *fp);

void balance_neighboursset(int patharray[41], int ancestor_pos, int direction, FILE *fp);

// File reading for neighbourset

void neighbouroutput(FILE *fp, double xcord, double ycord, int node_height, int direction);

void neighbourset(FILE *fp, double xcord, double ycord);

// To prevent a point stating itself as a neighbour

extern int serial_number;

// For blanking of non-aerodynamic points
int notaero_blank(int nvert, coords_t *coords_list, coords_t main_point, coords_t neighnour_point);

extern coords_t main_coord;

int adapt(quadtree_t *tree, quadtree_node_t *node, double x, double y);

extern int checker;

void eastern_diagonal_neighbourset(quadtree_node_t *node, int mainnode_direction, FILE *fp);

void western_diagonal_neighbourset(quadtree_node_t *node, int mainnode_direction, FILE *fp);

void northern_diagonal_neighbourset(quadtree_node_t *root, int mainnode_direction, FILE *fp);

void southern_diagonal_neighbourset(quadtree_node_t *node, int mainnode_direction, FILE *fp);

extern coords_t *adapted_list;
extern int adapted_line_count;

int adaptation_fileinput(coords_t *adapted_list, char *adapted_filename);

extern int newoutputfile;
extern int newneighboursetfile;
extern int second_poly;

void quadtree_valleywalk(quadtree_node_t *root, void (*descent_valley)(quadtree_node_t *node),
                             void (*ascent)(quadtree_node_t *node));

void descent_valley(quadtree_node_t *node);
void valley_refinement(quadtree_node_t *valley_node, int flag);

int maxDepth(quadtree_node_t *node);

extern int height_of_tree;

quadtree_node_t *reach_ancestor(quadtree_node_t *node, int patharray[41], int ancestor_pos);

int east_ancestor(int patharray[41], int path_size);
int west_ancestor(int patharray[41], int path_size);
int north_ancestor(int patharray[41], int path_size);
int south_ancestor(int patharray[41], int path_size);

int wallpoint_insert_flag;

void extraoutput(FILE *fp, double nw_bound_xcord, double nw_bound_ycord, double se_bound_xcord, double se_bound_ycord, double flag);

coords_t *derefined_list;
void derefine_fromlist(coords_t *derefined_list, int derefine_counter);
quadtree_node_t *quadtree_parent_search(double x, double y);
int derefine_search(coords_t *derefined_list, double x, double y, int derefine_counter);

int foreign_flag;
void centroidify(quadtree_node_t *node, coords_t *shape_list);
void quadtree_foreignwalk(quadtree_node_t *root, void (*descent_foreign)(quadtree_node_t *node, coords_t *shape_list),
                             void (*ascent)(quadtree_node_t *node), coords_t *shape_list);
void descent_foreign(quadtree_node_t *node, coords_t *shape_list);

void quadtree_hillwalk(quadtree_node_t *root, void (*descent_hill)(quadtree_node_t *node),
                             void (*ascent)(quadtree_node_t *node));
void descent_hill(quadtree_node_t *node);
void hill_derefinement(quadtree_node_t *hill_node, int flag);

int hills_and_valleys_block_flag;

void non_leaf_neighbours(quadtree_node_t *node, FILE *fp);
void write_quadtree_node_to_file(quadtree_node_t *node, FILE *fp);

int only_leaf_flag;

int non_leaf_immediate_neighbours_check(quadtree_node_t *node);

extern coords_t *non_leaf_blank_list;
extern int non_leaf_blank_line_count;

int non_leaf_blank(int lines, coords_t *non_leaf_blank_list, double testx, double testy);

void quadtree_blankwalk(quadtree_node_t *root, void (*descent_blank)(quadtree_node_t *node),
                       void (*ascent)(quadtree_node_t *node));

void descent_blank(quadtree_node_t *node);

#endif
