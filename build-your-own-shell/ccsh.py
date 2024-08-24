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
        print(f"cd: not a directory path")

def print_working_directory():
    # step 5: pwd built-in command 
    print(os.getcwd())

def execute_command(command_parts):
    # handle pipes by splitting on '|' and chaining commands
    if '|' in command_parts:
        commands = [cmd.strip() for cmd in ' '.join(command_parts).split('|')]

        previous_process = None 

        for cmd in commands: 
            # split each command string into a list of arguments for Popen
            cmd_args = shlex.split(cmd)

            if previous_process is None: 
                # first command 
                previous_process = subprocess.Popen(cmd_args, stdout=subprocess.PIPE)
            else: 
                # subsequent commands 
                previous_process = subprocess.Popen(cmd_args, stdin=previous_process.stdout, stdout=subprocess.PIPE)
        
        # wait for the last process in the pipeline to finish 
        output, error = previous_process.communicate()
        if output:
            print(output.decode())
        if error:
            print(error.decode())
    else: 
        try:
            # Run external command without pipes
            subprocess.run(command_parts, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
        except FileNotFoundError:
            # Step 3: Handle non-existent commands
            print(f"No such file or directory (os error {errno.ENOENT})")

def main():
    prompt = "ccsh> "

    # Step 2: Loop to handle multiple commands
    while True:
        # Step 1: Prompt display and get user input, trim whitespace
        user_input = input(prompt).strip()

        # Step 1 & 4: Parse input into command and arguments
        command_parts = shlex.split(user_input)

        if not command_parts:
            continue

        command = command_parts[0].lower()
        args = command_parts[1:]

        if command == "exit":
            break
        # Step 5: Change directory
        elif command == "cd":
            change_directory(args[0] if args else os.path.expanduser("~"))
        # Step 5: Print working directory
        elif command == "pwd":
            print_working_directory()
        else:
            execute_command(command_parts)

if __name__ == "__main__":
    main()


