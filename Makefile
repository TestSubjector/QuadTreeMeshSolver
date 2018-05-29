CC=gcc

main:	bounds.o centralcode.o file.o node.o point.o pointpos.o quadtree.o quadtree_neighbourset.o
		cc -o main bounds.o centralcode.o file.o node.o point.o pointpos.o quadtree.o quadtree_neighbourset.o -lm

quadtree.o:	quadtree.c quadtree.h bool.h
			cc -c quadtree.c -lm



clean:
	rm main bounds.o centralcode.o node.o \
	point.o quadtree.o file.o pointpos.o quadtree_neighbourset.o
	