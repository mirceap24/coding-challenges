import time
import threading
from flask import Flask, request, jsonify

# Create a Flask app instance
app = Flask(__name__)

# Define the SlidingWindowCounterRateLimiter class
class SlidingWindowCounterRateLimiter:
    def __init__(self, window_size, max_requests):
        """
        Initialize the SlidingWindowCounterRateLimiter with a window size and a request threshold.

        Args:
        - window_size: Duration of each time window in seconds.
        - max_requests: Maximum allowed requests within the window size.
        """
        self.window_size = window_size        # Window size in seconds (e.g., 60 seconds)
        self.max_requests = max_requests      # Maximum allowed requests in a sliding window
        self.ip_counters = {}                 # Dictionary to store request counts for each IP
        self.lock = threading.Lock()          # Lock for thread safety

    def get_current_window(self):
        """
        Calculate the current time window based on the floor of the current timestamp.
        
        Returns:
        - current_window: The current window timestamp (in window_size intervals).
        """
        return int(time.time() // self.window_size)
    
    def get_or_create_counters(self, ip):
        """
        Get or create the counters for a specific IP address. We store both current and previous window counts.

        Args:
        - ip: The IP address of the incoming request.

        Returns:
        - counters: A dictionary containing the current and previous window counters for the IP.
        """
        current_window = self.get_current_window()

        if ip not in self.ip_counters:
            self.ip_counters[ip] = {
                "current_window": current_window,
                "current_count": 0,
                "previous_window": current_window - 1,
                "previous_count": 0
            }
        
        counters = self.ip_counters[ip]

        # if the current window is different from stored one, shift windows
        if counters["current_window"] != current_window:
            # shift current to window
            counters["previous_window"] = counters["current_window"]
            counters["previous_count"] = counters["current_count"]
            # reset current window count for the new window
            counters["current_window"] = current_window
            counters["current_count"] = 0
        
        return counters 
    
    def is_request_allowed(self, ip):
        """
        Determine if a request is allowed based on the sliding window counter algorithm.

        Args:
        - ip: The IP address of the incoming request.

        Returns:
        - True if the request is allowed (under the threshold), False otherwise.
        """
        with self.lock:
            counters = self.get_or_create_counters(ip)
            current_time = time.time()

            # calculate how far into the current window we are
            time_in_current_window = current_time % self.window_size
            percentage_in_current_window = time_in_current_window / self.window_size

            # calculate the weighted request count from current and previous windows
            weighted_count = (
                counters["previous_count"] * (1 - percentage_in_current_window)
                + counters["current_count"] * percentage_in_current_window
            )

            if weighted_count < self.max_requests:
                # If the weighted count is under the limit, allow the request
                counters["current_count"] += 1
                return True

            # Otherwise, reject the request
            return False

# Sliding window parameters
WINDOW_SIZE = 60   # Window size in seconds (e.g., 60 seconds)
MAX_REQUESTS = 10  # Maximum allowed requests in the sliding window

# Instantiate the rate limiter with the defined parameters
rate_limiter = SlidingWindowCounterRateLimiter(WINDOW_SIZE, MAX_REQUESTS)

# Define the Flask route that is rate-limited using the sliding window counter algorithm
@app.route('/limited')
def sliding_window_counter_limited():
    """
    A route that applies rate limiting using the sliding window counter algorithm.

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

         