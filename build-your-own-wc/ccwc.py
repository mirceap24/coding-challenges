import sys 
import os 

def count_bytes_lines_words_chars(file_name):
    """Counts the number of bytes, lines, words, and charaters in a file by reading it line by line"""
    lines_count = 0 
    words_count = 0 
    chars_count = 0 

    with open(file_name, 'r') as file: 
        for line in file: 
            lines_count += 1 
            words_count += len(line.split())
            chars_count += len(line)
    
    # number of bytes from file size 
    bytes_count = os.path.getsize(file_name)

    return bytes_count, lines_count, words_count, chars_count

def count_bytes_lines_words_chars_from_stdin():
    """Counts the number of bytes, lines, words, and characters from standard input by reading it line by line"""
    bytes_count = 0 
    lines_count = 0 
    words_count = 0 
    chars_count = 0 

    for line in sys.stdin: 
        lines_count += 1 
        words_count += len(line.split())
        chars_count += len(line)
        bytes_count += len(line.encode())
    
    return bytes_count, lines_count, words_count, chars_count

def ccwc(option, file_name = None):
    """Processes the file content or standard input based on the option provided."""
    if file_name:
        bytes_count, lines_count, words_count, chars_count = count_bytes_lines_words_chars(file_name)
    else: 
        bytes_count, lines_count, words_count, chars_count = count_bytes_lines_words_chars_from_stdin()
    
    if option == '-c':
        print(f"{bytes_count}", end = ' ')
        if file_name:
            print(file_name)
    elif option == '-l':
        print(f"{lines_count}", end = ' ')
        if file_name:
            print(file_name)
    elif option == '-w':
        print(f"{words_count}", end = ' ')
        if file_name:
            print(file_name)
    elif option == '-m':
        print(f"{chars_count}", end = ' ')
        if file_name:
            print(file_name)
    else: 
        # Default case, print lines, words and bytes 
        print(f"{lines_count} {words_count} {bytes_count}", end = ' ')
        if file_name:
            print(file_name)

def main():
    if len(sys.argv) == 2 and sys.argv[1] not in ['-c', '-l', '-w', '-m']:
        # only filename provided, use default output 
        file_name = sys.argv[1]
        ccwc(None, file_name)
    elif len(sys.argv) == 3: 
        option = sys.argv[1]
        file_name = sys.argv[2]
        ccwc(option, file_name)
    elif len(sys.argv) == 2 and sys.argv[1] in ['-c', '-l', '-w', '-m']:
        # read from stdin 
        option = sys.argv[1]
        ccwc(option)
    else: 
        # no arguments, read from stdin with default option 
        ccwc(None)


if __name__ == "__main__":
    main()