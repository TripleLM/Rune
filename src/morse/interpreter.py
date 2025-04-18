"""
Morse code interpretation and generation module
"""
import logging
import numpy as np
from scipy import signal

logger = logging.getLogger("rune.morse")

class MorseInterpreter:
    """Interprets and generates Morse code"""
    
    # Morse code mapping
    MORSE_CODE = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 
        'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--', 
        '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', 
        '9': '----.', '.': '.-.-.-', ',': '--..--', '?': '..--..', 
        "'": '.----.', '!': '-.-.--', '/': '-..-.', '(': '-.--.', 
        ')': '-.--.-', '&': '.-...', ':': '---...', ';': '-.-.-.', 
        '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-', 
        '"': '.-..-.', '$': '...-..-', '@': '.--.-.'
    }
    
    # Reverse mapping for decoding
    REVERSE_MORSE = {v: k for k, v in MORSE_CODE.items()}
    
    def __init__(self, config):
        """Initialize morse interpreter with configuration"""
        self.config = config
        self.sample_rate = config["audio"].get("sample_rate", 16000)
        
        # Configuration for morse detection
        self.dot_duration = 0.1  # seconds
        self.dash_duration = self.dot_duration * 3
        self.threshold = 0.5  # amplitude threshold for detecting signals
        
        logger.info("MorseInterpreter initialized")
    
    def is_morse(self, audio_data):
        """
        Check if audio data contains morse code patterns
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Boolean indicating if audio contains morse patterns
        """
        # Simplified detection logic - actual implementation would be more sophisticated
        # This looks for regular patterns of similar duration sounds with pauses
        
        # Convert to mono if needed
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)
        
        # Get the amplitude envelope
        envelope = np.abs(audio_data)
        
        # Detect peaks (simple threshold-based approach)
        peaks = envelope > self.threshold
        
        # Check for morse-like patterns
        # This is a very simplified approach
        return np.any(peaks)
    
    def decode(self, audio_data):
        """
        Decode morse code from audio
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Decoded text
        """
        logger.info("Decoding morse from audio")
        
        # TODO: Implement actual morse decoding
        # This would analyze timing of sounds and silences to identify dots and dashes
        
        # For this example, we'll just return a placeholder
        morse_string = "... --- ..."  # SOS
        return self.morse_to_text(morse_string)
    
    def morse_to_text(self, morse_string):
        """
        Convert morse code string to text
        
        Args:
            morse_string: String with dots, dashes and spaces
            
        Returns:
            Decoded text
        """
        words = morse_string.split("   ")
        text = []
        
        for word in words:
            chars = word.split(" ")
            for char in chars:
                if char in self.REVERSE_MORSE:
                    text.append(self.REVERSE_MORSE[char])
            text.append(" ")
        
        return "".join(text).strip()
    
    def text_to_morse(self, text):
        """
        Convert text to morse code
        
        Args:
            text: Text to convert
            
        Returns:
            Morse code string (dots and dashes)
        """
        morse = []
        for char in text.upper():
            if char == ' ':
                morse.append("   ")  # word space
            elif char in self.MORSE_CODE:
                morse.append(self.MORSE_CODE[char])
                morse.append(" ")  # character space
        
        return "".join(morse).strip() 