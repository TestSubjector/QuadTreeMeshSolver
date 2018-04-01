#include "quadtree.h"
#define min(x, y) ({                \
    typeof(x) _min1 = (x);          \
    typeof(y) _min2 = (y);          \
    (void) (&_min1 == &_min2);      \
    _min1 < _min2 ? _min1 : _min2; })

#define max(x, y) ({                \
    typeof(x) _max1 = (x);          \
    typeof(y) _max2 = (y);          \
    (void) (&_max1 == &_max2);      \
    _max1 > _max2 ? _max1 : _max2; })


// For blanking of points inside the solid boundary
int pnpoly(int nvert, coords_t *coords_list, double testx, double testy)
{
    int i, j, c = 1;

    // Point on boundary, then not inside the polygon
    for(i= 0; i< nvert; i++)
    {
        if(coords_list[i].y == testy && coords_list[i].x == testx)
        {
            return c;
        }
    }

    for (i = 0, j = nvert-1; i < nvert; j = i++) 
    {
        if (((coords_list[i].y>testy) != (coords_list[j].y>testy)) &&
            (testx < (coords_list[j].x- coords_list[i].x) * (testy - coords_list[i].y) / (coords_list[j].y - coords_list[i].y) + coords_list[i].x))
                c = !c;
    }
    return c;
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
 
    if (val == 0) return 0;  // colinear
 
    return (val > 0)? 1: 2; // clock or counterclock wise
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
 
    // Special Cases
    // p1, q1 and p2 are colinear and p2 lies on segment p1q1
    // if (o1 == 0 && onSegment(p1, p2, q1)) return 1;
 
    // p1, q1 and q2 are colinear and q2 lies on segment p1q1
    // if (o2 == 0 && onSegment(p1, q2, q1)) return 1;
 
    // p2, q2 and p1 are colinear and p1 lies on segment p2q2
    // if (o3 == 0 && onSegment(p2, p1, q2)) return 1;
 
     // p2, q2 and q1 are colinear and q1 lies on segment p2q2
    // if (o4 == 0 && onSegment(p2, q1, q2)) return 1;
 
    return 0; // Doesn't fall in any of the above cases
}

int notaero_blank(int nvert, coords_t *coords_list, coords_t main_point, coords_t neighbour_point)
{
    int i, j, k;
    // printf(" \n It's running atleast");

    // Point on boundary, then not inside the polygon
    for(i = 0; i < nvert - 1; i++)
    {
        if((main_point.x == coords_list[i].x && main_point.y == coords_list[i].y 
            || neighbour_point.x == coords_list[i+1].x && neighbour_point.y == coords_list[i+1].y
            || main_point.x == coords_list[i+1].x && main_point.y == coords_list[i+1].y
            || neighbour_point.x == coords_list[i].x && neighbour_point.y == coords_list[i].y))
        {
            for(j = 0; j< nvert; j++)
            {
                if(main_point.x == coords_list[j].x && main_point.y == coords_list[j].y)
                {
                    break;
                }
            }
            for(k = 0; k <nvert; k++)
            {
                if(neighbour_point.x == coords_list[k].x && neighbour_point.y == coords_list[k].y)
                {
                    break;
                }
            }
            if(j!= nvert && k!=nvert)
            {
                // printf("\n The j is %d and the k is %d", j, k);
                if(j == k + 1 || k == j +1 || (j == 0 && k == nvert-1) || (j == nvert-1 && k==0))
                {
                    return 1;
                }
                else
                {
                    return pnpoly(line_count, coords_list, (main_coord.x + neighbour_point.x)/2, (main_coord.y + neighbour_point.y)/2 );
                }
            }
            else
            {
                return 1;
            }
        }
        else
        {
            if(doIntersect(main_point, neighbour_point, coords_list[i], coords_list[i+1]))
            {
                return 0;
            }
        }
    }
    return 1;
}

