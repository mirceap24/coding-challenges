import subprocess
import shlex 
import errno 
import os
import signal
import readline 
import atexit

# Global variable to store the current child process
current_child_process = None
HISTORY_FILE = os.path.expanduser("~/.ccsh_history")
MAX_HISTORY_LINES = 1000

def setup_history():
    """
    Set up command history handling
    """
    if not os.path.exists(HISTORY_FILE):
        open(HISTORY_FILE, 'a').close()
    
    readline.read_history_file(HISTORY_FILE)
    readline.set_history_length(MAX_HISTORY_LINES)
    atexit.register(readline.write_history_file, HISTORY_FILE)

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

def display_history():
    """
    Display command history
    """
    for i in range(1, readline.get_current_history_length() + 1):
        command = readline.get_history_item(i)
        if command.strip().lower() != 'history':
            print(command)

def main():
    prompt = "ccsh> "

    # set up command history
    setup_history()

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
            elif command == "history":
                display_history()
            else:
                execute_command(command_parts)
        except EOFError:
            print("\nUse 'exit' to leave the shell.")

if __name__ == "__main__":
    main()