CC ?= cc
CFLAGS ?= -Wall -Wextra -O2

.PHONY: all clean test

all: hello

hello: main.c
	$(CC) $(CFLAGS) main.c -o hello

test: hello
	@test "$$($(CURDIR)/hello)" = "hello E3"
	@echo "PASS: hello E3"

clean:
	rm -f hello
