#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <sys/stat.h>
#include <errno.h>
#include <limits.h>
#include <ctype.h>

#define PORT 8080
#define BUFFER_SIZE 1024
#define MAX_QUEUE_SIZE 100
#define MAX_PATH_LENGTH 1024

typedef enum {
    FIFO,
    SFF
} SchedulingPolicy;

typedef struct {
    int client_socket;
    char path[MAX_PATH_LENGTH];
    off_t file_size;
} Request;

typedef struct {
    Request queue[MAX_QUEUE_SIZE];
    int size;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
    SchedulingPolicy policy;
} RequestQueue;

RequestQueue request_queue = {
    .size = 0,
    .mutex = PTHREAD_MUTEX_INITIALIZER,
    .not_empty = PTHREAD_COND_INITIALIZER,
    .not_full = PTHREAD_COND_INITIALIZER,
    .policy = FIFO
};

void error(const char *msg) {
    perror(msg);
    exit(EXIT_FAILURE);
}

int compare_requests(const void *a, const void *b) {
    const Request *req1 = (const Request *)a;
    const Request *req2 = (const Request *)b;
    return req1->file_size - req2->file_size;
}

void send_response(int client_socket, const char *status, const char *content_type, const char *content, size_t content_length) {
    char header[BUFFER_SIZE];
    int header_length = snprintf(header, sizeof(header),
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %zu\r\n"
        "\r\n",
        status, content_type, content_length);

    if (send(client_socket, header, header_length, 0) < 0 ||
        send(client_socket, content, content_length, 0) < 0) {
        perror("Failed to send response");
    }
}

char* sanitize_path(const char* path) {
    char full_path[4096];
    snprintf(full_path, sizeof(full_path), "www%s", path);

    char* real_path = realpath(full_path, NULL);
    if (real_path == NULL) {
        return NULL;
    }
    
    char* www_dir = realpath("www", NULL);
    if (www_dir == NULL) {
        free(real_path);
        return NULL;
    }
    
    if (strncmp(real_path, www_dir, strlen(www_dir)) != 0) {
        free(real_path);
        free(www_dir);
        return NULL;
    }
    
    free(www_dir);
    return real_path;
}

void handle_client(int client_socket, const char *path) {
    char *safe_path = sanitize_path(path);
    if (safe_path == NULL) {
        const char *forbidden_content = "<html><body><h1>403 Forbidden</h1></body></html>";
        send_response(client_socket, "403 Forbidden", "text/html", forbidden_content, strlen(forbidden_content));
        close(client_socket);
        return;
    }

    if (strcmp(path, "/") == 0) {
        free(safe_path);
        safe_path = sanitize_path("/index.html");
        if (safe_path == NULL) {
            const char *not_found_content = "<html><body><h1>404 Not Found</h1></body></html>";
            send_response(client_socket, "404 Not Found", "text/html", not_found_content, strlen(not_found_content));
            close(client_socket);
            return;
        }
    }

    if (access(safe_path, F_OK) != 0) {
        const char *not_found_content = "<html><body><h1>404 Not Found</h1></body></html>";
        send_response(client_socket, "404 Not Found", "text/html", not_found_content, strlen(not_found_content));
        free(safe_path);
        close(client_socket);
        return;
    }

    FILE *file = fopen(safe_path, "rb");
    if (!file) {
        const char *not_found_content = "<html><body><h1>404 Not Found</h1></body></html>";
        send_response(client_socket, "404 Not Found", "text/html", not_found_content, strlen(not_found_content));
    } else {
        fseek(file, 0, SEEK_END);
        long file_size = ftell(file);
        rewind(file);

        char *buffer = malloc(file_size);
        if (!buffer) {
            fclose(file);
            free(safe_path);
            error("Memory allocation failed");
        }

        if (fread(buffer, 1, file_size, file) != (size_t)file_size) {
            free(buffer);
            fclose(file);
            free(safe_path);
            error("File read failed");
        }

        fclose(file);
        send_response(client_socket, "200 OK", "text/html", buffer, file_size);
        free(buffer);
    }

    free(safe_path);
    close(client_socket);
}

