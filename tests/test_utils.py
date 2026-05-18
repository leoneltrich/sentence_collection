import unittest
from app.utils import normalize_sentence

class TestNormalization(unittest.TestCase):
    def test_lowercase(self):
        self.assertEqual(normalize_sentence("HELLO WORLD"), "hello world")
    
    def test_remove_punctuation(self):
        self.assertEqual(normalize_sentence("Hello, World!"), "hello world")
        self.assertEqual(normalize_sentence("Wait... what?"), "wait what")
        self.assertEqual(normalize_sentence("Sentence with (parentheses) and [brackets]."), "sentence with parentheses and brackets")
    
    def test_mixed_case_and_punctuation(self):
        self.assertEqual(normalize_sentence("This is a Test, with Commas and Dots."), "this is a test with commas and dots")
    
    def test_whitespace_handling(self):
        self.assertEqual(normalize_sentence("  Multiple   spaces  "), "multiple spaces")
    
    def test_empty_string(self):
        self.assertEqual(normalize_sentence(""), "")

if __name__ == '__main__':
    unittest.main()
