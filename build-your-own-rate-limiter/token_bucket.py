import time 
import threading 
from flask import Flask, request, jsonify 

app = Flask(__name__)

class RateLimiter: 
    def __init__(self, bucket_capacity, token_rate):
        self.bucket_capacity = bucket_capacity
        self.token_rate = token_rate
        self.ip_buckets = {}
        self.lock = threading.Lock()
    
    def get_or_create_bucket(self, ip):
        if ip not in self.ip_buckets:
            self.ip_buckets[ip] = {
                "tokens": self.bucket_capacity, 
                "last_refill_time": time.time()
            }
        return self.ip_buckets[ip]

    def refill_tokens(self, bucket):
        now = time.time()
        time_passed = now - bucket["last_refill_time"]
        new_tokens = int(time_passed * self.token_rate)
        if new_tokens > 0:
            bucket["tokens"] = min(bucket["tokens"] + new_tokens, self.bucket_capacity)
            bucket["last_refill_time"] = now
    
    def consume_token(self, ip):
        with self.lock:
            bucket = self.get_or_create_bucket(ip)
            self.refill_tokens(bucket)
            if bucket["tokens"] > 0:
                bucket["tokens"] -= 1
                return True
            return False

# Tocken bucket parameters 
BUCKET_CAPACITY = 10
TOKEN_RATE = 1

rate_limiter = RateLimiter(BUCKET_CAPACITY, TOKEN_RATE)

@app.route('/unlimited')
def unlimited():
    return "Unlimited! Let's Go!"

@app.route('/limited')
def limited():
    ip = request.remote_addr
    if rate_limiter.consume_token(ip):
        return "Limited, don't overuse me!"
    else:
        return jsonify({"error": "Too many requests"}), 429


if __name__ == '__main__': 
    app.run(host='127.0.0.1', port=8080)