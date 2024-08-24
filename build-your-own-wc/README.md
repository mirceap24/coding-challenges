## CCWC (Coding Challenges Word Count)

CCWC is a simple Python implementation of the Unix `wc` (word count) command. It provides functionality to count bytes, lines, words, and characters in a file or from standard input. 

### Features 
* Count bytes(`-c` option)
* Count lines (`-l` option)
* Count words (`-w` option)
* Count characters (`-m` option)
* Default mode (equivalent to `-c`, `-l` and `-w` combined)
* Support for reading from a file or standard input 

### Requirements 
* Python 3.x

### Usage 

```bash
python3 ccwc.py [OPTION] [FILE]
```

If no FILE is specified, `ccwc` reads from standard input. 

### Examples 

1. Count bytes in a file: 
```bash
python3 ccwc.py -c test.txt
342190 test.txt
```

2. Count lines in a file: 
```bash
python3 ccwc.py -l test.txt 
7145 test.txt
```

3. Count words in a file: 
```bash 
python3 ccwc.py -w test.txt 
58164 test.txt 
```

4. Count characters in a file: 
```bash 
python3 ccwc.py -m test.txt 
339292 test.txt 
```

5. Default output(lines, words, bytes):
```bash 
python3 ccwc.py test.txt 
7145 58164 342190 test.txt
```

6. Read from standard input 
```bash 
cat test.txt | python3 ccwc.py -l
7145
```

