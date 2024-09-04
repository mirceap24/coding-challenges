import time
import threading
from flask import Flask, request, jsonify

# Create a Flask app instance
app = Flask(__name__)

# Define the SlidingWindowLogRateLimiter class to implement the sliding window log algorithm
class SlidingWindowLogRateLimiter:
    def __init__(self, window_size, max_requests):
        """
        Initialize the SlidingWindowLogRateLimiter with a window size and a request threshold.

        Args:
        - window_size: Duration of the sliding window in seconds.
        - max_requests: Maximum allowed requests within the window size.
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.ip_logs = {}
        self.lock = threading.Lock()
    
    def get_or_create_log(self, ip):
        """
        Get the log of request timestamps for a specific IP address. If it doesn't exist, create one.

        Args:
        - ip: The IP address of the incoming request.

        Returns:
        - log: The list of request timestamps for the given IP.
        """
        if ip not in self.ip_logs: 
            self.ip_logs[ip] = []
        
        return self.ip_logs[ip]
    
    def remove_old_logs(self, log):
        """
        Remove old request timestamps that fall outside of the sliding window.

        Args:
        - log: List of request timestamps for an IP address.
        """
        current_time = time.time()
        # keep only the timestamps within the sliding window (within window_size seconds)
        while log and log[0] <= current_time - self.window_size:
            log.pop(0)  # remove oldest timestamp from log 
    
    def is_request_allowed(self, ip):
        """
         Determine if a request is allowed based on the sliding window log algorithm.

        Args:
        - ip: The IP address of the incoming request.

        Returns:
        - True if the request is allowed (under the threshold), False otherwise.
        """
        with self.lock:
            log = self.get_or_create_log(ip) # Retrieve or create the log for this IP
            self.remove_old_logs(log)

            if len(log) < self.max_requests:
                # If the number of requests in the current window is below the threshold, allow the request
                log.append(time.time())  # Add the current request's timestamp to the log
                return True 

            return False 

# Sliding window parameters
WINDOW_SIZE = 60   # Window size in seconds (e.g., 60 seconds)
MAX_REQUESTS = 10  # Maximum allowed requests in a single window

# Instantiate the rate limiter with the defined parameters
rate_limiter = SlidingWindowLogRateLimiter(WINDOW_SIZE, MAX_REQUESTS)

# Define the Flask route that is rate-limited using the sliding window log algorithm
@app.route('/limited')
def sliding_window_limited():
    """
    A route that applies rate limiting using the sliding window log algorithm.

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
        
             