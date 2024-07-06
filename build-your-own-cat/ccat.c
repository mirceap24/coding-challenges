#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void cat_stream(FILE *stream) {
    int ch; 
    while ((ch = fgetc(stream)) != EOF) {
        putchar(ch);
    }
}

void cat_file(const char *filename) {
    if (filename == NULL || strcmp(filename, "-") == 0) {
        cat_stream(stdin);
    } else {
        FILE *file = fopen(filename, "r");
        if (file == NULL) {
            fprintf(stderr, "Error: Cannot open file '%s'\n", filename);
            exit(1);
        }
        cat_stream(file);
        fclose(file);
    }
}

int main(int argc, char *argv[]) {
    if (argc == 1) {
        cat_file(NULL);
    } else {
        for (int i = 1; i < argc; i ++) {
            cat_file(argv[i]);
        }
    }
    return 0;
}