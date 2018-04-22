#include "bool.h"
#include "quadtree.h"
#include <stdio.h>

int serial_number = 1;
int neighbour_counter;

// File input function to store the input coordinates
int fileinput(coords_t *coords_list, char *filename)
{
    char *line = NULL;
    size_t n = 0;

    FILE *coordFile = fopen(filename, "r");

    if (coords_list == NULL)
    {
        printf("\n Coord structure has memory problems");
        exit(0);
    }
    int line_count = 0;

    while (getline(&line, &n, coordFile) != -1 && line_count < MAX)
    {
        int items = sscanf(line, "%lf %lf", &coords_list[line_count].x,
                           &coords_list[line_count].y);
        if (items != 2)
        {
            printf("\n File sanity check failed");
            exit(1);
        }
        line_count++;
    }
    fclose(coordFile);
    return line_count;
}

// File output function to give the coordinates of all points of the grid
void fileoutput(int append, char *filename, double xcord, double ycord)
{
    // The if condition checks for blanking points

    char xcordstr[11];
    char ycordstr[11];
    gcvt(xcord, 10, xcordstr);
    gcvt(ycord, 10, ycordstr);
    // double_to_char(xcord,xcordstr);
    // double_to_char(ycord,ycordstr);
    FILE *fp = NULL;
    if (append == 1)
    {
        fp = fopen(filename, "a+");
    }
    else
    {
        fp = fopen(filename, "w");
    }
    if (pnpoly(line_count, coords_list, xcord, ycord))
    {
        if (fp != NULL)
        {
            fputs(xcordstr, fp);
            fputs(" ", fp);
            fputs(ycordstr, fp);
            fputs("\n", fp);
            fclose(fp);
        }
    }
}

// File output function to calculate validate neighbours for points
void neighbouroutput(int append, char *filename, double xcord, double ycord)
{
    // The if condition checks for blanking points
    char xcordstr[11];
    char ycordstr[11];
    char serialnumstr[11];
    char neighbourcountstr[11];
    gcvt(xcord, 10, xcordstr);
    gcvt(ycord, 10, ycordstr);
    gcvt(serial_number, 10, serialnumstr);
    // double_to_char(xcord,xcordstr);
    // double_to_char(ycord,ycordstr);
    FILE *fp = NULL;
    if (append == 1)
    {
        fp = fopen(filename, "a+");
    }
    else
    {
        fp = fopen(filename, "w");
    }
    if (xcord == 1000 && ycord == 1000)
    {
        // Do nothing
        // printf("Last point counted");
        gcvt(neighbour_counter, 10, neighbourcountstr);
        fputs("\t", fp);
        fputs(neighbourcountstr, fp);
    }
    else if (pnpoly(line_count, coords_list, xcord, ycord))
    {
        if (neighbour_counter != 0)
        {
            gcvt(neighbour_counter, 10, neighbourcountstr);
            fputs("\t", fp);
            fputs(neighbourcountstr, fp);
        }
        neighbour_counter = 0;
        if (fp != NULL)
        {
            fputs("\t\n", fp);
            fputs(serialnumstr, fp);
            serial_number++;
            fputs("\t", fp);
            fputs(xcordstr, fp);
            fputs(",", fp);
            fputs(ycordstr, fp);
            fputs("\t\t", fp);
            fclose(fp);
        }
    }
    else
    {
        // printf("\n Blanked point, and so ignored");
    }
}

void neighbourset(int append, char *filename, double xcord, double ycord)
{
    // The if condition checks for blanking points
    char xcordstr[11];
    char ycordstr[11];
    gcvt(xcord, 10, xcordstr);
    gcvt(ycord, 10, ycordstr);
    // double_to_char(xcord,xcordstr);
    // double_to_char(ycord,ycordstr);
    FILE *fp = NULL;
    if (append == 1)
    {
        fp = fopen(filename, "a+");
    }
    else
    {
        fp = fopen(filename, "w");
    }
    if (pnpoly(line_count, coords_list, xcord, ycord))
    {
        coords_t neighbour_point;
        neighbour_point.x = xcord;
        neighbour_point.y = ycord;
        if (notaero_blank(line_count, coords_list, main_coord, neighbour_point))
        {
            neighbour_counter++;
            if (fp != NULL)
            {
                fputs(" ", fp);
                fputs(xcordstr, fp);
                fputs(",", fp);
                fputs(ycordstr, fp);
                fputs("\t", fp);
                fclose(fp);
            }
        }
        else
        {
            // printf("\n \n Non - Aero blanked \n\n");
        }
    }
}
