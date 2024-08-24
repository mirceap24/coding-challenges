## cccat - Coding Challenges Concatenate 

`cccat` is a Python implementation of the Unix `cat` command, with additional features for line numbering. It allows you to concatenate and display the contents of files, as well as read from standard input. 

### Features 
* Read and display contents of multiple files 
* Read from standard input 
* Concatenate multiple files 
* Number all lines (`-n` option)
* Number only non-blank lines (`-b` option)

### Requirements 
* Python 3.x 

### Usage 
```bash
python3 cccat.py [-n | -b] [file ...]
```
* `-n`: Number all output lines 
* `-b`: Number only non-blank output lines 
* `file`: Path to the file(s) to be read. Use `-` for standard input. 

### Examples 
1. Display contents of a file: 
```bash 
python3 cccat.py test.txt
```

2. Read from standard input:
```bash 
head -n1 test.txt | python3 cccat.py -
```

3. Concatenate multiple files: 
```bash
python3 cccat.py test.txt test2.txt
```

4. Number lines as they're printed out:
```bash 
head -n3 test.txt | python3 cccat.py -n
```

5. Number lines, including blank ones
```bash 
sed G test.txt | python3 cccat.py -n | head -n4
```

6. Number all lines, excluding blank ones
```bash 
sed G test.txt | python3 cccat.py -b | head -n4
```

### Implementation Details 
The `cccat` program is implemented in Python and consists of a main function `cccat` that handles file reading and line processing. Here's a brief overview of its components:

* `cccat(files, number_lines, number_nonblank)`: Main function that processes files and stdin.
* `process_line(line)`: Helper function to handle line numbering and output.

The program uses the `sys` module to read command-line arguments and handle standard input/output operations.

### Error Handling 
* If a specified file is not found, an error message is printed to `stderr`.
* If both `-n` and `-b` options are used simultaneously, an error message is displayed and the program exits.

