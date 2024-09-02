import time
import threading
from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)

BUCKET_CAPACITY = 10 
TOKEN_RATE = 1 

class TokenBucket: 
    def __init__(self):
        self.tokens = BUCKET_CAPACITY
        self.last_refill_time = time.time()

    def consume(self):
        if self.tokens > 0: 
            self.tokens -= 1 
            return True 
        return False 
    
    def refill(self):
        now = time.time()
        time_passed = now - self.last_refill_time
        new_tokens = int(time_passed * TOKEN_RATE)
        if new_tokens > 0:
            self.tokens = min(self.tokens + new_tokens, BUCKET_CAPACITY)
            self.last_refill_time = now

ip_buckets = defaultdict(TokenBucket)

@app.route('/unlimited')
def unlimited():
    return "Unlimited! Let's Go!"

@app.route('/limited')
def limited():
    ip = request.remote_addr
    bucket = ip_buckets[ip]

    # background thread handles refilling 
    if bucket.consume():
        return "Limited, don't overuse me!"
    else: 
        return jsonify({"error": "Too many requests"}), 429 

def token_refill_thread():
    while True: 
        time.sleep(1)
        for bucket in ip_buckets.values():
            bucket.refill()

if __name__ == '__main__':
    # Start the token refill thread
    refill_thread = threading.Thread(target=token_refill_thread, daemon=True)
    refill_thread.start()
    
    # Run the Flask app
    app.run(host='127.0.0.1', port=8080)

    

