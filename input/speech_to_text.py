"""
Speech-to-Text Processor
Uses Hugging Face Whisper model for converting audio to text
Optimized for CPU with whisper-small model via transformers library
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import warnings
import numpy as np


class SpeechToTextProcessor:
    """
    Converts audio files to text using Whisper
    
    Model Options:
    - whisper-tiny: ~39M parameters (fastest, CPU-friendly) ⚡
    - whisper-base: ~74M parameters (balanced)
    - whisper-small: ~244M parameters (recommended for CPU) ✅
    - whisper-medium: ~769M parameters (GPU recommended)
    - whisper-large: ~1.5B parameters (GPU required)
    
    For CPU: Use whisper-small (good accuracy, manageable speed)
    
    Example:
        processor = SpeechToTextProcessor(model_name="whisper-small")
        text = processor.transcribe("audio.wav")
    """
    
    AVAILABLE_MODELS = {
        "tiny": {"size": "39M", "speed": "very fast", "device": "CPU"},
        "base": {"size": "74M", "speed": "fast", "device": "CPU"},
        "small": {"size": "244M", "speed": "moderate", "device": "CPU"},  # Recommended
        "medium": {"size": "769M", "speed": "slow", "device": "GPU recommended"},
        "large": {"size": "1.5B", "speed": "very slow", "device": "GPU required"},
    }
    
    def __init__(self, model_name: str = "small", device: str = "cpu"):
        """
        Initialize Whisper processor
        
        Args:
            model_name: Model size ("tiny", "base", "small", "medium", "large")
                       Default: "small" (best for CPU)
            device: Device to use ("cpu" or "cuda")
            
        Raises:
            ValueError: If invalid model name
            ImportError: If whisper not installed
        """
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(
                f"Invalid model: {model_name}. "
                f"Choose from: {list(self.AVAILABLE_MODELS.keys())}"
            )
        
        self.model_name = model_name
        self.device = device
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model from Hugging Face with proper error handling"""
        try:
            from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
            import torch
        except ImportError:
            raise ImportError(
                "transformers or torch not installed. Install with: pip install transformers torch"
            )
        
        try:
            model_id = f"openai/whisper-{self.model_name}"
            print(f"📥 Loading {model_id} ({self.AVAILABLE_MODELS[self.model_name]['size']})...")
            
            # Load processor and model from Hugging Face
            self.processor = AutoProcessor.from_pretrained(model_id)
            
            # Set device
            if self.device == "cuda" and torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
            
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id,
                torch_dtype=torch.float32,  # Use float32 for CPU compatibility
                low_cpu_mem_usage=True,
                use_safetensors=True
            )
            self.model.to(device)
            self.model.eval()
            
            self.device = device
            print(f"✅ Model loaded successfully on {self.device.upper()}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {e}")
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        verbose: bool = False
    ) -> str:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
            language: Language code (e.g., "en", "hi") or None for auto-detect
            verbose: Print progress information
            
        Returns:
            Transcribed text
            
        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If transcription fails
        """
        import torchaudio
        import torch
        
        audio_file = Path(audio_path)
        
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            print(f"🎵 Transcribing: {audio_file.name}")
            
            # Load audio
            waveform, sample_rate = torchaudio.load(str(audio_file))
            
            # Resample to 16kHz if necessary
            if sample_rate != 16000:
                resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                waveform = resampler(waveform)
                sample_rate = 16000
            
            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)
            
            # Squeeze to 1D
            waveform = waveform.squeeze()
            
            # Process input
            inputs = self.processor(
                waveform,
                sampling_rate=sample_rate,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate transcription
            with torch.no_grad():
                predicted_ids = self.model.generate(
                    inputs["input_features"],
                    max_length=225,
                    num_beams=5,
                    early_stopping=True
                )
            
            # Decode
            text = self.processor.batch_decode(
                predicted_ids,
                skip_special_tokens=True
            )[0]
            
            text = text.strip()
            print(f"✅ Transcription complete")
            
            return text
            
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")
    
    def transcribe_with_details(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio and return detailed results
        
        Args:
            audio_path: Path to audio file
            language: Language code or None
            
        Returns:
            Dictionary with:
            - text: Transcribed text
            - segments: List of segments with timestamps
            - language: Detected language
        """
        import torchaudio
        import torch
        
        audio_file = Path(audio_path)
        
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            # Load audio
            waveform, sample_rate = torchaudio.load(str(audio_file))
            
            # Resample to 16kHz if necessary
            if sample_rate != 16000:
                resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                waveform = resampler(waveform)
                sample_rate = 16000
            
            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)
            
            # Squeeze to 1D
            waveform = waveform.squeeze()
            
            # Process input
            inputs = self.processor(
                waveform,
                sampling_rate=sample_rate,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate transcription
            with torch.no_grad():
                predicted_ids = self.model.generate(
                    inputs["input_features"],
                    max_length=225
                )
            
            # Decode
            text = self.processor.batch_decode(
                predicted_ids,
                skip_special_tokens=True
            )[0]
            
            return {
                "text": text.strip(),
                "segments": [],  # Timestamps not available with this API
                "language": language or "en",
            }
            
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")
    
    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about current model
        
        Returns:
            Dictionary with model specifications
        """
        info = self.AVAILABLE_MODELS[self.model_name].copy()
        info["name"] = self.model_name
        info["device"] = self.device
        return info
    
    @staticmethod
    def get_available_models() -> Dict[str, Dict[str, str]]:
        """
        Get information about all available models
        
        Returns:
            Dictionary with all model specifications
        """
        return SpeechToTextProcessor.AVAILABLE_MODELS.copy()
    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"SpeechToTextProcessor(model=whisper-{self.model_name}, "
            f"device={self.device})"
        )


# Streamlit-compatible wrapper
def streamlit_transcribe(audio_file_path: str, model_name: str = "small") -> Optional[str]:
    """
    Streamlit-compatible transcription function
    
    Args:
        audio_file_path: Path to audio file
        model_name: Whisper model to use
        
    Returns:
        Transcribed text or None if error
    """
    try:
        processor = SpeechToTextProcessor(model_name=model_name, device="cpu")
        return processor.transcribe(audio_file_path, verbose=False)
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None


# Quick-start helper
def quick_transcribe(audio_path: str) -> str:
    """
    Quick transcription with whisper-small (CPU-optimized)
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Transcribed text
    """
    processor = SpeechToTextProcessor(model_name="small", device="cpu")
    return processor.transcribe(audio_path)


def load_audio_for_model(audio_path: str, target_sr: int = 16000) -> tuple:
    """
    Load and preprocess audio file for Whisper model
    
    Args:
        audio_path: Path to audio file
        target_sr: Target sample rate (default: 16000 Hz for Whisper)
        
    Returns:
        Tuple of (waveform, sample_rate)
    """
    try:
        import torchaudio
        
        waveform, sr = torchaudio.load(str(audio_path))
        
        # Resample if needed
        if sr != target_sr:
            resampler = torchaudio.transforms.Resample(sr, target_sr)
            waveform = resampler(waveform)
            sr = target_sr
        
        # Convert to mono
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        
        return waveform.squeeze(), sr
        
    except ImportError:
        raise ImportError("torchaudio not installed. Install with: pip install torchaudio")
