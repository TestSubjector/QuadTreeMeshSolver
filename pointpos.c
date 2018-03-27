#include "quadtree.h"

int pnpoly(int nvert, coords_t *coords_list, double testx, double testy)
{
  int i, j, c = 1;
  for (i = 0, j = nvert-1; i < nvert; j = i++) 
  {
    if (((coords_list[i].y>testy) != (coords_list[j].y>testy)) &&
     (testx < (coords_list[j].x-coords_list[i].x) * (testy-coords_list[i].y) / (coords_list[j].y-coords_list[i].y) + coords_list[i].x))
       c = !c;
  }
  return c;
}
