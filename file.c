#include "quadtree.h"
#include <stdio.h>

// Put file reading portions here in the future

int fileinput(coords_t *coords_list, char *filename)
{
    char *line = NULL;
    size_t n = 0;

    FILE *coordFile = fopen(filename, "r");

    
    if(coords_list == NULL)
    {
        printf("\n Coord structure has memory problems");
        exit(0);
    }
    int line_count = 0;

    while(getline(&line, &n, coordFile) != -1 && line_count < MAX)
    {
        int items = sscanf(line, "%lf %lf", &coords_list[line_count].x, &coords_list[line_count].y);
        if(items != 2)
        {
            printf("\n File sanity check failed");
            exit(1);
        }
        line_count++;
    }

    fclose(coordFile);
    return line_count;
}