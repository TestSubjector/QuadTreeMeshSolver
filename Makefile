CC=gcc

main:	bounds.o centralcode.o coords.o file.o node.o point.o pointpos.o quadtree.o quadtree_neighbourset.o
		cc -o main bounds.o centralcode.o coords.o file.o node.o point.o pointpos.o quadtree.o quadtree_neighbourset.o

quadtree.o:	quadtree.c quadtree.h bool.h
			cc -c quadtree.c



clean:
	rm main bounds.o centralcode.o coords.o node.o \
	point.o quadtree.o file.o pointpos.o quadtree_neighbourset.o
	