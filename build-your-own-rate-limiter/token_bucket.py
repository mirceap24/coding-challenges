from flask import Flask, request, jsonify, make_response
from time import time 
import threading 

app = Flask(__name__)

# Token bucket parameters 
TOKENS_PER_SECOND = 1 
BUCKET_CAPACITY = 10 
token_buckets = {} 
lock = threading.Lock()

def get_bucket(ip):
    current_time = time()

    with lock: # thread safe access to token_buckets
        if ip not in token_buckets: 
            token_buckets[ip] = {"tokens": BUCKET_CAPACITY, "last_checked": current_time}
        
        bucket = token_buckets[ip]
        time_passed = current_time - bucket['last_checked']

        if time_passed >= 1: 
            new_tokens = int(time_passed * TOKENS_PER_SECOND)
            bucket['tokens'] = min(BUCKET_CAPACITY, bucket['tokens'] + new_tokens)
            bucket['last_checked'] = current_time
    
    return bucket 

def allow_request(ip):
    bucket = get_bucket(ip)

    with lock: 
        if bucket['tokens'] >= 1: 
            bucket['tokens'] -= 1
            return True 
        else: 
            return False 

@app.route('/unlimited', methods = ['GET'])
def unlimited():
    return "Unlimited! Let's Go!", 200 

@app.route('/limited', methods = ['GET'])
def limited():
    ip = request.remote_addr

    if allow_request(ip):
        return "Limited, don't over use me!", 200 
    else: 
        return jsonify({"error": "Too many requests"}), 429 

if __name__ == '__main__':
    app.run(host = '127.0.0.1', port = 8080)