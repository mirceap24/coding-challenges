from flask import Flask, request, jsonify
from time import time
from math import floor
import redis

app = Flask(__name__)

class SlidingWindowRateLimiter:
    def __init__(self, redis_client, window_size, request_limit):
        self.redis_client = redis_client
        self.window_size = window_size
        self.request_limit = request_limit

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

        # Use Redis pipeline for atomic operations
        with self.redis_client.pipeline() as pipe:
            # Get current and previous counts
            current_key = f"{ip}:{current_window_start}"
            previous_key = f"{ip}:{current_window_start - self.window_size}"
            
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

    def allow_request(self, ip):
        """
        Determines if a request from a specific IP should be allowed based on the sliding window counter algorithm.
        """
        weighted_count, current_key = self.get_weighted_count(ip)

        if weighted_count < self.request_limit:
            # Use Redis to atomically increment and get the new count
            new_count = self.redis_client.incr(current_key)
            self.redis_client.expire(current_key, self.window_size * 2)  # Keep for current and next window
            
            # Double-check after incrementing
            if new_count <= self.request_limit:
                return True
            else:
                # If we've exceeded the limit, decrement the count
                self.redis_client.decr(current_key)
                return False
        else:
            return False

# Initialize Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Initialize the rate limiter with desired window size and request limit
WINDOW_SIZE = 60  # 60 seconds
REQUEST_LIMIT = 10  # 10 requests per window

rate_limiter = SlidingWindowRateLimiter(redis_client, WINDOW_SIZE, REQUEST_LIMIT)

@app.route('/limited', methods=['GET'])
def limited():
    ip = request.remote_addr
    
    if rate_limiter.allow_request(ip):
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
