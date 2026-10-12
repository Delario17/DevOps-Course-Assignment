#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{
    if (argc == 2 && strcmp(argv[1], "--version") == 0) {
        puts("tiny-greeting 1.0.0");
        return 0;
    }
    if (argc != 1) {
        fprintf(stderr, "usage: %s [--version]\n", argv[0]);
        return 2;
    }

    puts("hello E3");
    return 0;
}
