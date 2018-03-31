#include "bool.h"
#include "quadtree.h"
#include <stdio.h>

double main_pointx;
double main_pointy;

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
        if (items != 2) {
          printf("\n File sanity check failed");
          exit(1);
        }
        line_count++;
    }
    fclose(coordFile);
    return line_count;
}

void fileoutput(int append, char *filename, double xcord, double ycord) 
{
    // The if condition checks for blanking points
    
    char xcordstr[11];
    char ycordstr[11];
    gcvt(xcord,10,xcordstr);
    gcvt(ycord,10,ycordstr);
    // double_to_char(xcord,xcordstr);
    // double_to_char(ycord,ycordstr);
    FILE *fp = NULL;
    if (append==1) 
    {
        fp = fopen(filename, "a+");
    } 
    else 
    {
        fp = fopen(filename, "w");
    }
    if(pnpoly(line_count, coords_list, xcord, ycord))
    {
        if (fp != NULL) 
        {
            fputs(xcordstr, fp);
            fputs(" ",fp);
            fputs(ycordstr,fp);
            fputs("\n",fp);
            fclose(fp);
        }
    }
}

void neighbouroutput(int append, char *filename, double xcord, double ycord) 
{
    main_pointx = xcord;
    main_pointy = ycord;
    // The if condition checks for blanking points

    char xcordstr[11];
    char ycordstr[11];
    gcvt(xcord,10,xcordstr);
    gcvt(ycord,10,ycordstr);
    // double_to_char(xcord,xcordstr);
    // double_to_char(ycord,ycordstr);
    FILE *fp = NULL;
    if (append==1) 
    {
        fp = fopen(filename, "a+");
    } 
    else 
    {
        fp = fopen(filename, "w");
    }
    //if(pnpoly(line_count, coords_list, xcord, ycord))
    {    
        if (fp != NULL) 
        {
            fputs("\n", fp);
            fputs(xcordstr, fp);
            fputs(" ",fp);
            fputs(ycordstr,fp);
            fputs(" has the neighbours : ",fp);
            fclose(fp);
        }
        
    }
}

void neighbourset(int append, char *filename, double xcord, double ycord) 
{
  // The if condition checks for blanking points
    char xcordstr[11];
    char ycordstr[11];
    gcvt(xcord,10,xcordstr);
    gcvt(ycord,10,ycordstr);
    // double_to_char(xcord,xcordstr);
    // double_to_char(ycord,ycordstr);
    FILE *fp = NULL;
    if (append==1) {
      fp = fopen(filename, "a+");
    } else {
      fp = fopen(filename, "w");
    }
    if(pnpoly(line_count, coords_list, xcord, ycord))
    {
        if (fp != NULL) {
          fputs("(", fp);
          fputs(xcordstr, fp);
          fputs(",",fp);
          fputs(ycordstr,fp);
          fputs(") ",fp);
          fclose(fp);
        }
    }
} 
