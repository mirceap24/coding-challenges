import threading
import unittest
from unittest.mock import patch

from token_bucket import app, ip_buckets, refill_tokens, consume_token, BUCKET_CAPACITY, TOKEN_RATE

class TestTokenBucket(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        ip_buckets.clear()
        self.app_context.pop()
    
    def test_unlimited_route(self):
        response = self.app.get('/unlimited')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Unlimited! Let's Go!")

    def test_limited_route_success(self):
        response = self.app.get('/limited')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Limited, don't overuse me!")
    
    def test_limited_route_rate_limit_exceeded(self):
        # consume all tokens 
        for _ in range(BUCKET_CAPACITY):
            self.app.get('/limited')
        
        # this request should be rate limited 
        response = self.app.get('/limited')
        self.assertEqual(response.status_code, 429)
        self.assertIn("error", response.get_json())
    
    @patch('time.time')
    def test_token_refill(self, mock_time):
        mock_time.return_value = 0 
        ip = '192.168.1.1'
        bucket = ip_buckets[ip]

        for _ in range(BUCKET_CAPACITY):
            consume_token(bucket)
        
        self.assertEqual(bucket['tokens'], 0)

        # move time forward by 5 seconds
        mock_time.return_value = 5 
        refill_tokens(bucket)

        # Check if 5 tokens have been refilled (5 seconds * 1 token/second)
        self.assertEqual(bucket['tokens'], 5)
    
    @patch('time.time')
    def test_token_refill_max_capacity(self, mock_time):
        mock_time.return_value = 0
        ip = '192.168.1.1'
        bucket = ip_buckets[ip]

        # move time forward by more than enough to refill the entire bucket
        mock_time.return_value = BUCKET_CAPACITY * 2 / TOKEN_RATE
        refill_tokens(bucket)

        # check if the bucket is filled to capacity, not exceeding it
        self.assertEqual(bucket['tokens'], BUCKET_CAPACITY)
    
    def test_multiple_ips(self):
        # simulate requests from two different IPs
        response1 = self.app.get('/limited', environ_base={'REMOTE_ADDR': '1.1.1.1'})
        response2 = self.app.get('/limited', environ_base={'REMOTE_ADDR': '2.2.2.2'})

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

        # check that we have separate buckets for each IP
        self.assertEqual(len(ip_buckets), 2)
        self.assertIn('1.1.1.1', ip_buckets)
        self.assertIn('2.2.2.2', ip_buckets)
    
    @patch('token_bucket.consume_token')
    def test_consume_token_called(self, mock_consume_token):
        mock_consume_token.return_value = True
        response = self.app.get('/limited')
        self.assertEqual(response.status_code, 200)
        mock_consume_token.assert_called_once()
    
    @patch('token_bucket.consume_token')
    def test_consume_token_rate_limited(self, mock_consume_token):
        mock_consume_token.return_value = False
        response = self.app.get('/limited')
        self.assertEqual(response.status_code, 429)
        mock_consume_token.assert_called_once()
    
    def test_concurrent_requests(self):
        num_requests = 50 
        num_allowed = BUCKET_CAPACITY
        results = []

        def make_request():
            response = self.app.get('/limited')
            results.append(response.status_code)
        
        threads = []
        for _ in range(num_requests):
            thread = threading.Thread(target = make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads: 
            thread.join()

        # count the number of successful (200) and rate-limited (429) responses
        successful_requests = results.count(200)
        rate_limited_requests = results.count(429)

        self.assertEqual(successful_requests, num_allowed)
        self.assertEqual(rate_limited_requests, num_requests - num_allowed)
    
    def test_concurrent_requests_multiple_ips(self):
        num_ips = 5
        num_requests_per_ip = 20
        num_allowed_per_ip = BUCKET_CAPACITY  # number of requests that should be allowed per IP

        results = {f'192.168.0.{i}': [] for i in range(1, num_ips + 1)}

        def make_request(ip):
            response = self.app.get('/limited', environ_base={'REMOTE_ADDR': ip})
            results[ip].append(response.status_code)

        threads = []
        for ip in results.keys():
            for _ in range(num_requests_per_ip):
                thread = threading.Thread(target=make_request, args=(ip,))
                threads.append(thread)
                thread.start()

        # wait for all threads to complete
        for thread in threads:
            thread.join()

        for ip, res in results.items():
            successful_requests = res.count(200)
            rate_limited_requests = res.count(429)
            self.assertEqual(successful_requests, num_allowed_per_ip, f"IP {ip} did not have the expected number of successful requests")
            self.assertEqual(rate_limited_requests, num_requests_per_ip - num_allowed_per_ip, f"IP {ip} did not have the expected number of rate-limited requests")




if __name__ == '__main__':
    unittest.main()