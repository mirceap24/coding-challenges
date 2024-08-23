import unittest
import tempfile
import os
import sys
from io import StringIO
from unittest.mock import patch
from ccwc import count_bytes_lines_words_chars, count_bytes_lines_words_chars_from_stdin, ccwc

class TestCCWC(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode = 'w+', delete = False)
        self.temp_file.write("Hello, world!\nThis is a test file.")
        self.temp_file.close()

        # large temporary file for testing 
        self.large_temp_file = tempfile.NamedTemporaryFile(mode = 'w+', delete = False)
        for _ in range(100000):
            self.large_temp_file.write("This is a long line of text for testing purposes.\n")
        self.large_temp_file.close()

    def cleanUp(self):
        os.unlink(self.temp_file.name)
        os.unlink(self.large_temp_file.name)

    def test_count_bytes_lines_words_chars(self):
        # Test the function that counts from a file
        bytes_count, lines_count, words_count, chars_count = count_bytes_lines_words_chars(self.temp_file.name)
        self.assertEqual(bytes_count, 34)
        self.assertEqual(lines_count, 2)
        self.assertEqual(words_count, 7)
        self.assertEqual(chars_count, 34)
    
    def test_count_bytes_lines_words_chars_large_file(self):
        # Test the function with a large file
        bytes_count, lines_count, words_count, chars_count = count_bytes_lines_words_chars(self.large_temp_file.name)
        self.assertEqual(lines_count, 100000)
        self.assertEqual(words_count, 1000000)  # 10 words per line
        self.assertEqual(chars_count, 5000000)  # 50 characters per line (including newline)

    @patch('sys.stdin', StringIO("Hello, world!\nThis is a test file.\n"))
    def test_count_bytes_lines_words_chars_from_stdin(self):
        # Test the function that counts from stdin
        bytes_count, lines_count, words_count, chars_count = count_bytes_lines_words_chars_from_stdin()
        self.assertEqual(bytes_count, 35)
        self.assertEqual(lines_count, 2)
        self.assertEqual(words_count, 7)
        self.assertEqual(chars_count, 35)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_ccwc_with_file(self, mock_stdout):
        # Test ccwc function with different options for a file
        ccwc('-c', self.temp_file.name)
        self.assertEqual(mock_stdout.getvalue().strip(), f"34 {self.temp_file.name}")

        mock_stdout.truncate(0) # clear the content
        mock_stdout.seek(0) # move cursor at beginning

        ccwc('-l', self.temp_file.name)
        self.assertEqual(mock_stdout.getvalue().strip(), f"2 {self.temp_file.name}")

        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        ccwc('-w', self.temp_file.name)
        self.assertEqual(mock_stdout.getvalue().strip(), f"7 {self.temp_file.name}")

        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        ccwc('-m', self.temp_file.name)
        self.assertEqual(mock_stdout.getvalue().strip(), f"34 {self.temp_file.name}")

        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        ccwc(None, self.temp_file.name)
        self.assertEqual(mock_stdout.getvalue().strip(), f"2 7 34 {self.temp_file.name}")

    @patch('sys.stdout', new_callable=StringIO)
    def test_ccwc_with_stdin(self, mock_stdout):
        # Mock sys.stdin with the input
        input_data = "Hello, world!\nThis is a test file.\n"
        
        with patch('sys.stdin', StringIO(input_data)):
            ccwc('-c')
            self.assertEqual(mock_stdout.getvalue().strip(), "35")
        
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        with patch('sys.stdin', StringIO(input_data)):
            ccwc('-l')
            self.assertEqual(mock_stdout.getvalue().strip(), "2")
        
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        with patch('sys.stdin', StringIO(input_data)):
            ccwc('-w')
            self.assertEqual(mock_stdout.getvalue().strip(), "7")
        
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        with patch('sys.stdin', StringIO(input_data)):
            ccwc('-m')
            self.assertEqual(mock_stdout.getvalue().strip(), "35")
        
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        with patch('sys.stdin', StringIO(input_data)):
            ccwc(None)
            self.assertEqual(mock_stdout.getvalue().strip(), "2 7 35")

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()