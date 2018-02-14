#include "quadtree.h"
#include <stdio.h>

static int split_node_(quadtree_t *tree, quadtree_node_t *node);

static int insert_(quadtree_t* tree, quadtree_node_t *root, quadtree_point_t *point);

static int node_contains_(quadtree_node_t *outer, quadtree_point_t *it);

static quadtree_node_t *get_quadrant_(quadtree_node_t *root, quadtree_point_t *point);

/* private implementations */
static int node_contains_(quadtree_node_t *outer, quadtree_point_t *it)
{
    return outer->bounds != NULL
        && outer->bounds->nw->x <= it->x
        && outer->bounds->nw->y >= it->y
        && outer->bounds->se->x >= it->x
        && outer->bounds->se->y <= it->y;
}

static void reset_node_(quadtree_t *tree, quadtree_node_t *node)
{
    quadtree_node_reset(node);
}

static quadtree_node_t *get_quadrant_(quadtree_node_t *root, quadtree_point_t *point)
{
    if(node_contains_(root->nw, point))
    {
        return root->nw;
    }
    if(node_contains_(root->ne, point))
    {
        return root->ne;
    }
    if(node_contains_(root->sw, point))
    {
        return root->sw;
    }
    if(node_contains_(root->se, point))
    {
        return root->se;
    }
    return NULL;
}


static int split_node_(quadtree_t *tree, quadtree_node_t *node)
{
    quadtree_node_t *nw;
    quadtree_node_t *ne;
    quadtree_node_t *sw;
    quadtree_node_t *se;
    quadtree_point_t *old;

    double x  = node->bounds->nw->x;
    double y  = node->bounds->nw->y;
    double hw = node->bounds->width / 2;
    double hh = node->bounds->height / 2;

                                        //minx,   miny,       maxx,       maxy
    if(!(nw = quadtree_node_with_bounds(x,      y - hh,     x + hw,     y))) return 0;
    if(!(ne = quadtree_node_with_bounds(x + hw, y - hh,     x + hw * 2, y))) return 0;
    if(!(sw = quadtree_node_with_bounds(x,      y - hh * 2, x + hw,     y - hh))) return 0;
    if(!(se = quadtree_node_with_bounds(x + hw, y - hh * 2, x + hw * 2, y - hh))) return 0;

    node->nw = nw;
    node->ne = ne;
    node->sw = sw;
    node->se = se;

    old = node->point;
    node->point = NULL;

  return insert_(tree, node, old);
}


static quadtree_point_t* find_(quadtree_node_t* node, double x, double y)
{
    if(!node)
    {
      return NULL;
    }
    if(quadtree_node_isleaf(node))
    {
        if(node->point->x == x && node->point->y == y)
        {
            return node->point;
        }
    }
    else if(quadtree_node_ispointer(node))
    {
        quadtree_point_t test;
        test.x = x;
        test.y = y;
        return find_(get_quadrant_(node, &test), x, y);
    }
    return NULL;
}


static int insert_(quadtree_t* tree, quadtree_node_t *root, quadtree_point_t *point)
{
    if(quadtree_node_isempty(root))
    {
        root->point = point;
        return 1; /* normal insertion flag */
    }
    // The root point is same as new point to be inserted
    else if(quadtree_node_isleaf(root))
    {
        if(root->point->x == point->x && root->point->y == point->y)
        {
            reset_node_(tree, root);
            root->point = point;
            return 2; /* replace insertion flag */
        }
        else
        {
            if(!split_node_(tree, root))
            {
                return 0; /* failed insertion flag */
            }
            return insert_(tree, root, point);
        }
    }
    else if(quadtree_node_ispointer(root))
    {
        quadtree_node_t* quadrant = get_quadrant_(root, point);
        return quadrant == NULL ? 0 : insert_(tree, quadrant, point);
    }
    return 0;
}


quadtree_t* quadtree_new(double minx, double miny, double maxx, double maxy)
{
    quadtree_t *tree;
    if(!(tree = malloc(sizeof(*tree))))
    {
        return NULL;
    }

    tree->root = quadtree_node_with_bounds(minx, miny, maxx, maxy);
    if(!(tree->root))
    {
        return NULL;
    }
    tree->length = 0;
    return tree;
}


int quadtree_insert(quadtree_t *tree, double x, double y)
{
    quadtree_point_t *point;
    int insert_status;

    if(!(point = quadtree_point_new(x, y)))
    {
        return 0;
    }
    if(!node_contains_(tree->root, point))
    {
        quadtree_point_free(point);
        return 0;
    }

    if(!(insert_status = insert_(tree, tree->root, point)))
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

quadtree_point_t* quadtree_search(quadtree_t *tree, double x, double y)
{
    return find_(tree->root, x, y);
}

void quadtree_free(quadtree_t *tree)
{
    quadtree_node_free(tree->root);
    free(tree);
}

void quadtree_walk(quadtree_node_t *root, void (*descent)(quadtree_node_t *node),
                                     void (*ascent)(quadtree_node_t *node))
{
    (*descent)(root);
    if(root->nw != NULL)
    {
        quadtree_walk(root->nw, descent, ascent);
    }
    if(root->ne != NULL)
    {
        quadtree_walk(root->ne, descent, ascent);
    }
    if(root->sw != NULL)
    {
        quadtree_walk(root->sw, descent, ascent);
    }
    if(root->se != NULL)
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
    //     // printf("\n { nw.x:%f, nw.y:%f, se.x:%f, se.y:%f }: ", node->bounds->nw->x, 
    //     //     node->bounds->nw->y, node->bounds->se->x, node->bounds->se->y);
    // }
    if(node->bounds != NULL && quadtree_node_isempty(node))
    {
        // printf("\n Centroids Quad : { nw.x:%f, nw.y:%f, se.x:%f, se.y:%f }: ", node->bounds->nw->x, 
        //     node->bounds->nw->y, node->bounds->se->x, node->bounds->se->y);
        printf("%f %f\n", (node->bounds->nw->x + node->bounds->se->x)/2, (node->bounds->nw->y + node->bounds->se->y)/2);
    }
}

void ascent(quadtree_node_t *node)
{
    // printf("\n");
}
