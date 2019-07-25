CC=gcc -std=c18 -ggdb -O2 -Werror=implicit-function-declaration -Wl,-z,now -fstack-protector

main:	bounds.o centralcode.o file.o node.o treepoint.o pointpos.o quadtree.o quadtree_neighbourset.o
		cc -o main bounds.o centralcode.o file.o node.o treepoint.o pointpos.o quadtree.o quadtree_neighbourset.o -lm

quadtree.o:	quadtree.c quadtree.h bool.h
			cc -c quadtree.c -lm



clean:
	rm main bounds.o centralcode.o node.o \
	treepoint.o quadtree.o file.o pointpos.o quadtree_neighbourset.o
