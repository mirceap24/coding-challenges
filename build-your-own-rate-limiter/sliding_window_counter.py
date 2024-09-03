from flask import Flask, request, jsonify
from time import time
from math import floor
import threading

app = Flask(__name__)

class SlidingWindowRateLimiter:
    def __init__(self, window_size, request_limit):
        self.window_size = window_size
        self.request_limit = request_limit
        self.request_counters = {}
        self.lock = threading.Lock()

    def get_current_window_start(self):
        current_time = time()
        return floor(current_time / self.window_size) * self.window_size

    def get_weighted_count(self, ip):
        """
        Calculate the weighted count of requests using the current and previous window.
        """
        current_time = time()
        current_window_start = self.get_current_window_start()
        elapsed_time_in_current_window = current_time - current_window_start
        current_window_weight = elapsed_time_in_current_window / self.window_size
        previous_window_weight = 1 - current_window_weight

        with self.lock:
            if ip not in self.request_counters:
                self.request_counters[ip] = {
                    "current_window_start": current_window_start,
                    "current_count": 0,
                    "previous_count": 0
                }

            counter = self.request_counters[ip]

            # New window, shift counts
            if counter["current_window_start"] != current_window_start:
                counter["previous_count"] = counter["current_count"]
                counter["current_count"] = 0
                counter["current_window_start"] = current_window_start

            # Weighted sum of the current and previous windows
            weighted_count = (
                counter["current_count"] * current_window_weight +
                counter["previous_count"] * previous_window_weight
            )

            return weighted_count

    def allow_request(self, ip):
        """
        Determines if a request from a specific IP should be allowed based on the sliding window counter algorithm.
        """
        weighted_count = self.get_weighted_count(ip)

        if weighted_count < self.request_limit:
            with self.lock:
                self.request_counters[ip]["current_count"] += 1
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
