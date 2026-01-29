"""
Voice Input Handler
Captures audio from microphone for speech-to-text processing
"""

import os
import wave
from pathlib import Path
from typing import Optional
from datetime import datetime


class VoiceInputHandler:
    """
    Handles audio capture from microphone
    
    Requires: pyaudio (audio interface)
    
    Example:
        handler = VoiceInputHandler()
        audio_file = handler.record_audio(duration=10)
    """
    
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024):
        """
        Initialize voice input handler
        
        Args:
            sample_rate: Audio sample rate (Hz) - 16000 is standard for speech
            chunk_size: Audio chunk size for buffering
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio_dir = Path("audio_cache")
        self.audio_dir.mkdir(exist_ok=True)
        
        self.pyaudio = None
        self.stream = None
    
    def _init_pyaudio(self):
        """Lazy initialization of PyAudio"""
        if self.pyaudio is None:
            try:
                import pyaudio
                self.pyaudio = pyaudio.PyAudio()
            except ImportError:
                raise ImportError(
                    "pyaudio not installed. Install with: pip install pyaudio"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to initialize PyAudio: {e}")
    
    def record_audio(
        self,
        duration: int = 10,
        channels: int = 1,
        format_type: int = None
    ) -> str:
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds (max 60)
            channels: Number of audio channels (1=mono, 2=stereo)
            format_type: PyAudio format (None = paInt16)
            
        Returns:
            Path to saved WAV file
            
        Raises:
            ValueError: If duration exceeds limits
            RuntimeError: If recording fails
        """
        if duration < 1 or duration > 60:
            raise ValueError("Duration must be between 1 and 60 seconds")
        
        self._init_pyaudio()
        
        # Use paInt16 format for better speech recognition
        if format_type is None:
            format_type = self.pyaudio.get_format_from_width(2)  # 2 bytes per sample
        
        try:
            print(f"🎤 Starting recording for {duration} seconds...")
            
            # Open audio stream
            stream = self.pyaudio.open(
                format=format_type,
                channels=channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            # Record audio
            frames = []
            for i in range(int(self.sample_rate / self.chunk_size * duration)):
                data = stream.read(self.chunk_size)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            print("✅ Recording complete!")
            
            # Save to WAV file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = self.audio_dir / f"recording_{timestamp}.wav"
            
            with wave.open(str(audio_file), 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(self.pyaudio.get_sample_size(format_type))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            print(f"📁 Saved to: {audio_file}")
            return str(audio_file)
            
        except Exception as e:
            raise RuntimeError(f"Recording failed: {e}")
    
    def record_async(self, duration: int = 10):
        """
        Non-blocking audio recording (for Streamlit)
        
        Args:
            duration: Recording duration
            
        Returns:
            File path (when recording completes)
        """
        try:
            import streamlit as st
            
            # Streamlit audio recorder widget
            audio_bytes = st.audio_input("🎤 Click to record your symptoms")
            
            if audio_bytes:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audio_file = self.audio_dir / f"streamlit_recording_{timestamp}.wav"
                
                with open(audio_file, "wb") as f:
                    f.write(audio_bytes.getbuffer())
                
                return str(audio_file)
            
            return None
            
        except ImportError:
            raise ImportError("Streamlit not available. Use record_audio() instead.")
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.pyaudio:
            self.pyaudio.terminate()
    
    def get_audio_files(self) -> list:
        """
        Get list of recorded audio files
        
        Returns:
            List of audio file paths
        """
        return sorted(self.audio_dir.glob("*.wav"))
    
    def delete_audio_file(self, filepath: str):
        """
        Delete an audio file
        
        Args:
            filepath: Path to audio file
        """
        try:
            Path(filepath).unlink()
            print(f"Deleted: {filepath}")
        except Exception as e:
            print(f"Failed to delete {filepath}: {e}")
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.cleanup()
