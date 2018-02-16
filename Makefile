CC=gcc

main:	bounds.o centralcode.o coords.o file.o node.o point.o quadtree.o
		cc -o main bounds.o centralcode.o coords.o file.o node.o point.o quadtree.o

quadtree.o:	quadtree.c quadtree.h
			cc -c quadtree.c

clean:
	rm main bounds.o centralcode.o coords.o node.o \
	point.o quadtree.o file.o