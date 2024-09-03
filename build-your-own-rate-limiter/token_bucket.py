import time
import threading
from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)

# Token bucket parameters
BUCKET_CAPACITY = 10
TOKEN_RATE = 1

# Dictionary to store token buckets for each IP address
ip_buckets = defaultdict(lambda: {"tokens": BUCKET_CAPACITY, "last_refill_time": time.time()})

lock = threading.Lock()

def refill_tokens(bucket):
    """
    Refill the bucket with tokens based on the elapsed time since the last refill.
    This function is now called during each request to ensure tokens are refilled in real-time.
    """
    now = time.time()
    time_passed = now - bucket["last_refill_time"]
    new_tokens = int(time_passed * TOKEN_RATE)
    if new_tokens > 0:
        bucket["tokens"] = min(bucket["tokens"] + new_tokens, BUCKET_CAPACITY)
        bucket["last_refill_time"] = now

def consume_token(bucket):
    """
    Attempt to consume a token from the bucket.
    This function is now responsible for refilling tokens before consuming.
    Returns True if successful (token available), False if no tokens are available.
    """
    with lock:
        refill_tokens(bucket)  # make sure tokens are refilled before consumption
        if bucket["tokens"] > 0:
            bucket["tokens"] -= 1
            return True
        return False

@app.route('/unlimited')
def unlimited():
    return "Unlimited! Let's Go!"

@app.route('/limited')
def limited():
    ip = request.remote_addr
    bucket = ip_buckets[ip]

    if consume_token(bucket):
        return "Limited, don't overuse me!"
    else:
        return jsonify({"error": "Too many requests"}), 429

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
