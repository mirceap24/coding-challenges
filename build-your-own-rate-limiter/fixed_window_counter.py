import time
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

class FixedWindowRateLimiter: 
    def __init__(self, window_size, max_requests):
        """
        Initialize the FixedWindowRateLimiter with a window size and a request threshold.

        Args:
        - window_size: Duration of each time window in seconds.
        - max_requests: Maximum number of allowed requests in a single window.
        """
        self.window_size = window_size  # Length of each window in seconds (e.g., 60 seconds)
        self.max_requests = max_requests    # Maximum allowed requests per window
        self.ip_counters = {}   # Dictionary to store counters for each IP
        self.lock = threading.Lock()
    
    def get_current_window(self):
        """
        Calculate the current time window based on the floor of the current timestamp.

        Returns:
        - current_window: The current window timestamp (floor based on window_size).
        """
        return int(time.time() // self.window_size)

    def get_or_create_counter(self, ip):
        """
        Get the request counter for a specific IP address and the current time window. If it doesn't exist, create one.

        Args:
        - ip: The IP address of the incoming request.

        Returns:
        - counter: The request counter for the given IP address and current window.
        """
        current_window = self.get_current_window()

        if ip not in self.ip_counters:
            # If the IP has no entry, initialize it with the current window and count of 0
            self.ip_counters[ip] = {"window": current_window, "count": 0}
        
        # if the current window is different from the one stored, reset the counter
        if self.ip_counters[ip]["window"] != current_window:
            self.ip_counters[ip]["window"] = current_window
            self.ip_counters[ip]["count"] = 0
        
        return self.ip_counters[ip]
    
    def is_request_allowed(self, ip):
        """
        Determine if a request is allowed based on the fixed window rate limiting.

        Args:
        - ip: The IP address of the incoming request.

        Returns:
        - True if the request is allowed (under the threshold), False otherwise.
        """
        with self.lock: 
            counter = self.get_or_create_counter(ip)

            if counter["count"] < self.max_requests:
                counter["count"] += 1 
                return True 

            return False 

# Fixed window parameters
WINDOW_SIZE = 60   # Window size in seconds (e.g., 60 seconds)
MAX_REQUESTS = 60  # Maximum allowed requests in a single window

# Instantiate the rate limiter with the defined parameters
rate_limiter = FixedWindowRateLimiter(WINDOW_SIZE, MAX_REQUESTS)

# Define the Flask route that is rate-limited using the fixed window counter algorithm
@app.route('/limited')
def fixed_window_limited():
    """
    A route that applies rate limiting using the fixed window counter algorithm.

    Returns:
    - A success message if the request is allowed.
    - A 429 error response if the rate limit is exceeded.
    """
    ip = request.remote_addr  # Get the IP address of the requester
    if rate_limiter.is_request_allowed(ip):
        # If the request is allowed (under the limit), return a success message
        return "Request succeeded!"
    else:
        # Return a rate limit exceeded message with a 429 HTTP status if the threshold is exceeded
        return jsonify({"error": "Too many requests"}), 429


# Run the Flask app when this script is executed
if __name__ == '__main__':
    """
    Start the Flask development server, making it accessible locally at port 8080.
    """
    app.run(host='127.0.0.1', port=8080)
