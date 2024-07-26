#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc != 3 || strcmp(argv[1], "-c") != 0) {
        fprintf(stderr, "Usage: %s -c <filename>\n", argv[0]);
        return 1;
    }

    FILE *file = fopen(argv[2], "rb");
    if (file == NULL) {
        perror("Error opening file");
        return 1;
    }

    fseek(file, 0, SEEK_END);
    long size = ftell(file);
    fclose(file);

    printf("%7ld %s\n", size, argv[2]);

    return 0;
}