# The algorithm divides time into fixed intervals 
# For each window, the number of requests made during that window is counted 
# The algorithm tracks the number of requests in both the current window and the immediately preceding window 
# The rate limiter uses a weighted average of the counts from the current and previous windows
# The weight dependes on how far you are into the current window. For example
    ## if you're 30% into the current window, the previous window's count will contribute 70% to the overall
    ## count, and the current window's count will contribute 30%
# If the weighted average exceeds the predefined limit, the request is denied

from flask import Flask, request, jsonify
from time import time
from math import floor
import threading

app = Flask(__name__)

# Sliding window counter parameters
WINDOW_SIZE = 60  # Window size in seconds
REQUEST_LIMIT = 10  # Maximum number of requests allowed in the window

request_counters = {}
lock = threading.Lock()

def get_current_window_start():
    current_time = time()
    return floor(current_time / WINDOW_SIZE) * WINDOW_SIZE

def get_weighted_count(ip):
    """
    Calculate the weighted count of requests using the current and previous window.
    """
    current_time = time()
    current_window_start = get_current_window_start()
    ellapsed_time_in_current_window = current_time - current_window_start
    current_window_weight = ellapsed_time_in_current_window / WINDOW_SIZE
    previous_window_weight = 1 - current_window_weight

    with lock: 
        if ip not in request_counters: 
            request_counters[ip] = {
                "current_window_start": current_window_start,
                "current_count": 0,
                "previous_count": 0
            }

        counter = request_counters[ip]

        # new window, shift counts 
        if counter["current_window_start"] != current_window_start: 
            counter["previous_count"] = counter["current_count"]
            counter["current_count"] = 0
            counter["current_window_start"] = current_window_start
        
        # weighted sum of the current and previous windows 
        weighted_count = (
            counter["current_count"] * current_window_weight +
            counter["previous_count"] * previous_window_weight
        )

        return weighted_count

def allow_request(ip):
    """
    Determines if a request from a specific IP should be allowed based on the sliding window counter algorithm.
    """
    weighted_count = get_weighted_count(ip)

    if weighted_count < REQUEST_LIMIT: 
        with lock: 
            request_counters[ip]["current_count"] += 1 
            return True 
    else: 
        return False 
    
@app.route('/limited', methods=['GET'])
def limited():
    ip = request.remote_addr 
    
    if allow_request(ip):
        return "Request allowed", 200
    else:
        return jsonify({"error": "Too many requests"}), 429
    

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)

