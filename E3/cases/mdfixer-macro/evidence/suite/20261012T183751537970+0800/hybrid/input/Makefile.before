CC := gcc
CPPFLAGS := -Iinclude
CFLAGS := -Wall -Wextra -O2
# Intentional MD: config.h omitted. Intentional RD: unused.h declared.
HEADERS := include/common.h include/unused.h

.PHONY: all clean
all: bin/demo

bin/demo: build/main.o
	mkdir -p bin
	$(CC) $(CFLAGS) build/main.o -o bin/demo

build/main.o: src/main.c $(HEADERS)
	mkdir -p build
	$(CC) $(CPPFLAGS) $(CFLAGS) -c src/main.c -o build/main.o

clean:
	rm -rf build bin