void add_request_to_queue(int client_socket, const char *path) {
    pthread_mutex_lock(&request_queue.mutex);

    while (request_queue.size == MAX_QUEUE_SIZE) {
        pthread_cond_wait(&request_queue.not_full, &request_queue.mutex);
    }

    Request req = { .client_socket = client_socket, .file_size = 0 };
    strncpy(req.path, path, sizeof(req.path) - 1);
    req.path[sizeof(req.path) - 1] = '\0';

    struct stat file_stat;
    char *safe_path = sanitize_path(path);
    if (safe_path != NULL && stat(safe_path, &file_stat) == 0) {
        req.file_size = file_stat.st_size;
        free(safe_path);
    }

    request_queue.queue[request_queue.size++] = req;

    pthread_cond_signal(&request_queue.not_empty);
    pthread_mutex_unlock(&request_queue.mutex);
}

void *worker_thread(void *arg) {
    while (1) {
        pthread_mutex_lock(&request_queue.mutex);

        while (request_queue.size == 0) {
            pthread_cond_wait(&request_queue.not_empty, &request_queue.mutex);
        }

        Request request;
        if (request_queue.policy == FIFO) {
            request = request_queue.queue[0];
            memmove(&request_queue.queue[0], &request_queue.queue[1], (request_queue.size - 1) * sizeof(Request));
        } else {
            qsort(request_queue.queue, request_queue.size, sizeof(Request), compare_requests);
            request = request_queue.queue[0];
            memmove(&request_queue.queue[0], &request_queue.queue[1], (request_queue.size - 1) * sizeof(Request));
        }

        request_queue.size--;

        pthread_cond_signal(&request_queue.not_full);
        pthread_mutex_unlock(&request_queue.mutex);

        handle_client(request.client_socket, request.path);
    }

    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <number_of_workers> <scheduling_policy>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    int num_workers = atoi(argv[1]);
    if (num_workers <= 0) {
        error("Invalid number of workers");
    }

    if (strcmp(argv[2], "FIFO") == 0) {
        request_queue.policy = FIFO;
    } else if (strcmp(argv[2], "SFF") == 0) {
        request_queue.policy = SFF;
    } else {
        error("Invalid scheduling policy. Use 'FIFO' or 'SFF'.");
    }

    int server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == -1) {
        error("Socket creation failed");
    }

    struct sockaddr_in server_addr = {
        .sin_family = AF_INET,
        .sin_addr.s_addr = INADDR_ANY,
        .sin_port = htons(PORT)
    };

    if (bind(server_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        close(server_socket);
        error("Bind failed");
    }

    if (listen(server_socket, 10) < 0) {
        close(server_socket);
        error("Listen failed");
    }

    printf("Server is listening on port %d with %d worker threads...\n", PORT, num_workers);

    pthread_t worker_threads[num_workers];
    for (int i = 0; i < num_workers; i++) {
        if (pthread_create(&worker_threads[i], NULL, worker_thread, NULL) != 0) {
            error("Failed to create worker thread");
        }
    }

    while (1) {
        struct sockaddr_in client_addr;
        socklen_t client_addr_len = sizeof(client_addr);
        int client_socket = accept(server_socket, (struct sockaddr *)&client_addr, &client_addr_len);
        if (client_socket < 0) {
            perror("Failed to accept connection");
            continue;
        }

        char buffer[BUFFER_SIZE];
        ssize_t bytes_received = recv(client_socket, buffer, sizeof(buffer) - 1, 0);
        if (bytes_received < 0) {
            perror("Failed to receive");
            close(client_socket);
            continue;
        }
        buffer[bytes_received] = '\0';

        char method[8], path[MAX_PATH_LENGTH], version[16];
        if (sscanf(buffer, "%7s %1023s %15s", method, path, version) != 3) {
            fprintf(stderr, "Failed to parse request\n");
            close(client_socket);
            continue;
        }

        add_request_to_queue(client_socket, path);
    }

    close(server_socket);
    return 0;
}