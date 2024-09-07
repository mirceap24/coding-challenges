#include <stdio.h>
#include <stdlib.h>
#include <string.h>

long count_bytes(const char *filename) {
    FILE *file = fopen(filename, "rb");
    if (file == NULL) {
        perror("Error opening file");
        return -1;
    }

    if (fseek(file, 0, SEEK_END) != 0) {
        perror("Error seeking file");
        fclose(file);
        return -1;
    }

    long size = ftell(file);
    if (size == -1) {
        perror("Error getting file size");
        fclose(file);
        return -1;
    }

    fclose(file);
    return size;
}

long count_lines(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening file");
        return -1;
    }

    long line_count = 0;
    int ch; 

    while ((ch = fgetc(file)) != EOF) {
        if (ch == '\n') {
            line_count++;
        }
    }

     if (ferror(file)) {
        perror("Error reading file");
        fclose(file);
        return -1;
    }

    fclose(file);
    return line_count;
}

long count_words(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening file");
        return -1;
    }

    long word_count = 0; 
    int in_word = 0; 
    int ch;

    while ((ch = fgetc(file)) != EOF) {
        if (isspace(ch)) {
            // if the current character is whitespace
            // mark that we're no longer inside a word
            in_word = 0;
        } else if (in_word == 0) {
            // if current char is not whitespace and we weren't in a word
            // mark that we're inside a word now
            in_word = 1; 
            word_count++;   // increment word_count
        }
    }

    if (ferror(file)) {
        perror("Error reading file");
        fclose(file);
        return -1;
    }

    fclose(file);
    return word_count;
}

int main(int argc, char *argv[]) {
    // Check if we have the correct number of arguments
    if (argc != 3) {
        fprintf(stderr, "Usage: %s [-c|-l] <filename>\n", argv[0]);
        return 1;
    }

    const char *option = argv[1];
    const char *filename = argv[2];
    long result;

    if (strcmp(option, "-c") == 0) {
        result = count_bytes(filename);
    } else if (strcmp(option, "-l") == 0) {
        result = count_lines(filename);
    } else if (strcmp(option, "-w") == 0) {
        result = count_words(filename);
    }
    else {
        fprintf(stderr, "Error: Unsuported option.");
        return 1;
    }

    if (result == -1) {
        return 1;
    }

    printf(" %ld %s\n", result, filename);

    return 0;
}