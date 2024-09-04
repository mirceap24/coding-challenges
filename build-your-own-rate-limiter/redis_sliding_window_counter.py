import time
import redis
from flask import Flask, request, jsonify

# Create a Flask app instance
app = Flask(__name__)

# Create a Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

class DistributedSlidingWindowCounterRateLimiter: 
    def __init__(self, window_size, max_requests):
        self.window_size = window_size
        self.max_requests = max_requests

    def get_current_window(self):
        return int(time.time() // self.window_size)
    
    def is_request_allowed(self, ip):
        current_time = time.time()
        current_window = self.get_current_window()

        # Keys for the current and previous windows
        current_key = f"{ip}:{current_window}"
        previous_key = f"{ip}:{current_window - 1}"

        pipe = redis_client.pipeline()

        # Increment the counter for the current window
        pipe.incr(current_key)
        pipe.expire(current_key, self.window_size * 2)

        # Get the count from the previous window
        pipe.get(previous_key)

        current_count, _, previous_count = pipe.execute()

        # Convert previous_count to int, default to 0 if None
        previous_count = int(previous_count or 0)

        # Calculate the weight of the previous window
        time_passed_in_window = current_time % self.window_size
        weight = 1 - (time_passed_in_window / self.window_size)

        # Calculate the weighted sum of requests
        weighted_count = previous_count * weight + current_count
        
        # Check if the weighted count exceeds the limit
        if weighted_count > self.max_requests:
            return False
        return True

# Sliding window parameters
WINDOW_SIZE = 60   # Window size in seconds
MAX_REQUESTS = 60  # Maximum allowed requests in the sliding window

# Instantiate the rate limiter with the defined parameters
rate_limiter = DistributedSlidingWindowCounterRateLimiter(WINDOW_SIZE, MAX_REQUESTS)

@app.route('/limited')
def sliding_window_counter_limited():
    ip = request.remote_addr
    if rate_limiter.is_request_allowed(ip):
        return "Request succeeded!"
    else:
        return jsonify({"error": "Too many requests"}), 429

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8080
    app.run(host='127.0.0.1', port=port)