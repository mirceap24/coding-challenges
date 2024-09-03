from flask import Flask, request, jsonify 
from time import time 
import threading 

app = Flask(__name__)

# Sliding window parameters 
WINDOW_SIZE = 60 # window size in seconds 
REQUEST_LIMIT = 10 # max number of requests allowed in the window 

request_logs = {}
lock = threading.Lock()

def prune_old_requests(log, current_time):
    """
    Removes log entries older than the sliding window
    """
    while log and log[0] < current_time - WINDOW_SIZE: 
        log.pop(0)

def allow_request(ip):
    current_time = time()

    with lock: 
        if ip not in request_logs: 
            request_logs[ip] = []
        
        log = request_logs[ip]
        
        # prune any old requests that are outside the current window 
        prune_old_requests(log, current_time)

        # check if the request limit has been reached within the current window 
        if len(log) < REQUEST_LIMIT: 
            log.append(current_time)
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
