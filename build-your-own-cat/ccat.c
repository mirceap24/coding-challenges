#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <sys/types.h>

void cat_stream(FILE *stream, bool number_lines, int *line_number) {
    char *buffer = NULL; 
    size_t buffer_size = 0; 
    ssize_t line_length;

    while ((line_length = getline(&buffer, &buffer_size, stream)) != -1) {
        if (number_lines) {
            printf("%d  ", (*line_number)++);
        }
        fwrite(buffer, sizeof(char), line_length, stdout);
    }

    free(buffer);
}

void cat_file(const char *filename, bool number_lines, int *line_number) {
    FILE *file = (filename == NULL || strcmp(filename, "-") == 0) ? stdin : fopen(filename, "r");
    if (file == NULL) {
        fprintf(stderr, "Error: Cannot open file '%s'\n", filename);
        exit(1);
    }

    cat_stream(file, number_lines, line_number);

    if (file != stdin) {
        fclose(file);
    }
}

int main(int argc, char *argv[]) {
    bool number_lines = false; 
    int line_number = 1; 

    if (argc > 1 && strcmp(argv[1], "-n") == 0) {
        number_lines = true; 
        argv++;
        argc--;
    }

    if (argc == 1) {
        cat_file(NULL, number_lines, &line_number);
    } else {
        for (int i = 1; i < argc; i ++) {
            cat_file(argv[i], number_lines, &line_number);
        }
    }

    return 0;
}