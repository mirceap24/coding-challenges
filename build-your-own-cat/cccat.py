import sys 

def cccat(files = None, number_lines = False, number_nonblank = False):
    """
    Concatenate and print files or stdin, with optional line numbering.

    Args: 
    files (list): List of filenames to process. None or '-' for stdin
    number_lines (bool): if True, number all lines
    number_nonblank (bool): If True, number only non-blank lines
    """
    line_number = 1 

    # function to process a single line 
    def process_line(line):
        nonlocal line_number
        if number_lines or (number_nonblank and line.strip()):
            # number the line if the conditions are met 
            output = f"{line_number:6d}  {line}"
            line_number += 1 
        else: 
            output = line 
        print(output, end = '')
    
    # process stdin if no files are specified or '-' is in the file list 
    if not files or '-' in files: 
        for line in sys.stdin: 
            process_line(line)
    
    # process each file in the list 
    if files: 
        for file in files:
            if file == '-':
                continue
            try: 
                with open(file, 'r') as f: 
                    for line in f: 
                        process_line(line)
            except FileNotFoundError: 
                print(f"Error: {file} not found", file = sys.stderr)


if __name__ == "__main__":
    number_lines = '-n' in sys.argv
    number_nonblank = '-b' in sys.argv
    files = []
    for arg in sys.argv[1:]:
        if arg != '-n' and arg != '-b':
            files.append(arg)

    if number_lines and number_nonblank:
        print("Error: Cannot use both -n and -b options", file=sys.stderr)
        sys.exit(1)

    cccat(files, number_lines = number_lines, number_nonblank = number_nonblank)