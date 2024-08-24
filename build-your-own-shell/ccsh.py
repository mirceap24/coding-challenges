import subprocess
import shlex 
import errno 
import os 

def change_directory(path):
    # step 5: cd built-in command 
    try: 
        os.chdir(path)
    except FileNotFoundError: 
        print(f"cd: no such file or directory: {path}")
    except NotADirectoryError: 
        print(f"cd: not a directory: {path}")

def print_working_directory():
    # step 5: pwd built-in command 
    print(os.getcwd())

def main():
    prompt = "ccsh> "

    # step 2: loop to handle multiple commands 
    while True: 
        # step 1: prompt display and get user input, trim whitespace 
        user_input = input(prompt).strip()

        # step 1 & 4: parse input in command and arguments 
        command_parts = shlex.split(user_input)

        if not command_parts: 
            continue 
        
        command = command_parts[0].lower()
        args = command_parts[1:]

        if command == "exit":
            break 
        # step 5: change directory
        elif command == "cd":
            change_directory(args[0] if args else os.path.expanduser("~"))
        # step 5: print working directory
        elif command == "pwd":
            print_working_directory()
        else: 
            try: 
                # run external command with arguments and wait for it to complete
                subprocess.run(command_parts, check = True)
            except subprocess.CalledProcessError as e: 
                print(f"Command failed with exit code {e.returncode}")
            except FileNotFoundError: 
                # step 3: non-existent commands 
                print(f"No such file or directory (os error {errno.ENOENT})")
    

if __name__ == "__main__":
    main()