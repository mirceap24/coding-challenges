from flask import Flask, request, jsonify
from time import time
import threading

app = Flask(__name__)

class SlidingWindowRateLimiter:
    def __init__(self, window_size, request_limit):
        self.window_size = window_size
        self.request_limit = request_limit
        self.request_logs = {}
        self.lock = threading.Lock()

    def prune_old_requests(self, log, current_time):
        """
        Removes log entries older than the sliding window.
        """
        while log and log[0] < current_time - self.window_size:
            log.pop(0)

    def allow_request(self, ip):
        current_time = time()

        with self.lock:
            if ip not in self.request_logs:
                self.request_logs[ip] = []
            
            log = self.request_logs[ip]

            # Prune any old requests that are outside the current window
            self.prune_old_requests(log, current_time)

            # Check if the request limit has been reached within the current window
            if len(log) < self.request_limit:
                log.append(current_time)
                return True
            else:
                return False

# Initialize the rate limiter with desired window size and request limit
WINDOW_SIZE = 60  # 60 seconds
REQUEST_LIMIT = 10  # 10 requests per window

rate_limiter = SlidingWindowRateLimiter(WINDOW_SIZE, REQUEST_LIMIT)

@app.route('/limited', methods=['GET'])
def limited():
    ip = request.remote_addr

    if rate_limiter.allow_request(ip):
        return "Request allowed", 200
    else:
        return jsonify({"error": "Too many requests"}), 429

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
