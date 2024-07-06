#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <sys/types.h>
#include <ctype.h>

// Enum to represent different line numbering modes 
typedef enum {
    NUMBER_NONE,        // No line numbering 
    NUMBER_ALL,         // Number all lines
    NUMBER_NONBLANK     // Number only non-blank lines
} NumberingMode;

// Function to check if a line is blank
bool is_blank_line(const char *line) {
    while (*line) {
        if (!isspace((unsigned char)*line)) {
            return false;
        }
        line++;
    }
    return true;
}

// Main function to process a file stream 
void cat_stream(FILE *stream, NumberingMode numbering, int *line_number) {
    char *buffer = NULL; 
    size_t buffer_size = 0; 
    ssize_t line_length;

    // using getline for dynamic buffer allocation
    // allows handling of lines of any length 
    while ((line_length = getline(&buffer, &buffer_size, stream)) != -1) {
        // apply line numbering 
         if (numbering == NUMBER_ALL || 
            (numbering == NUMBER_NONBLANK && !is_blank_line(buffer))) {
            printf("%d  ", (*line_number)++);
        }
        // Write the line to stdout
        fwrite(buffer, sizeof(char), line_length, stdout);
    }

    // Free the dynamically allocated buffer to prevent memory leaks
    free(buffer);
}

// Function to handle file opening and call cat_stream
void cat_file(const char *filename, NumberingMode numbering, int *line_number) {
    // Use stdin if filename is NULL or "-", otherwise open the specified file
    FILE *file = (filename == NULL || strcmp(filename, "-") == 0) ? stdin : fopen(filename, "r");
    if (file == NULL) {
        fprintf(stderr, "Error: Cannot open file '%s'\n", filename);
        exit(1);
    }

    cat_stream(file, numbering, line_number);

    // Close the file if it's not stdin
    if (file != stdin) {
        fclose(file);
    }
}

int main(int argc, char *argv[]) {
    NumberingMode numbering = NUMBER_NONE;
    int line_number = 1; 

    // parse command-line options 
    // we check for -n and -b options, updating the numbering mode accordingly
    if (argc > 1) {
        if (strcmp(argv[1], "-n") == 0) {
            numbering = NUMBER_ALL; 
            argv++;
            argc--;
        } else if (strcmp(argv[1], "-b") == 0) {
            numbering = NUMBER_NONBLANK;
            argv++;
            argc--;
        }
    }

    // if no files specified, read from stdin 
    // otherwise, process each specified file
    if (argc == 1) {
        cat_file(NULL, numbering, &line_number);
    } else {
        for (int i = 1; i < argc; i ++) {
            cat_file(argv[i], numbering, &line_number);
        }
    }

    return 0;
}