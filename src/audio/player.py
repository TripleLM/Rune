"""
Audio playback and speech synthesis module
"""
import logging
import numpy as np
import sounddevice as sd
from pathlib import Path
import os
import wave # For Piper output
import io # For Piper output

try:
    from piper.voice import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    logging.warning("piper-tts library not found. TTS will not work.")

logger = logging.getLogger("rune.audio.player")

class AudioPlayer:
    """Handles audio playback and text-to-speech synthesis"""
    
    def __init__(self, config):
        """Initialize audio player with configuration"""
        self.audio_config = config.get("audio", {})
        self.assistant_config = config.get("assistant", {})
        
        self.sample_rate = self.audio_config.get("sample_rate", 16000) 
        self.channels = self.audio_config.get("channels", 1) # Note: Piper output is mono
        self.voice_model_type = self.assistant_config.get("voice_model_type", "piper")
        self.voice_model_path = Path(self.assistant_config.get("voice_model_path", "models/tts/en_US-lessac-medium.onnx"))
        self.voice_model_config_path = self.assistant_config.get("voice_model_config_path")
        if not self.voice_model_config_path: # Auto-detect config path if not specified
            self.voice_model_config_path = self.voice_model_path.with_suffix(".onnx.json")
        else:
            self.voice_model_config_path = Path(self.voice_model_config_path)
            
        self.playing = False
        self.tts_model: PiperVoice | None = None # Type hint for loaded TTS model
        
        # Initialize the local text-to-speech model
        self.init_tts()
        
        logger.info(f"AudioPlayer initialized with sample rate {self.sample_rate} and TTS type '{self.voice_model_type}'")
    
    def init_tts(self):
        """Initialize the text-to-speech model based on configuration"""
        if self.voice_model_type != "piper":
            logger.warning(f"Unsupported TTS model type: {self.voice_model_type}. Only 'piper' is implemented.")
            return
            
        if not PIPER_AVAILABLE:
            logger.error("Cannot initialize Piper TTS: piper-tts library not installed.")
            return
            
        logger.info(f"Attempting to load Piper TTS model from {self.voice_model_path} and config {self.voice_model_config_path}")
        
        if not self.voice_model_path.is_file():
            logger.error(f"Piper TTS model file not found: {self.voice_model_path}")
            return
        if not self.voice_model_config_path.is_file():
            logger.error(f"Piper TTS model config file not found: {self.voice_model_config_path}")
            return
            
        try:
            self.tts_model = PiperVoice.load(str(self.voice_model_path), config_path=str(self.voice_model_config_path))
            # Check if model sample rate matches config, warn if not
            # Note: Piper typically dictates its output sample rate.
            # We might need to resample if it doesn't match sounddevice needs, but let's assume they match for now.
            logger.info("Piper TTS model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Piper TTS model: {e}")
            self.tts_model = None
    
    def speak(self, text):
        """
        Convert text to speech and play it
        
        Args:
            text: Text to be spoken
        """
        logger.info(f"Converting text to speech: {text}")
        
        audio_data = None
        if self.tts_model:
            logger.info(f"Synthesizing speech using loaded TTS model: {self.voice_model_type}")
            try:
                # Synthesize to a WAV in memory
                with io.BytesIO() as wav_io:
                    self.tts_model.synthesize(text, wav_io)
                    wav_io.seek(0)
                    # Read the WAV data from memory
                    with wave.open(wav_io, 'rb') as wav_file:
                        n_channels = wav_file.getnchannels()
                        sampwidth = wav_file.getsampwidth()
                        framerate = wav_file.getframerate()
                        n_frames = wav_file.getnframes()
                        wav_bytes = wav_file.readframes(n_frames)
                        
                        # Convert bytes to numpy array
                        if sampwidth == 1:
                            dtype = np.uint8
                        elif sampwidth == 2:
                            dtype = np.int16
                        else:
                            raise ValueError("Unsupported sample width")
                            
                        audio_np = np.frombuffer(wav_bytes, dtype=dtype)
                        
                        # Normalize to float32 between -1.0 and 1.0 for sounddevice
                        if dtype == np.uint8:
                            audio_np = (audio_np.astype(np.float32) - 128) / 128.0
                        else:
                            audio_np = audio_np.astype(np.float32) / np.iinfo(dtype).max
                        
                        # Ensure correct number of channels (Piper is likely mono)
                        if n_channels == 1 and self.channels == 2:
                             audio_np = np.column_stack((audio_np, audio_np))
                        elif n_channels == 2 and self.channels == 1:
                             audio_np = audio_np.mean(axis=1)
                        # TODO: Handle resampling if framerate != self.sample_rate
                        if framerate != self.sample_rate:
                            logger.warning(f"TTS output rate ({framerate}Hz) differs from config ({self.sample_rate}Hz). Playback might be incorrect. Resampling not implemented.")
                        
                        audio_data = audio_np
                        logger.info("Speech synthesized successfully.")
                        
            except Exception as e:
               logger.error(f"Error during Piper TTS synthesis: {e}")
        else:
            logger.warning("Cannot synthesize speech: TTS Model not loaded.")

        if audio_data is not None:
             self.play(audio_data)
        else:
             logger.error("Speech synthesis failed, cannot play audio.")
             # Fallback: Play 1 second of silence
             logger.info("Playing silence as fallback.")
             self.play(np.zeros((int(self.sample_rate * 1), self.channels), dtype=np.float32))
    
    def play(self, audio_data):
        """
        Play audio data through speaker
        
        Args:
            audio_data: Audio data as numpy array
        """
        logger.info("Playing audio")
        self.playing = True
        
        # Play the audio
        sd.play(audio_data, samplerate=self.sample_rate)
        sd.wait()
        
        self.playing = False
        logger.info("Audio playback complete")
    
    def play_morse(self, morse_code):
        """
        Play morse code as audio
        
        Args:
            morse_code: Morse code string (dots and dashes)
        """
        logger.info(f"Playing morse code: {morse_code}")
        
        # Generate audio for morse code
        dot_duration = 0.1  # seconds
        dash_duration = dot_duration * 3
        pause_duration = dot_duration
        
        audio_segments = []
        
        for symbol in morse_code:
            if symbol == '.':
                # Generate dot sound
                duration = dot_duration
                tone = np.sin(2 * np.pi * 800 * np.arange(int(duration * self.sample_rate)) / self.sample_rate)
                audio_segments.append(tone.reshape(-1, 1))
            elif symbol == '-':
                # Generate dash sound
                duration = dash_duration
                tone = np.sin(2 * np.pi * 800 * np.arange(int(duration * self.sample_rate)) / self.sample_rate)
                audio_segments.append(tone.reshape(-1, 1))
            elif symbol == ' ':
                # Generate pause
                duration = pause_duration
                silence = np.zeros((int(duration * self.sample_rate), 1))
                audio_segments.append(silence)
        
        # Combine all segments
        audio_data = np.vstack(audio_segments)
        
        # Play the morse code audio
        self.play(audio_data)
    
    def stop(self):
        """Stop any current audio playback"""
        if self.playing:
            logger.info("Stopping audio playback")
            sd.stop()
            self.playing = False
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up AudioPlayer resources")
        # Stop any ongoing playback
        self.stop() 