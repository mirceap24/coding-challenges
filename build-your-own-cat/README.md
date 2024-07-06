# Build Your Own Cat Tool

This project guides you through creating a simplified version of the Unix `cat` command in C. The tool reads files or standard input and outputs the content, with optional line numbering.

## Features

- Read and display file contents
- Read from standard input
- Concatenate multiple files
- Number all lines (`-n` option)
- Number non-blank lines (`-b` option)

## Steps to Build

### Step 0: Setup

1. Install a C compiler (e.g., gcc)
2. Set up your preferred text editor or IDE
3. Create a new directory for the project

### Step 1: Basic File Reading

Implement basic file reading and output:

- Parse command-line arguments
- Open specified file
- Read and display file contents
- Handle basic errors (e.g., file not found)

### Step 2: Standard Input Support

Add support for reading from standard input:

- Read from stdin when no file is specified or '-' is given
- Modify the program to handle both file and stdin input

### Step 3: Multiple File Concatenation

Implement concatenation of multiple files:

- Process multiple command-line arguments
- Read and display contents of each specified file in order

### Step 4: Line Numbering

Add the `-n` option to number all output lines:

- Implement command-line option parsing
- Add line numbering logic
- Use dynamic memory allocation for reading lines

### Step 5: Numbering Non-blank Lines

Add the `-b` option to number only non-blank lines:

- Extend the option parsing to include `-b`
- Implement logic to identify and skip blank lines
- Modify line numbering to work with both `-n` and `-b` options