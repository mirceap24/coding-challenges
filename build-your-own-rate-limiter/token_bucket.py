from flask import Flask, request, jsonify
import time

# Flask application instance 
app = Flask(__name__)

# Dictionary to store token buckets for each IP address
token_buckets = {}

# Constants for the token bucket 
MAX_TOKENS = 10     # max capacity of the bucket
REFILL_RATE = 1     # tokens added per second

def get_token_bucket(ip): 
    """
    Retrieve or create a token bucket for the given IP address.
    Each bucket is represented by a dictionary containing: 
        - last_checked: The last time the bucket was refilled
        - tokens: The current number of tokens in the bucket
    """
    current_time = time.time()
    if ip not in token_buckets: 
        # create new token bucket for the IP 
        token_buckets[ip] = {'tokens': MAX_TOKENS, 'last_checked': current_time}
        return token_buckets[ip]

    # retrieve existing bucket 
    bucket = token_buckets[ip]

    # calculate the time since the last check 
    time_passed = current_time - bucket['last_checked']

    # calculate how many tokens to add(based on time passed)
    tokens_to_add = int(time_passed * REFILL_RATE)

    # update number of tokens, without exceeding MAX_TOKENS 
    bucket['tokens'] = min(MAX_TOKENS, bucket['tokens'] + tokens_to_add)

    # update last checked time 
    bucket['last_checked'] = current_time

    return bucket

def is_request_allowed(ip):
    """
    Check if the request is allowed based on the token bucket for the IP address.
    If allowed, a token is consumed from the bucket. If not, the request is denied.
    """
    bucket = get_token_bucket(ip)

    if bucket['tokens'] >= 1: 
        bucket['tokens'] -= 1 
        return True 
    else: 
        # deny request as the bucket is empty 
        return False 


# Define the '/limited' route 
@app.route('/limited', methods = ['GET'])
def limited():
    """
    This route represents an endpoint that will have rate limiting applied in the future.
    For now, it just returns a simple message.
    """
    ip = request.remote_addr

    if is_request_allowed(ip):
        return "Request allowed\n"
    else: 
        return jsonify({"error": "Too Many Requests"}), 429

# Define the '/unlimited' route 
@app.route('/unlimited', methods = ['GET'])
def unlimited():
    """
    This route does not have any rate limiting.
    Can be accessed any number of times without any restrictions.
    """
    return "Unlimited! Let's Go!\n"

# run the Flask app 
if __name__ == "__main__":
    app.run(host = '127.0.0.1', port = 8080)