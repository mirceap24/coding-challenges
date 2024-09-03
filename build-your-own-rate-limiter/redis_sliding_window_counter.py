from flask import Flask, request, jsonify
from time import time
from math import floor
import redis

app = Flask(__name__)

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Sliding window counter parameters
WINDOW_SIZE = 60  # Window size in seconds
REQUEST_LIMIT = 10  # Maximum number of requests allowed in the window

def get_current_window_start():
    current_time = time()
    return floor(current_time / WINDOW_SIZE) * WINDOW_SIZE

def get_weighted_count(ip):
    """
    Calculate the weighted count of requests using the current and previous window.
    """
    current_time = time()
    current_window_start = get_current_window_start()
    elapsed_time_in_current_window = current_time - current_window_start
    current_window_weight = elapsed_time_in_current_window / WINDOW_SIZE
    previous_window_weight = 1 - current_window_weight

    # Use Redis pipeline for atomic operations
    with redis_client.pipeline() as pipe:
        # Get current and previous counts
        current_key = f"{ip}:{current_window_start}"
        previous_key = f"{ip}:{current_window_start - WINDOW_SIZE}"
        
        pipe.get(current_key)
        pipe.get(previous_key)
        current_count, previous_count = pipe.execute()

        # Convert to integers, default to 0 if None
        current_count = int(current_count or 0)
        previous_count = int(previous_count or 0)

        # Calculate weighted count
        weighted_count = (
            current_count * current_window_weight +
            previous_count * previous_window_weight
        )

        return weighted_count, current_key

def allow_request(ip):
    """
    Determines if a request from a specific IP should be allowed based on the sliding window counter algorithm.
    """
    weighted_count, current_key = get_weighted_count(ip)

    if weighted_count < REQUEST_LIMIT:
        # Use Redis to atomically increment and get the new count
        new_count = redis_client.incr(current_key)
        redis_client.expire(current_key, WINDOW_SIZE * 2)  # Keep for current and next window
        
        # Double-check after incrementing
        if new_count <= REQUEST_LIMIT:
            return True
        else:
            # If we've exceeded the limit, decrement the count
            redis_client.decr(current_key)
            return False
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
    import sys
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8080
    app.run(host='127.0.0.1', port=port)

