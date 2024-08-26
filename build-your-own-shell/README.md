## CCSH - Coding Challenges Shell 

CCSH is a lightweight, customizable command-line shell implemented in both Python and C. It provides a simple yet powerful interface for interacting with your operating system, supporting basic command execution, built-in commands, piping, and command history.

### Features 
* Custom Prompt: Easily recognizable `ccsh>` prompt 
* Command Execution: Run external commands with arguments 
* Built-in Commands: Supports `cd`, `pwd`, `exit` and `history` 
* Pipe Support: Chain commands using the `|` operator 
* Signal Handling: Handles interrupts (Ctrl + C)
    * When no child process is running, interrupts the current input line and displays a new prompt 
    * When a child process is running, it terminates the child process without exiting the shell 
* Command History: 
    * Saves history to `~/.ccsh_history`
    * Supports up/down arrow navigation 
    * `history` command to display past commands

### Feature Implementation Details 

#### 1. Command Execution
* Python: Uses the `subprocess` module to create and manage child processes
* C: Uses `fork()` and `execvp()` system calls to create child processes and execute commands 

#### 2. Built-in Commands 
Both versions implement `cd`, `pwd`, `exit`, and `history` as built-in commands.

#### 3. Pipe Support 
* Python: Uses `subprocess.Popen` with piped stdout and stdin to chain commands
* C: Implements piping using the `pipe()` system call and manually setting up file descriptores for each command in the pipeline 

#### 4. Signal Handling 
* Python: Uses the `signal` module to set up a custom signal handler 
* C: Uses the `signal()` function to register a custom signal handler for SIGINT 

#### 5. Command History 
* Python: Uses the `readline` module, which is a Python wrapper for GNU Readline 
* C: Directly uses the GNU Readline library functions like `read_history()`, `add_history()` and `write_history()`


### Usage 
```bash 
python3 ccsh.py 
```

```bash 
gcc -o ccsh ccsh.c -lreadline -lreadhistory
./ccsh
```

Once you start CCSH, you will see the prompt: 
```bash
ccsh>
```

You can now enter commands just like in any other shell. Here are some examples: 
```bash 
ccsh> ls
ccsh> pwd
ccsh> cd /path/to/directory
ccsh> cat file.txt | wc -l
ccsh> history
ccsh> exit
```