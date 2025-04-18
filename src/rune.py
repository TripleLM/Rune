#!/usr/bin/env python3
"""
Rune - Main application entry point
"""
import os
import sys
import logging
import argparse
import signal
from pathlib import Path

# Import modules
from audio.recorder import AudioRecorder
from audio.player import AudioPlayer
from morse.interpreter import MorseInterpreter
from assistant.engine import AssistantEngine
from interface.button import ButtonInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rune")

class Rune:
    """Main Rune assistant application class"""
    
    def __init__(self, config_path=None):
        logger.info("Initializing Rune assistant...")
        
        # Set up configuration
        self.config_path = config_path or Path("config/default.yml")
        self.load_config()
        
        # Initialize components
        self.audio_recorder = AudioRecorder(self.config)
        self.audio_player = AudioPlayer(self.config)
        self.morse = MorseInterpreter(self.config)
        self.assistant = AssistantEngine(self.config)
        self.button = ButtonInterface(self.config)
        
        # Set up button callback
        self.button.set_press_callback(self.handle_button_press)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        
        logger.info("Rune assistant initialized and ready")
    
    def load_config(self):
        """Load configuration from file"""
        logger.info(f"Loading configuration from {self.config_path}")
        # TODO: Implement actual config loading
        self.config = {
            "audio": {
                "sample_rate": 16000,
                "channels": 1
            },
            "assistant": {
                "model_path": "models/assistant_model"
            }
        }
    
    def handle_button_press(self):
        """Handle push-to-talk button press"""
        logger.info("Button pressed - starting interaction")
        
        # Stop any current output
        self.audio_player.stop()
        
        # Listen for input
        audio_data = self.audio_recorder.record()
        
        # Check if input is morse code
        if self.morse.is_morse(audio_data):
            text = self.morse.decode(audio_data)
        else:
            # Process speech to text
            text = self.audio_recorder.transcribe(audio_data)
        
        logger.info(f"Recognized input: {text}")
        
        # Process with assistant
        response = self.assistant.process(text)
        
        # Output response
        logger.info(f"Assistant response: {response}")
        self.audio_player.speak(response)
    
    def run(self):
        """Run the main application loop"""
        logger.info("Starting Rune assistant")
        try:
            # Main event loop
            while True:
                # Just wait for button press callbacks
                signal.pause()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            self.handle_shutdown(None, None)
    
    def handle_shutdown(self, signum, frame):
        """Handle graceful shutdown"""
        logger.info("Shutting down Rune assistant...")
        
        # Clean up resources
        self.audio_recorder.cleanup()
        self.audio_player.cleanup()
        self.button.cleanup()
        
        logger.info("Shutdown complete.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rune - Offline Local AI Assistant")
    parser.add_argument("--config", help="Path to configuration file")
    args = parser.parse_args()
    
    app = Rune(config_path=args.config)
    app.run() 