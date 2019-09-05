#include "quadtree.h"
#include <float.h>
#include <math.h>

#define min(x, y) ({                \
    __typeof__(x) _min1 = (x);          \
    __typeof__(y) _min2 = (y);          \
    (void) (&_min1 == &_min2);      \
    _min1 < _min2 ? _min1 : _min2; })

#define max(x, y) ({                \
    __typeof__(x) _max1 = (x);          \
    __typeof__(y) _max2 = (y);          \
    (void) (&_max1 == &_max2);      \
    _max1 > _max2 ? _max1 : _max2; })

// TODO - Make this soft-coded rather than hard-coded
int second_poly = 0;
int third_poly = 0;
int fourth_poly = 0;

// For blanking of points inside the solid boundary
int pnpoly(int nvert, coords_t *shape_list, double testx, double testy)
{
    int i, j, c = 1;

    // The leaf under observation stores one of the input points, so no blanking. Goes through all input points
    for (i = 0; i < nvert; i++)
    {
        if (coords_list[i].y == testy && coords_list[i].x == testx && foreign_flag == 0)
        {
            return c;
        }
        else if (shape_list[i].y == testy && shape_list[i].x == testx && foreign_flag == 1)
        {
            return c;
        }
    }

    // for (i = 0; i < adapted_line_count; i++)
    // {
    //     if (adapted_list[i].y == testy && adapted_list[i].x == testx)
    //     {
    //         return c;
    //     }
    // }

    for (i = 0, j = nvert - 1; i < nvert; j = i++) // We start from j = nvert-1 to cover the last edge
    {
        // Essentially, the condition below uses the formula {y-y1 = (y2-y1/x2-x1)*(x-x1)} and slopes to find
        // if the point lies inside the clockwise polygon or not
        if (((shape_list[i].y > testy) != (shape_list[j].y > testy)) &&
            (testx < (shape_list[j].x - shape_list[i].x) * (testy - shape_list[i].y) / (shape_list[j].y - shape_list[i].y) + shape_list[i].x))
            c = !c;
        // else if(fabs(((coords_list[j].y - coords_list[i].y) * testx - (coords_list[j].x - coords_list[i].x)* testy +
        //     (coords_list[j].x * coords_list[i].y - coords_list[j].y * coords_list[i].x)) /
        //      sqrt(pow(coords_list[j].y -coords_list[i].y, 2) + pow(coords_list[j].x - coords_list[i].x, 2))) < FLT_EPSILON)
        // {
        //     // printf("\n Removing cursed points");
        //     c = !c;
        // }
    }
    return c;
}

int non_leaf_blank(int lines, coords_t *non_leaf_blank_list, double testx, double testy)
{
    int i, return_value = 1;
    for(i = 0; i < lines; i++)
    {
        if(non_leaf_blank_list[i].y == testy && non_leaf_blank_list[i].x == testx)
        {
            printf("\n Blanking Non_Leaf Point %lf %lf", testx, testy);
            return_value = 0;
        }
    }
    return return_value;
}

// For blanking of non-aerodynamic points
int onSegment(coords_t p, coords_t q, coords_t r)
{
    if (q.x <= max(p.x, r.x) && q.x >= min(p.x, r.x) &&
        q.y <= max(p.y, r.y) && q.y >= min(p.y, r.y))
        return 1;

    return 0;
}

// To find orientation of ordered triplet (p, q, r).
// The function returns following values
// 0 --> p, q and r are colinear
// 1 --> Clockwise
// 2 --> Counterclockwise
int orientation(coords_t p, coords_t q, coords_t r)
{
    int val = (q.y - p.y) * (r.x - q.x) -
              (q.x - p.x) * (r.y - q.y);

    if (val == 0)
        return 0; // colinear

    return (val > 0) ? 1 : 2; // clock or counterclock wise
}

// The main function that returns true if line segment 'p1q1'
// and 'p2q2' intersect.
int doIntersect(coords_t p1, coords_t q1, coords_t p2, coords_t q2)
{
    // Find the four orientations needed for general and
    // special cases

    int o1 = orientation(p1, q1, p2);
    int o2 = orientation(p1, q1, q2);
    int o3 = orientation(p2, q2, p1);
    int o4 = orientation(p2, q2, q1);

    // General case
    if (o1 != o2 && o3 != o4)
        return 1;

    return 0; // Doesn't fall in any of the above cases
}

int notaero_blank(int nvert, coords_t *polygon_list, coords_t main_point, coords_t neighbour_point)
{
    int i, j, k;

    for (i = 0; i < nvert - 1; i++)
    {
        if ((main_point.x == polygon_list[i].x && main_point.y == polygon_list[i].y) ||
             (neighbour_point.x == polygon_list[i + 1].x && neighbour_point.y == polygon_list[i + 1].y) ||
             (main_point.x == polygon_list[i + 1].x && main_point.y == polygon_list[i + 1].y) ||
             (neighbour_point.x == polygon_list[i].x && neighbour_point.y == polygon_list[i].y))
        {
            for (j = 0; j < nvert; j++)
            {
                if (main_point.x == polygon_list[j].x && main_point.y == polygon_list[j].y)
                {
                    break;
                }
            }
            for (k = 0; k < nvert; k++)
            {
                if (neighbour_point.x == polygon_list[k].x && neighbour_point.y == polygon_list[k].y)
                {
                    break;
                }
            }
            if (j != nvert && k != nvert)
            {
                // printf("\n The j is %d and the k is %d", j, k);
                if (j == k + 1 || k == j + 1 || (j == 0 && k == nvert - 1) || (j == nvert - 1 && k == 0))
                {
                    return 1;
                }
                else
                {

                    return pnpoly(shape_line_count, shape_list, (main_coord.x + neighbour_point.x) / 2, (main_coord.y + neighbour_point.y) / 2);
                }
            }
        }
        else
        {
            // When main_point or neighbouring_point is not a wall point
            if (doIntersect(main_point, neighbour_point, polygon_list[i], polygon_list[i + 1]))
            {
                return 0;
            }
        }
    }
    return 1;
}
