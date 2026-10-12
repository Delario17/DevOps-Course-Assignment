#include <stdio.h>
#include <string.h>
#include "common.h"
#include "config.h"

int main(int argc, char **argv)
{
    if (argc == 2 && strcmp(argv[1], "--version") == 0) {
        puts("demo 1.0.0");
        return 0;
    }
    if (argc != 1) {
        fprintf(stderr, "usage: %s [--version]\n", argv[0]);
        return 2;
    }
    printf("%d\n", COMMON_VALUE + CONFIG_VALUE);
    return 0;
}
