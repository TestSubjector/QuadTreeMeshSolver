#include "quadtree.h"

// Initialiaze quadtree_point
quadtree_point_t *quadtree_point_new(double x, double y)
{
    quadtree_point_t *point;
    if (!(point = malloc(sizeof(*point))))
    {
        return NULL;
    }
    point->x = x;
    point->y = y;
    return point;
}

void quadtree_point_free(quadtree_point_t *point)
{
    free(point);
}

void derefine(coords_t *derefined_list, int derefine_counter)
{
    int child_counter;
    quadtree_node_t *parent_node;
    for(int i = 0; i < derefine_counter; i++)
    {
        child_counter = 0;
        if(derefined_list[i].x != 10000 && derefined_list[i].y != 10000)
        {
            parent_node = quadtree_parent_search(derefined_list[i].x, derefined_list[i].y);
            if(parent_node == NULL)
            {
                printf("\n Warning: Problems in paret node finding");
            }

            if (quadtree_node_isempty(parent_node->nw))
            {
                child_counter += derefine_search(derefined_list, (parent_node->nw->bounds->nw->x + parent_node->nw->bounds->se->x) / 2, (parent_node->nw->bounds->nw->y + parent_node->nw->bounds->se->y) / 2, derefine_counter);
            }
            else if (quadtree_node_isleaf(parent_node->nw))
            {
                child_counter += derefine_search(derefined_list, parent_node->nw->point->x, parent_node->nw->point->y, derefine_counter);
            }
            else
            {
                //Quadrants are not on same level, so no derefinement
            }

            if (quadtree_node_isempty(parent_node->ne))
            {
                child_counter += derefine_search(derefined_list, (parent_node->ne->bounds->nw->x + parent_node->ne->bounds->se->x) / 2, (parent_node->ne->bounds->nw->y + parent_node->ne->bounds->se->y) / 2, derefine_counter);
            }
            else if (quadtree_node_isleaf(parent_node->ne))
            {
                child_counter += derefine_search(derefined_list, parent_node->ne->point->x, parent_node->ne->point->y, derefine_counter);
            }
            else
            {
                //Quadrants are not on same level, so no derefinement
            }

            if (quadtree_node_isempty(parent_node->sw))
            {
                child_counter += derefine_search(derefined_list, (parent_node->sw->bounds->nw->x + parent_node->sw->bounds->se->x) / 2, (parent_node->sw->bounds->nw->y + parent_node->sw->bounds->se->y) / 2, derefine_counter);
            }
            else if (quadtree_node_isleaf(parent_node->sw))
            {
                child_counter += derefine_search(derefined_list, parent_node->sw->point->x, parent_node->sw->point->y, derefine_counter);
            }
            else
            {
                //Quadrants are not on same level, so no derefinement
            }

            if (quadtree_node_isempty(parent_node->se))
            {
                child_counter += derefine_search(derefined_list, (parent_node->se->bounds->nw->x + parent_node->se->bounds->se->x) / 2, (parent_node->se->bounds->nw->y + parent_node->se->bounds->se->y) / 2, derefine_counter);
            }
            else if (quadtree_node_isleaf(parent_node->se))
            {
                child_counter += derefine_search(derefined_list, parent_node->se->point->x, parent_node->se->point->y, derefine_counter);
            }
            else
            {
                //Quadrants are not on same level, so no derefinement
            }

            if(child_counter == 4)
            {
                quadtree_node_free(parent_node->nw);
                quadtree_node_free(parent_node->ne);
                quadtree_node_free(parent_node->sw);
                quadtree_node_free(parent_node->se);
                parent_node->nw = NULL;
                parent_node->ne = NULL;
                parent_node->sw = NULL;
                parent_node->se = NULL;
            }
        }

    }
}

int derefine_search(coords_t *derefined_list, double x, double y, int derefine_counter)
{
    for(int i = 0; i < derefine_counter; i++)
    {
        if(derefined_list[i].x == x && derefined_list[i].y == y)
        {
            derefined_list[i].x = 10000;
            derefined_list[i].y = 10000;
            return 1;
        }
    }
    return 0;
}

quadtree_node_t *reach_ancestor(quadtree_node_t *node, int patharray[41], int ancestor_pos)
{
    int path_step = 0;
    for (int i = 0; i < ancestor_pos; i++)
    {
        path_step = patharray[i];
        if (path_step == 1)
        {
            node = node->nw;
        }
        if (path_step == 2)
        {
            node = node->ne;
        }
        if (path_step == 3)
        {
            node = node->sw;
        }
        if (path_step == 4)
        {
            node = node->se;
        }
    }
    return node;
}

int east_ancestor(int patharray[41], int path_size)
{
    int ancestor_pos = -1;
    int pathstep;
    for (int i = path_size - 1; i >= 0; i--)
    {
        pathstep = patharray[i];
        if (pathstep == 1)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Eastern neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 2)
        {
            continue;
        }
        else if (pathstep == 3)
        {
            // printf("\n Found common ancestor for Eastern neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 4)
        {
            continue;
        }
        else if (pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted patharray");
            exit(2);
        }
    }
    return ancestor_pos;
}

int west_ancestor(int patharray[41], int path_size)
{
    int ancestor_pos = -1;
    int pathstep;
    for (int i = path_size - 1; i >= 0; i--)
    {
        pathstep = patharray[i];
        if (pathstep == 1)
        {
            continue;
        }
        else if (pathstep == 2)
        {
            // printf("\n Found common ancestor for Western neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 3)
        {
            continue;
        }
        else if (pathstep == 4)
        {
            // printf("\n Found common ancestor for Western neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted patharray");
            exit(2);
        }
    }
    return ancestor_pos;    
}

int north_ancestor(int patharray[41], int path_size)
{
    int ancestor_pos = -1;
    int pathstep;
    for (int i = path_size - 1; i >= 0; i--)
    {
        pathstep = patharray[i];
        if (pathstep == 1)
        {
            continue;
        }
        else if (pathstep == 2)
        {
            continue;
        }
        else if (pathstep == 3)
        {
            // printf("\n Found common ancestor for Northern neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 4)
        {
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted patharray");
            exit(2);
        }
    }
    return ancestor_pos;    
}

int south_ancestor(int patharray[41], int path_size)
{
    int ancestor_pos = -1;
    int pathstep;
    for (int i = path_size - 1; i >= 0; i--)
    {
        pathstep = patharray[i];
        if (pathstep == 1)
        {
            // printf("\n Found common ancestor for Southern neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 2)
        {
            // Analysis - Not all leaf nodes should have eastern neighbours (the easternmost nodes)
            // printf("\n Found common ancestor for Southern neighbour");
            ancestor_pos = i;
            break;
        }
        else if (pathstep == 3)
        {
            continue;
        }
        else if (pathstep == 4)
        {
            continue;
        }
        else if (pathstep == 0)
        {
            printf("\n Array iter has problems");
        }
        else
        {
            printf("\n Some random value corrupted pathaarray");
            // exit(1);
        }
    }
    return ancestor_pos;    
}
