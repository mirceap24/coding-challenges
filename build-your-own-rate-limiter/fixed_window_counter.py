# This algorithm tracks the number of requests in fixed time windows (e.g, 60-second windows)
# and limits the number of requests that can be made within each window

from math import floor
from flask import Flask, request, jsonify, make_response
from time import time 
import threading 

app = Flask(__name__)

# Fixed window parameters 
WINDOW_SIZE = 60 
REQUEST_LIMIT = 60 # 60 requests per window
request_counters = {}
lock = threading.Lock()

def get_window_start_time():
    """
    Returns the start time of the current window
    """
    current_time = time()
    return floor(current_time / WINDOW_SIZE) * WINDOW_SIZE

def allow_request(ip):
    current_window = get_window_start_time()

    with lock: # thread safe access to request_counters
        if ip not in request_counters:
            request_counters[ip] = {"window": current_window, "count": 0}
        
        counter = request_counters[ip]

        # if the request is in a new window, reset the counter 
        if counter["window"] != current_window: 
            counter["window"] = current_window
            counter["count"] = 0 
        
        # increment the counter and check if the request is allowed 
        if counter["count"] < REQUEST_LIMIT: 
            counter["count"] += 1 
            return True 
        else: 
            return False 
        

@app.route('/unlimited', methods=['GET'])
def unlimited():
    return "Unlimited! Let's Go!", 200

@app.route('/limited', methods=['GET'])
def limited():
    ip = request.remote_addr

    if allow_request(ip):
        return "Limited, don't over use me!", 200
    else:
        return jsonify({"error": "Too many requests"}), 429

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)