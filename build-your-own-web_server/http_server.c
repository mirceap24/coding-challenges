#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <sys/stat.h>

#define PORT 8080
#define BUFFER_SIZE 1024
#define QUEUE_SIZE 10
#define THREAD_POOL_SIZE 5

// Circular queue to hold client socket file descriptors
typedef struct {
    int clients[QUEUE_SIZE];
    int front;
    int rear;
    int count;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty;  // Condition variable to signal when the queue is not empty
    pthread_cond_t not_full;   // Condition variable to signal when the queue is not full
} client_queue_t;

client_queue_t queue = {
    .front = 0,
    .rear = 0,
    .count = 0,
    .mutex = PTHREAD_MUTEX_INITIALIZER,
    .not_empty = PTHREAD_COND_INITIALIZER,
    .not_full = PTHREAD_COND_INITIALIZER
};

// Function to add a client to the queue
void enqueue(int client_fd) {
    pthread_mutex_lock(&queue.mutex);

    // Wait until the queue has space
    while (queue.count == QUEUE_SIZE) {
        pthread_cond_wait(&queue.not_full, &queue.mutex);
    }

    // Add client to the queue
    queue.clients[queue.rear] = client_fd;
    queue.rear = (queue.rear + 1) % QUEUE_SIZE;
    queue.count++;

    // Signal that the queue is not empty
    pthread_cond_signal(&queue.not_empty);
    pthread_mutex_unlock(&queue.mutex);
}

// Function to remove a client from the queue
int dequeue() {
    pthread_mutex_lock(&queue.mutex);

    // Wait until the queue has clients
    while (queue.count == 0) {
        pthread_cond_wait(&queue.not_empty, &queue.mutex);
    }

    // Remove client from the queue
    int client_fd = queue.clients[queue.front];
    queue.front = (queue.front + 1) % QUEUE_SIZE;
    queue.count--;

    // Signal that the queue is not full
    pthread_cond_signal(&queue.not_full);
    pthread_mutex_unlock(&queue.mutex);

    return client_fd;
}

// Function to serve the requested file to the client
void serve_file(int client_fd, const char *path) {
    FILE *file = fopen(path, "r");
    if (file == NULL) {
        // File not found, return 404
        const char *not_found = "HTTP/1.1 404 Not Found\r\n\r\n404 Not Found";
        write(client_fd, not_found, strlen(not_found));
    } else {
        // File found, send HTTP response with file contents
        const char *header = "HTTP/1.1 200 OK\r\n\r\n";
        write(client_fd, header, strlen(header));

        char file_buffer[BUFFER_SIZE];
        while (fgets(file_buffer, sizeof(file_buffer), file) != NULL) {
            write(client_fd, file_buffer, strlen(file_buffer));
        }
        fclose(file);
    }
}

// Worker function for threads to handle client requests
void *handle_client(void *arg) {
    while (1) {
        int client_fd = dequeue();

        char buffer[BUFFER_SIZE];
        read(client_fd, buffer, sizeof(buffer));
        printf("Received request:\n%s\n", buffer);

        // Parse the request line (assuming well-formed input)
        char method[16], path[1024], http_version[16];
        sscanf(buffer, "%s %s %s", method, path, http_version);

        // Handle root path as /index.html
        if (strcmp(path, "/") == 0) {
            strcpy(path, "./www/index.html");
        } else {
            // Construct the file path from the request
            char temp_path[1048];
            snprintf(temp_path, sizeof(temp_path), "./www%s", path);
            strcpy(path, temp_path);
        }

        // Serve the file if it exists
        serve_file(client_fd, path);

        close(client_fd);
    }
    return NULL;
}

int main() {
    int server_fd, client_fd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t addrlen = sizeof(client_addr);

    // Create socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    // Bind the socket to the port
    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Listen for incoming connections
    if (listen(server_fd, 3) < 0) {
        perror("Listen failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Create a pool of worker threads
    pthread_t thread_pool[THREAD_POOL_SIZE];
    for (int i = 0; i < THREAD_POOL_SIZE; i++) {
        pthread_create(&thread_pool[i], NULL, handle_client, NULL);
    }

    printf("Server is listening on port %d...\n", PORT);

    // Accept connections and enqueue them
    while (1) {
        client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &addrlen);
        if (client_fd < 0) {
            perror("Accept failed");
            continue;
        }
        enqueue(client_fd);  // Add client to the queue for workers to handle
    }

    
    close(server_fd);
    return 0;
}
