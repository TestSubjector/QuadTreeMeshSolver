CC=gcc -std=c18 -ggdb

main:	bounds.o centralcode.o file.o node.o treepoint.o pointpos.o quadtree.o quadtree_neighbourset.o
		cc -std=c11 -o main bounds.o centralcode.o file.o node.o treepoint.o pointpos.o quadtree.o quadtree_neighbourset.o -lm

quadtree.o:	quadtree.c quadtree.h bool.h
			cc -c quadtree.c -lm



clean:
	rm main bounds.o centralcode.o node.o \
	treepoint.o quadtree.o file.o pointpos.o quadtree_neighbourset.o
	
