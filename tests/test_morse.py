"""
Tests for the morse code interpreter
"""
import unittest
import sys
import os
import numpy as np

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.morse.interpreter import MorseInterpreter

class TestMorseInterpreter(unittest.TestCase):
    """Test case for MorseInterpreter class"""
    
    def setUp(self):
        """Set up test case"""
        # Create a mock config
        self.config = {
            "audio": {
                "sample_rate": 16000,
                "channels": 1
            }
        }
        self.interpreter = MorseInterpreter(self.config)
    
    def test_text_to_morse(self):
        """Test text to morse conversion"""
        # Test basic conversion
        self.assertEqual(self.interpreter.text_to_morse("SOS"), "... --- ...")
        
        # Test case insensitivity
        self.assertEqual(self.interpreter.text_to_morse("sos"), "... --- ...")
        
        # Test with spaces
        self.assertEqual(self.interpreter.text_to_morse("HELLO WORLD"), 
                        ".... . .-.. .-.. ---   .-- --- .-. .-.. -..")
    
    def test_morse_to_text(self):
        """Test morse to text conversion"""
        # Test basic conversion
        self.assertEqual(self.interpreter.morse_to_text("... --- ..."), "SOS")
        
        # Test with word spaces
        self.assertEqual(self.interpreter.morse_to_text(".... . .-.. .-.. ---   .-- --- .-. .-.. -.."), 
                        "HELLO WORLD")
    
    def test_is_morse(self):
        """Test morse detection"""
        # Create a simple audio pattern that should be detected as morse
        sample_rate = 16000
        duration = 1  # seconds
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create a sine wave at 800 Hz (typical morse code frequency)
        frequency = 800
        audio = np.sin(2 * np.pi * frequency * t)
        
        # Reshape to match expected format
        audio = audio.reshape(-1, 1)
        
        # It should detect this pattern as potential morse code
        self.assertTrue(self.interpreter.is_morse(audio))
        
        # Empty audio should not be detected as morse
        self.assertFalse(self.interpreter.is_morse(np.zeros((100, 1))))

if __name__ == "__main__":
    unittest.main() 