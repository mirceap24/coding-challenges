import time
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

class RateLimiter: 
    def __init__(self, bucket_capacity, token_rate):
        """
        Initialize the RateLimiter with a bucket capacity and token refill rate.

        Args:
        - bucket_capacity: Maximum number of tokens in each IP's bucket.
        - token_rate: Rate at which tokens are refilled per second.
        """
        self.bucket_capacity = bucket_capacity  # max tokens per bucket
        self.token_rate = token_rate            # tokens refilled per second
        self.ip_buckets = {}                    # Dictionary to store buckets for each IP
        self.lock = threading.Lock()
    
    def get_or_create_bucket(self, ip):
        """
        Get the token bucket for a specific IP address. If it doesn't exist, create one.

        Args:
        - ip: The IP address of the incoming request.

        Returns:
        - bucket: The token bucket for the given IP address.
        """
        if ip not in self.ip_buckets: 
            # initialize a new bucket for the IP with max tokens and the current timestamp
            self.ip_buckets[ip] = {
                "tokens": self.bucket_capacity,      # Start with full bucket
                "last_refill_time": time.time()      # Timestamp of the last refill
            }
        return self.ip_buckets[ip]
    
    def refill_tokens(self, bucket):
        """
        Refill tokens in the bucket based on the time passed since the last refill.

        Args:
        - bucket: The token bucket that needs to be refilled.
        """
        now = time.time() 
        time_passed = now - bucket["last_refill_time"]
        new_tokens = int(time_passed * self.token_rate)

        if new_tokens > 0: 
            bucket["tokens"] = min(bucket["tokens"] + new_tokens, self.bucket_capacity)
            bucket["last_refill_time"] = now
    
    def consume_token(self, ip):
        """
        Attempt to consume a token from the bucket for a given IP.

        Args:
        - ip: The IP address of the incoming request.

        Returns:
        - True if a token was successfully consumed, otherwise False.
        """
        with self.lock: 
            bucket = self.get_or_create_bucket(ip)
            # refill tokens before consuming 
            self.refill_tokens(bucket)
            if bucket["tokens"] > 0: 
                bucket["tokens"] -= 1 
                return True 
            return False 

# Token bucket parameters
BUCKET_CAPACITY = 10  # Maximum 10 tokens per bucket
TOKEN_RATE = 1        # Refill 1 token per second

# Instantiate the rate limiter with the defined parameters
rate_limiter = RateLimiter(BUCKET_CAPACITY, TOKEN_RATE)

# Define the Flask route that is not rate-limited
@app.route('/unlimited')
def unlimited():
    """
    A route that can be accessed without rate limiting.
    
    Returns:
    - A simple text response indicating no limits.
    """
    return "Unlimited! Let's Go!"


# Define the Flask route that is rate-limited
@app.route('/limited')
def limited():
    """
    A route that applies rate limiting based on the token bucket algorithm.
    
    Returns:
    - A success message if tokens are available.
    - A 429 error response if the rate limit is exceeded.
    """
    ip = request.remote_addr  # Get the IP address of the requester
    if rate_limiter.consume_token(ip):
        # If token was consumed successfully, return success message
        return "Limited, don't overuse me!"
    else:
        # Return a rate limit exceeded message with a 429 HTTP status
        return jsonify({"error": "Too many requests"}), 429


# Run the Flask app when this script is executed
if __name__ == '__main__':
    """
    Start the Flask development server, making it accessible locally at port 8080.
    """
    app.run(host='127.0.0.1', port=8080)
