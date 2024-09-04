#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>  // For socket functions
#include <pthread.h>    // For multi-threading
#include <sys/stat.h>   // For file existence check
#include <fcntl.h>      // For file operations

#define PORT 8080
#define LOCALHOST "127.0.0.1"
#define WWW_DIR "www"   // directory where HTML files are stored
#define MAX_QUEUE_SIZE 10   // Maximum number of pending connections in the queue
#define WORKER_THREADS 10   // Number of worker threads

void *worker_thread(void *arg);
void serve_file(int client_socket, const char *file_path);
void send_404(int client_socket);

// Shared task queue and synchronization structures
int client_queue[MAX_QUEUE_SIZE];
int queue_count = 0;
int queue_front = 0;
int queue_rear = 0;

pthread_mutex_t queue_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond_producer = PTHREAD_COND_INITIALIZER;
pthread_cond_t cond_consumer = PTHREAD_COND_INITIALIZER;

// Function to enqueue a client socket
void enqueue(int client_socket) {
    pthread_mutex_lock(&queue_mutex);
    
    while (queue_count == MAX_QUEUE_SIZE) {
        // Wait if the queue is full
        pthread_cond_wait(&cond_producer, &queue_mutex);
    }

    client_queue[queue_rear] = client_socket;
    queue_rear = (queue_rear + 1) % MAX_QUEUE_SIZE;
    queue_count++;

    pthread_cond_signal(&cond_consumer);
    pthread_mutex_unlock(&queue_mutex);
}

// Function to dequeue a client socket
int dequeue() {
    pthread_mutex_lock(&queue_mutex);

    while (queue_count == 0) {
        // Wait if the queue is empty
        pthread_cond_wait(&cond_consumer, &queue_mutex);
    }

    int client_socket = client_queue[queue_front];
    queue_front = (queue_front + 1) % MAX_QUEUE_SIZE;
    queue_count--;

    pthread_cond_signal(&cond_producer);
    pthread_mutex_unlock(&queue_mutex);

    return client_socket;
}

int main() {
    // Create worker threads
    pthread_t workers[WORKER_THREADS];
    for (int i = 0; i < WORKER_THREADS; i++) {
        pthread_create(&workers[i], NULL, worker_thread, NULL);
    }

    // Create the server socket
    int server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == -1) {
        perror("Could not create socket");
        return 1;
    }

    // Bind the socket to an IP/port
    struct sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = inet_addr(LOCALHOST);
    server_address.sin_port = htons(PORT);

    if (bind(server_socket, (struct sockaddr*)&server_address, sizeof(server_address)) < 0) {
        perror("Bind failed");
        return 1;
    }

    // Start listening for connections
    if (listen(server_socket, 10) < 0) {
        perror("Listen failed");
        return 1;
    }

    // Accept connections and enqueue them for worker threads
    int client_socket;
    struct sockaddr_in client_address;
    socklen_t client_len = sizeof(client_address);

    while (1) {
        client_socket = accept(server_socket, (struct sockaddr*)&client_address, &client_len);
        if (client_socket < 0) {
            perror("Accept failed");
            continue;
        }

        // Enqueue the client socket for the worker threads to process
        enqueue(client_socket);
    }

    close(server_socket);
    return 0;
}

// Worker thread function that handles client requests
void *worker_thread(void *arg) {
    while (1) {
        // Dequeue a client socket
        int client_socket = dequeue();

        // Receive data from client
        char request_buffer[1024];
        ssize_t bytes_received = recv(client_socket, request_buffer, sizeof(request_buffer) - 1, 0);
        if (bytes_received < 0) {
            perror("Receive failed");
            close(client_socket);
            continue;
        }
        request_buffer[bytes_received] = '\0';

        // Parse request to extract the requested path
        char method[10], path[1024], http_version[10];
        sscanf(request_buffer, "%s %s %s", method, path, http_version);

        // If path is "/", serve "index.html"
        if (strcmp(path, "/") == 0) {
            strcpy(path, "/index.html");
        }

        // Serve the file if it exists, otherwise send 404
        char file_path[2048];
        snprintf(file_path, sizeof(file_path), "%s%s", WWW_DIR, path); // concatenate "www" and the requested path

        struct stat st;
        if (stat(file_path, &st) == 0) {
            // File exists, serve it
            serve_file(client_socket, file_path);
        } else {
            // File does not exist, send 404 not Found
            send_404(client_socket);
        }

        close(client_socket);  // Close the connection after processing
    }
    return NULL;
}

// Function to serve a file
void serve_file(int client_socket, const char *file_path) {
    // Open the requested file
    FILE *file = fopen(file_path, "r");
    if (file == NULL) {
        // If file can't be opened, send 404 error
        send_404(client_socket);
        return;
    }

    // Send HTTP 200 OK header (before sending the file content)
    char response[] = "HTTP/1.1 200 OK\r\n"
                      "Content-Type: text/html\r\n"
                      "Connection: close\r\n"
                      "\r\n";
    send(client_socket, response, strlen(response), 0);

    // Read and send the file contents
    char file_buffer[1024];
    size_t bytes_read;
    while ((bytes_read = fread(file_buffer, 1, sizeof(file_buffer), file)) > 0) {
        send(client_socket, file_buffer, bytes_read, 0);
    }

    // Close the file after serving
    fclose(file);
}

// Function to send a 404 Not Found response
void send_404(int client_socket) {
    // Send HTTP 404 header and response
    char response[] = "HTTP/1.1 404 Not Found\r\n"
                      "Content-Type: text/html\r\n"
                      "Connection: close\r\n"
                      "\r\n";
    send(client_socket, response, strlen(response), 0);
}
