"""
Audio recording and voice transcription module
"""
import logging
import numpy as np
import sounddevice as sd
from pathlib import Path

logger = logging.getLogger("rune.audio.recorder")

class AudioRecorder:
    """Records audio from microphone and transcribes speech to text"""
    
    def __init__(self, config):
        """Initialize audio recorder with configuration"""
        self.config = config
        self.sample_rate = config["audio"].get("sample_rate", 16000)
        self.channels = config["audio"].get("channels", 1)
        self.recording = False
        
        # Initialize the local speech recognition model
        self.init_speech_recognition()
        
        logger.info(f"AudioRecorder initialized with sample rate {self.sample_rate}")
    
    def init_speech_recognition(self):
        """Initialize the speech recognition model"""
        # TODO: Load the appropriate offline STT model
        pass
    
    def record(self, duration=None):
        """
        Record audio from microphone
        
        Args:
            duration: Duration in seconds to record, or None to use button control
            
        Returns:
            Audio data as numpy array
        """
        logger.info("Starting audio recording")
        self.recording = True
        
        # In a button-controlled setup, this would be triggered by the button
        # and stopped when the button is released
        
        if duration:
            # Fixed duration recording
            frames = int(duration * self.sample_rate)
            audio_data = sd.rec(frames, samplerate=self.sample_rate, channels=self.channels)
            sd.wait()
        else:
            # This is a simplified version - actual implementation would use
            # the button interface to control recording duration
            frames = int(5 * self.sample_rate)  # Default to 5 seconds
            audio_data = sd.rec(frames, samplerate=self.sample_rate, channels=self.channels)
            sd.wait()
        
        self.recording = False
        logger.info("Audio recording complete")
        
        return audio_data
    
    def transcribe(self, audio_data):
        """
        Transcribe audio data to text using local model
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Transcribed text
        """
        logger.info("Transcribing audio to text")
        
        # TODO: Implement actual transcription with local model
        # This is a placeholder
        transcribed_text = "placeholder transcription"
        
        return transcribed_text
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up AudioRecorder resources")
        # Stop any ongoing recording
        if self.recording:
            sd.stop() 