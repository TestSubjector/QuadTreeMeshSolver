#include "quadtree.h"
#include "bool.h"
#include <stdio.h>
#include <string.h>

int newoutputfile = 1;
int newneighboursetfile = 1;
coords_t main_coord;

// Declarations
static int split_node_(quadtree_t *tree, quadtree_node_t *node);
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

static int split_node_(quadtree_t *tree, quadtree_node_t *node)
{
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
  node->ne = ne;
  node->sw = sw;
  node->se = se;

  old = node->point;
  node->point = NULL;

  return insert_(tree, node, old);
}

static quadtree_point_t *find_(quadtree_node_t *node, double x, double y)
{
  if (!node)
  {
    return NULL;
  }
  if (quadtree_node_isleaf(node))
  {
    if (node->point->x == x && node->point->y == y)
    {
      return node->point;
    }
  }
  else if (quadtree_node_ispointer(node))
  {
    quadtree_point_t test;
    test.x = x;
    test.y = y;
    return find_(get_quadrant_(node, &test), x, y);
  }
  return NULL;
}


/* Non-Static Definitions */
// Insert an input point into the tree
int quadtree_insert(quadtree_t *tree, double x, double y)
{
  quadtree_point_t *point;
  int insert_status;

  if (!(point = quadtree_point_new(x, y)))
  {
    return 0;
  }
  if (!node_contains_(tree->root, point))
  {
    quadtree_point_free(point);
    return 0;
  }

  if (!(insert_status = insert_(tree, tree->root, point)))
  {
    quadtree_point_free(point);
    return 0;
  }
  if (insert_status == 1)
  {
    tree->length++;
  }
  return insert_status;
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
      split_node_(tree, node);
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

int insert_(quadtree_t *tree, quadtree_node_t *root, quadtree_point_t *point)
{
  if (quadtree_node_isempty(root))
  {
    root->point = point;
    return 1; /* normal insertion flag */
  }
  // The root point is same as new point to be inserted
  else if (quadtree_node_isleaf(root))
  {
    if (root->point->x == point->x && root->point->y == point->y)
    {
      reset_node_(tree, root);
      root->point = point;
      return 2; /* replace insertion flag */
    }
    else
    {
      if (!split_node_(tree, root))
      {
        return 0; /* failed insertion flag */
      }
      return insert_(tree, root, point);
    }
  }
  else if (quadtree_node_ispointer(root))
  {
    quadtree_node_t *quadrant = get_quadrant_(root, point);
    return quadrant == NULL ? 0 : insert_(tree, quadrant, point);
  }
  return 0;
}

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

quadtree_point_t *quadtree_search(quadtree_t *tree, double x, double y)
{
  return find_(tree->root, x, y);
}

void quadtree_free(quadtree_t *tree)
{
  quadtree_node_free(tree->root);
  free(tree);
}

// For getting all the leaf arrays
void quadtree_leafwalk(quadtree_node_t *root,
                       void (*descent_leaf)(quadtree_node_t *node, quadtree_node_t *leaf_array),
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
  if ((node->bounds != NULL && quadtree_node_isempty(node)) || (quadtree_node_isleaf(node)))
  {
    leaf_array[leaf_iter] = *node;
    leaf_iter++;
    // printf("%d", leaf_iter);
  }
}

// Finding leaves one by one for neighbour set
void quadtree_neighbourwalk(quadtree_node_t *root,
                            void (*descent_node)(quadtree_node_t *node),
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
// It will one-by-one go through all the pointss and find neighbourset
void descent_node(quadtree_node_t *node)
{
  char *filename = "neighbour.txt";
  if (node->bounds != NULL && quadtree_node_isempty(node))
  {
    double xcord = (node->bounds->nw->x + node->bounds->se->x) / 2;
    double ycord = (node->bounds->nw->y + node->bounds->se->y) / 2;
    main_coord.x = xcord;
    main_coord.y = ycord;
    if (newneighboursetfile == 1)
    {
      // printf("\n*********Fileclean");
      neighbouroutput(0, filename, xcord, ycord);
      newneighboursetfile = 0;
    }
    else
    {
      neighbouroutput(1, filename, xcord, ycord);
    }
    printf("\n %lf %lf has neighbours\t", xcord, ycord);
    find_neighbourset(common_ancestor(tree->root, node), node);
  }
  else if (quadtree_node_isleaf(node))
  {
    main_coord.x = node->point->x;
    main_coord.y = node->point->y;
    if (newneighboursetfile == 1)
    {
      // printf("\n*********Fileclean");
      neighbouroutput(0, filename, node->point->x, node->point->y);
      newneighboursetfile = 0;
    }
    else
    {
      neighbouroutput(1, filename, node->point->x, node->point->y);
    }
    printf("\n %lf %lf has neighbours\t", node->point->x, node->point->y);
    find_neighbourset(common_ancestor(tree->root, node), node);
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
  // if(node->point != NULL)
  // {
  //     printf("%lf %lf \n", node->point->x, node->point->y);
  //     // printf("\n { nw.x:%f, nw.y:%f, se.x:%f, se.y:%f }: ",
  //     node->bounds->nw->x,
  //     //     node->bounds->nw->y, node->bounds->se->x, node->bounds->se->y);
  // }
  if (node->bounds != NULL && quadtree_node_isempty(node))
  {
    // printf("\n Centroids Quad : { nw.x:%f, nw.y:%f, se.x:%f, se.y:%f }: ",
    // node->bounds->nw->x,
    //     node->bounds->nw->y, node->bounds->se->x, node->bounds->se->y);
    //printf("\n%f %f", (node->bounds->nw->x + node->bounds->se->x) / 2,
    //       (node->bounds->nw->y + node->bounds->se->y) / 2);
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
