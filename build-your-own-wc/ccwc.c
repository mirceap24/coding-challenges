#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
    // check for correct number of arguments
    if (argc != 3) {
        fprintf(stderr, "Usage: %s -c <filename>\n", argv[0]);
        return 1;
    }

    // check if the option is "-c"
    if (strcmp(argv[1], "-c") != 0) {
        fprintf(stderr, "Error: Only -c option is supported\n");
        return 1;
    }

    // open file 
    FILE *file = fopen(argv[2], "rb");
    if (file == NULL) {
        perror("Error opening file");
        return 1;
    }

    // move the file pointer to the end of file 
    if (fseek(file, 0, SEEK_END) != 0) {
        perror("Error seeking file");
        fclose(file);
        return 1;
    }

    // get the position of the file pointer (which is the file size)
    long size = ftell(file);
    if (size == -1) {
        perror("Error getting file size");
        fclose(file);
        return 1;
    }

    fclose(file);

    printf(" %ld %s\n", size, argv[2]);
}