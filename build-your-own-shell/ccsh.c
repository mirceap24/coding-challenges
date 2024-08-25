#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include <sys/wait.h>
#include <readline/readline.h>
#include <readline/history.h>

#define MAX_COMMAND_LENGTH 1024
#define MAX_ARGS 64
#define HISTORY_FILE ".ccsh_history"
#define MAX_HISTORY_LINES 1000

pid_t current_child_process = 0;

void setup_history() {
    char *home = getenv("HOME");
    if (home) {
        char history_path[1024];
        snprintf(history_path, sizeof(history_path), "%s/%s", home, HISTORY_FILE);
        
        FILE *file = fopen(history_path, "a");
        if (file) fclose(file);
        
        read_history(history_path);
        stifle_history(MAX_HISTORY_LINES);
    }
}

void save_history() {
    char *home = getenv("HOME");
    if (home) {
        char history_path[1024];
        snprintf(history_path, sizeof(history_path), "%s/%s", home, HISTORY_FILE);
        write_history(history_path);
    }
}

void signal_handler(int sig) {
    if (current_child_process) {
        kill(current_child_process, SIGTERM);
        current_child_process = 0;
    } else {
        printf("\nccsh> ");
        fflush(stdout);
    }
}

void change_directory(const char *path) {
    if (chdir(path) != 0) {
        perror("cd");
    }
}

void print_working_directory() {
    char cwd[1024];
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        printf("%s\n", cwd);
    } else {
        perror("pwd");
    }
}

void execute_command(char **args) {
    pid_t pid = fork();
    
    if (pid == 0) {
        // Child process
        execvp(args[0], args);
        fprintf(stderr, "%s: No such file or directory (os error %d)\n", args[0], ENOENT);
        exit(EXIT_FAILURE);
    } else if (pid > 0) {
        // Parent process
        current_child_process = pid;
        int status;
        waitpid(pid, &status, 0);
        current_child_process = 0;
    } else {
        perror("fork");
    }
}

void execute_piped_commands(char **commands, int num_commands) {
    int pipes[num_commands - 1][2];
    pid_t pids[num_commands];

    for (int i = 0; i < num_commands - 1; i++) {
        if (pipe(pipes[i]) == -1) {
            perror("pipe");
            return;
        }
    }

    for (int i = 0; i < num_commands; i++) {
        pids[i] = fork();

        if (pids[i] == 0) {
            // Child process
            if (i > 0) {
                dup2(pipes[i-1][0], STDIN_FILENO);
            }
            if (i < num_commands - 1) {
                dup2(pipes[i][1], STDOUT_FILENO);
            }

            for (int j = 0; j < num_commands - 1; j++) {
                close(pipes[j][0]);
                close(pipes[j][1]);
            }

            char *args[MAX_ARGS];
            int arg_count = 0;
            char *token = strtok(commands[i], " ");
            while (token != NULL && arg_count < MAX_ARGS - 1) {
                args[arg_count++] = token;
                token = strtok(NULL, " ");
            }
            args[arg_count] = NULL;

            execvp(args[0], args);
            fprintf(stderr, "%s: command not found\n", args[0]);
            exit(EXIT_FAILURE);
        } else if (pids[i] < 0) {
            perror("fork");
            return;
        }
    }

    for (int i = 0; i < num_commands - 1; i++) {
        close(pipes[i][0]);
        close(pipes[i][1]);
    }

    for (int i = 0; i < num_commands; i++) {
        waitpid(pids[i], NULL, 0);
    }
}

void display_history() {
    HIST_ENTRY **history = history_list();
    if (history) {
        for (int i = 0; history[i]; i++) {
            if (strcmp(history[i]->line, "history") != 0) {
                printf("%s\n", history[i]->line);
            }
        }
    }
}

int main() {
    setup_history();
    signal(SIGINT, signal_handler);

    char *input;
    char *args[MAX_ARGS];

    while (1) {
        input = readline("ccsh> ");

        if (!input) {
            printf("\nUse 'exit' to leave the shell.\n");
            continue;
        }

        if (strlen(input) > 0) {
            add_history(input);

            if (strcmp(input, "exit") == 0) {
                free(input);
                break;
            } else if (strncmp(input, "cd", 2) == 0) {
                char *path = input + 3;
                if (strlen(path) == 0) {
                    path = getenv("HOME");
                }
                change_directory(path);
            } else if (strcmp(input, "pwd") == 0) {
                print_working_directory();
            } else if (strcmp(input, "history") == 0) {
                display_history();
            } else {
                if (strchr(input, '|')) {
                    char *commands[MAX_ARGS];
                    int num_commands = 0;
                    char *token = strtok(input, "|");
                    while (token != NULL && num_commands < MAX_ARGS) {
                        commands[num_commands++] = token;
                        token = strtok(NULL, "|");
                    }
                    execute_piped_commands(commands, num_commands);
                } else {
                    int arg_count = 0;
                    char *token = strtok(input, " ");
                    while (token != NULL && arg_count < MAX_ARGS - 1) {
                        args[arg_count++] = token;
                        token = strtok(NULL, " ");
                    }
                    args[arg_count] = NULL;
                    execute_command(args);
                }
            }
        }

        free(input);
    }

    save_history();
    return 0;
}