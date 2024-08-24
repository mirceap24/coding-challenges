import subprocess
import shlex 
import errno 
import os
import signal

# Global variable to store the current child process
current_child_process = None

def signal_handler(sig, frame):
    global current_child_process
    if current_child_process:
        # If there's a child process running, terminate it
        current_child_process.terminate()
        current_child_process = None
    else: 
        print("\nccsh> ", end = '', flush = True)

def change_directory(path):
    try: 
        os.chdir(path)
    except FileNotFoundError: 
        print(f"cd: no such file or directory: {path}")
    except NotADirectoryError: 
        print(f"cd: not a directory: {path}")

def print_working_directory():
    print(os.getcwd())

def execute_command(command_parts):
    global current_child_process
    if '|' in command_parts: 
        commands = [cmd.strip() for cmd in ' '.join(command_parts).split('|')]
        processes = []
        for i, cmd in enumerate(commands):
            cmd_args = shlex.split(cmd)
            if i == 0: 
                processes.append(subprocess.Popen(cmd_args, stdout = subprocess.PIPE))
            elif i == len(commands) - 1: 
                processes.append(subprocess.Popen(cmd_args, stdin=processes[-1].stdout, stdout=subprocess.PIPE))
            else: 
                processes.append(subprocess.Popen(cmd_args, stdin=processes[-1].stdout, stdout=subprocess.PIPE))

        current_child_process = processes[-1]
        try: 
            output, error = current_child_process.communicate()
            if output: 
                print(output.decode().strip())
            if error: 
                print(error.decode().strip())
        finally:
            current_child_process = None
    else:
        try: 
            current_child_process = subprocess.Popen(command_parts)
            current_child_process.wait()
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
        except FileNotFoundError:
            print(f"No such file or directory (os error {errno.ENOENT})")
        finally:
            current_child_process = None

def main():
    prompt = "ccsh> "

    # custom signal handler
    signal.signal(signal.SIGINT, signal_handler)

    while True: 
        try: 
            user_input = input(prompt).strip()
            command_parts = shlex.split(user_input)
            if not command_parts: 
                continue 
            command = command_parts[0].lower()
            args = command_parts[1:]
            if command == "exit":
                break
            elif command == "cd":
                change_directory(args[0] if args else os.path.expanduser("~"))
            elif command == "pwd":
                print_working_directory()
            else:
                execute_command(command_parts)
        except EOFError:
            print("\nUse 'exit' to leave the shell.")

if __name__ == "__main__":
    main()