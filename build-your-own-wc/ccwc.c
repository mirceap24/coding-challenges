#include <stdio.h>
#include <stdlib.h>
#include <string.h>

long count_bytes(const char *filename) {
    FILE *file = fopen(filename, "rb");
    if (file == NULL) {
        perror("Error opening file");
        exit(1);
    }
    fseek(file, 0, SEEK_END);
    long size = ftell(file);
    fclose(file);
    return size;
}

long count_lines(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening file");
        exit(1);
    }
    long lines = 0;
    int ch;
    while ((ch = fgetc(file)) != EOF) {
        if (ch == '\n') {
            lines++;
        }
    }
    fclose(file);
    return lines;
}

int main(int argc, char *argv[]) {
    if (argc != 3 || (strcmp(argv[1], "-c") != 0 && strcmp(argv[1], "-l") != 0)) {
        fprintf(stderr, "Usage: %s [-c|-l] <filename>\n", argv[0]);
        return 1;
    }

    const char *option = argv[1];
    const char *filename = argv[2];
    long count;

    if (strcmp(option, "-c") == 0) {
        count = count_bytes(filename);
    } else {
        count = count_lines(filename);
    }

    printf("%7ld %s\n", count, filename);

    return 0;
}