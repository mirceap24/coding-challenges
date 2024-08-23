import unittest 
import tempfile 
import os 
import sys 
import subprocess
from io import StringIO 
from unittest.mock import patch 

from ccwc import count_bytes, count_lines, count_words, count_chars, count_all, count_from_stdin, main

class TestCCWCUtility(unittest.TestCase):

    def setUp(self):
        # temporary file for testing 
        self.temp_file = tempfile.NamedTemporaryFile(delete = False)
        self.temp_filename = self.temp_file.name 
    
    def tearDown(self):
        self.temp_file.close()
        os.unlink(self.temp_filename)

    def test_count_bytes(self):
        content = b"Hello\nWorld\n"
        self.temp_file.write(content)
        self.temp_file.flush()
        self.assertEqual(count_bytes(self.temp_filename), len(content))

    def test_count_lines(self):
        content = "Hello\nWorld\n"
        with open(self.temp_filename, 'w') as f: 
            f.write(content)
        self.assertEqual(count_lines(self.temp_filename), 2)
    
    def test_count_words(self):
        content = "Hello World\nThis is a test\n"
        with open(self.temp_filename, 'w') as f:
            f.write(content)
        self.assertEqual(count_words(self.temp_filename), 6)
    
    def test_count_chars(self):
        content = "Hello World\nThis is a test\n"
        with open(self.temp_filename, 'w') as f:
            f.write(content)
        self.assertEqual(count_chars(self.temp_filename), len(content))

    def test_count_all(self):
        content = "Hello World\nThis is a test\n"
        with open(self.temp_filename, 'w') as f:
            f.write(content)
        lines, words, bytes_count = count_all(self.temp_filename)
        self.assertEqual(lines, 2)
        self.assertEqual(words, 6)
        self.assertEqual(bytes_count, len(content.encode('utf-8')))
    
    @patch('sys.stdin', StringIO("Hello World\nThis is a test"))
    def test_count_from_stdin(self):
        lines, words, bytes_count, chars = count_from_stdin()
        self.assertEqual(lines, 2)
        self.assertEqual(words, 6)
        self.assertEqual(bytes_count, 26)
        self.assertEqual(chars, 26)
    
    def test_large_file_handling(self):
        # Simulate a large file using the seq and xargs commands
        # This will simulate a file with 300,000 lines of the content in test.txt
        seq_cmd = ['seq', '1', '300000']
        xargs_cmd = ['xargs', '-Inone', 'cat', self.temp_filename]
        
        with open(self.temp_filename, 'w') as f:
            f.write("Hello World\n")

        # Run the command and capture the output using subprocess
        with subprocess.Popen(seq_cmd, stdout=subprocess.PIPE) as seq_proc:
            with subprocess.Popen(xargs_cmd, stdin=seq_proc.stdout, stdout=subprocess.PIPE) as xargs_proc:
                seq_proc.stdout.close()
                output = xargs_proc.communicate()[0]

        # Since the test file contains "Hello World\n", there are 2 words and 11 bytes per line.
        expected_lines = 300000
        expected_words = expected_lines * 2
        expected_bytes = expected_lines * len("Hello World\n".encode('utf-8'))

        # Using the functions to count from the generated large content
        lines, words, bytes_count = count_all(self.temp_filename)

        self.assertEqual(lines, expected_lines)
        self.assertEqual(words, expected_words)
        self.assertEqual(bytes_count, expected_bytes)