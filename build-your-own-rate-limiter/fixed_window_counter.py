# This algorithm tracks the number of requests in fixed time windows (e.g, 60-second windows)
# and limits the number of requests that can be made within each window

from math import floor 
from flask import Flask, request, jsonify 
from time import time 
import threading 

app = Flask(__name__)

class FixedWindowRateLimiter: 
    def __init__(self, window_size, request_limit):
        self.window_size = window_size 
        self.request_limit = request_limit
        self.request_counters = {}
        self.lock = threading.Lock()
    
    def get_window_start_time(self):
        """
        Returns the start time of the current window.
        """
        current_time = time()
        return floor(current_time / self.window_size) * self.window_size
    
    def allow_request(self, ip):
        """
        Determines if a request is allowed based on the current window and the request limit.
        """
        current_window = self.get_window_start_time()

        with self.lock: 
            if ip not in self.request_counters: 
                self.request_counters[ip] = {"window": current_window, "count": 0}
            
            counter = self.request_counters[ip]

            # if the request is in a new window, reset counter 
            if counter["window"] != current_window: 
                counter["window"] = current_window
                counter["count"] = 0 
            
            # increment counter and check if the request is allowed 
            if counter["count"] < self.request_limit: 
                counter["count"] += 1 
                return True 
            else: 
                return False

# Initialize the FixedWindowRateLimiter with the desired window size and request limit
WINDOW_SIZE = 60  # 60 seconds window
REQUEST_LIMIT = 60  # 60 requests per window

rate_limiter = FixedWindowRateLimiter(WINDOW_SIZE, REQUEST_LIMIT)

@app.route('/unlimited', methods=['GET'])
def unlimited():
    return "Unlimited! Let's Go!", 200

@app.route('/limited', methods=['GET'])
def limited():
    ip = request.remote_addr

    if rate_limiter.allow_request(ip):
        return "Limited, don't overuse me!", 200
    else:
        return jsonify({"error": "Too many requests"}), 429

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)