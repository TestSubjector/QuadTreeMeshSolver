#define _GNU_SOURCE
#include "bool.h"
#include "quadtree.h"
#include <stdio.h>

int serial_number = 1;
int neighbour_counter = 0;

// File input function to store the input coordinates
int fileinput(coords_t *coords_list, char *filename)
{
    char *line = NULL;
    size_t n = 0;
    int local_line_count = 0;

    FILE *coordFile = fopen(filename, "r");

    // Take x & y input from each line and store in coords_list
    while (getline(&line, &n, coordFile) != -1 && local_line_count < MAX)
    {
        int items = sscanf(line, "%lf %lf", &coords_list[local_line_count].x,
                           &coords_list[local_line_count].y);
        if (items != 2)
        {
            printf("\n ERROR : Input file does not have correct coordinate format");
            exit(1);
        }
        local_line_count++;
    }
    if(fclose(coordFile) != 0)
    {
        printf("\n ERROR - Input file stream didn't close properly");
        exit(1);
    }
    free(line);
    return local_line_count;
    // Returns total number of input points
}

int adaptation_fileinput(coords_t *adapted_list, char *adapted_filename)
{
    char *adapted_line = NULL;
    size_t adapted_n = 0;
    int local_line_count = 0;
    double xi = 0;
    double yi = 0;

    FILE *adapted_coordFile = fopen(adapted_filename, "r");

    // Take x & y input from each line and store in coords_list
    // while(fscanf(adapted_coordFile, "%lf %lf", xi, yi) != EOF)
    // {
    //     printf("\n %lf %lf the points are", xi, yi);
    //     local_line_count++;
    // }

    while (getline(&adapted_line, &adapted_n, adapted_coordFile) != -1 && local_line_count < MAX)
    {
        int items = sscanf(adapted_line, "%lf %lf", &adapted_list[local_line_count].x,
                           &adapted_list[local_line_count].y);
        if (items != 2)
        {
            printf("\n ERROR : Adapted file does not have correct coordinate format");
            exit(1);
        }
        // printf("\n %lf, %lf", adapted_list[local_line_count].x, adapted_list[local_line_count].y);
        local_line_count++;
    }

    fclose(adapted_coordFile);
    if(local_line_count == 0)
    {
        printf("\nStatus: Adapted file is empty, no adaptation will happen.");
    }
    else
    {
        printf("\n Please note that the adaptation is happening.");
    }
    free(adapted_line);
    return local_line_count;
    // Returns total number of input points
}

// File output function to give the coordinates of all points of the grid
void fileoutput(int append, char *filename, double xcord, double ycord)
{
    // The if condition checks for blanking points
    char xcordstr[20];
    char ycordstr[20];
    gcvt(xcord, 18, xcordstr);
    gcvt(ycord, 18, ycordstr);

    // if (strstr(xcordstr, ycordstr) != NULL && fabs(xcord) != fabs(ycord))
    // {
    //     printf("\n xcordstr is %s", xcordstr);
    // }
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
    if (fp == NULL)
    {
        printf("\n ERROR : File creation of point data was unsuccessful");
        exit(1);
    }
    if (pnpoly(shape_line_count, shape_list, xcord, ycord))
    {
        fputs(xcordstr, fp);
        fputs(" ", fp);
        fputs(ycordstr, fp);
        fputs("\n", fp);
    }
    fclose(fp);
}

// File output function to calculate valid neighbours for points
void neighbouroutput(int append, char *filename, double xcord, double ycord, int node_height, int direction)
{
    char xcordstr[25];
    char ycordstr[25];
    char heightstr[25];
    char directionstr[25];
    char serialnumstr[25];
    char neighbourcountstr[25];
    gcvt(xcord, 24, xcordstr);
    gcvt(ycord, 24, ycordstr);
    gcvt(node_height,2, heightstr);
    gcvt(direction, 2, directionstr);
    gcvt(serial_number, 10, serialnumstr);

    FILE *fp = NULL;
    if (append == 1)
    {
        fp = fopen(filename, "a+"); 
    }
    else
    {
        fp = fopen(filename, "w"); // Replace the old file with a blank line
    }

    if (fp == NULL)
    {
        printf("\n ERROR : File creation of neighbourhood data was unsuccessful");
        exit(1);
    }

    if (xcord == 1000 && ycord == 1000)
    {
        // Do nothing
        // printf("Last point counted");
        gcvt(neighbour_counter, 10, neighbourcountstr);
        fputs("\t", fp);
        fputs(neighbourcountstr, fp);
    }
    // Checks for blanking points i.e points inside the input polygon
    else
    {
        if (neighbour_counter != 0)
        {
            gcvt(neighbour_counter, 10, neighbourcountstr);
            fputs("\t", fp);
            fputs(neighbourcountstr, fp);
        }
        neighbour_counter = 0;

        fputs("\t\n", fp);
        fputs(serialnumstr, fp);
        fputs("\t", fp);
        fputs(xcordstr, fp);
        fputs(",", fp);
        fputs(ycordstr, fp);
        fputs("\t", fp);
        fputs(heightstr, fp);
        fputs("\t", fp);
        fputs(directionstr, fp);
        fputs("\t", fp);

        serial_number++; // Increment the S.No for new point
    }
    fclose(fp);
}


// For on-demand additions to the output files
void extraoutput(int append, char *filename,
                    double nw_bound_xcord, double nw_bound_ycord, 
                    double se_bound_xcord, double se_bound_ycord
                )
{
    char nw_xcordstr[20];
    char nw_ycordstr[20];
    char se_xcordstr[20];
    char se_ycordstr[20];
    
    gcvt(nw_bound_xcord, 18, nw_xcordstr);
    gcvt(nw_bound_ycord, 18, nw_ycordstr);
    gcvt(se_bound_xcord, 18, se_xcordstr);
    gcvt(se_bound_ycord, 18, se_ycordstr);

    FILE *fp = NULL;
    if (append == 1)
    {
        fp = fopen(filename, "a+");
    }
    else
    {
        printf("\n Warning: File Type: Problem with developing file format for additional parameters");
    }

    fputs(nw_xcordstr, fp);
    fputs("\t", fp);
    fputs(nw_ycordstr, fp);
    fputs("\t", fp);
    fputs(se_xcordstr, fp);
    fputs("\t", fp);
    fputs(se_ycordstr, fp);
    fputs("\t", fp);
    
    fclose(fp);
}

void neighbourset(int append, char *filename, double xcord, double ycord)
{
    // The if condition checks for blanking points
    char xcordstr[25];
    char ycordstr[25];
    gcvt(xcord, 24, xcordstr);
    gcvt(ycord, 24, ycordstr);
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
    if (pnpoly(shape_line_count, shape_list, xcord, ycord))
    {
        coords_t neighbour_point;
        neighbour_point.x = xcord;
        neighbour_point.y = ycord;

        neighbour_counter++;
        if (fp != NULL)
        {
            fputs(xcordstr, fp);
            fputs(",", fp);
            fputs(ycordstr, fp);
            fputs("\t", fp);
        }
    }
    fclose(fp);
}
