"""
Voice Biometric Authentication System
Uses ECAPA-TDNN speaker verification to authenticate Thad's voice before sensitive actions.

Requirements:
- pip install speechbrain pyannote.audio torch torchaudio
- Reference audio recording of Thad saying passphrase

Security: 95%+ voice similarity required before sensitive actions.
Offline: Runs fully local, no cloud dependency.
"""

import torch
import torchaudio
from pathlib import Path
from speechbrain.pretrained import EncoderClassifier
import numpy as np

# Configuration
REFERENCE_AUDIO = Path(__file__).parent / "data" / "thad_voice_reference.wav"
BIOMETRIC_LOG = Path(__file__).parent / ".." / ".." / "OneDrive" / "Desktop" / "Spocks Reports" / "biometric_data"
SIMILARITY_THRESHOLD = 0.95

class VoiceAuthenticator:
    """Voice biometric authentication using ECAPA-TDNN"""
    
    def __init__(self):
        self.model = None
        self.reference_embedding = None
        self._load_model()
    
    def _load_model(self):
        """Load ECAPA-TDNN model (first time only)"""
        try:
            self.model = EncoderClassifier.from_hparams(
                source="speechbrain/ecapa-voxceleb"
            )
            print("Voice model loaded successfully")
        except Exception as e:
            print(f"Error loading voice model: {e}")
            self.model = None
    
    def _extract_embedding(self, audio_path: Path) -> np.ndarray:
        """Extract voice embedding from audio file"""
        if self.model is None:
            raise RuntimeError("Voice model not loaded")
        
        # Load audio
        signal, fs = torchaudio.load(str(audio_path))
        
        # Extract embedding
        with torch.no_grad():
            embedding = self.model.encode_batch(signal)
        
        return embedding.squeeze().numpy()
    
    def enroll(self, audio_path: Path) -> bool:
        """
        Enroll Thad's voice from reference audio.
        Run once to create reference embedding.
        """
        if not audio_path.exists():
            print(f"Reference audio not found: {audio_path}")
            return False
        
        try:
            self.reference_embedding = self._extract_embedding(audio_path)
            
            # Save reference embedding
            BIOMETRIC_LOG.mkdir(parents=True, exist_ok=True)
            np.save(BIOMETRIC_LOG / "reference_embedding.npy", self.reference_embedding)
            
            print(f"Voice enrolled successfully: {audio_path}")
            return True
        except Exception as e:
            print(f"Enrollment failed: {e}")
            return False
    
    def authenticate(self, audio_path: Path) -> tuple[bool, float]:
        """
        Authenticate voice sample against reference.
        
        Returns:
            (authenticated: bool, similarity: float)
        """
        if self.reference_embedding is None:
            # Try to load saved reference
            ref_file = BIOMETRIC_LOG / "reference_embedding.npy"
            if ref_file.exists():
                self.reference_embedding = np.load(ref_file)
            else:
                print("No reference voice enrolled. Run enroll() first.")
                return False, 0.0
        
        try:
            # Extract embedding from test audio
            test_embedding = self._extract_embedding(audio_path)
            
            # Calculate cosine similarity
            similarity = np.dot(self.reference_embedding, test_embedding) / (
                np.linalg.norm(self.reference_embedding) * np.linalg.norm(test_embedding)
            )
            
            # Log attempt
            self._log_attempt(audio_path, similarity)
            
            authenticated = similarity >= SIMILARITY_THRESHOLD
            return authenticated, float(similarity)
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return False, 0.0
    
    def _log_attempt(self, audio_path: Path, similarity: float):
        """Log authentication attempt"""
        BIOMETRIC_LOG.mkdir(parents=True, exist_ok=True)
        log_file = BIOMETRIC_LOG / "auth_log.txt"
        
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        status = "PASS" if similarity >= SIMILARITY_THRESHOLD else "FAIL"
        
        with open(log_file, "a") as f:
            f.write(f"{timestamp} | {status} | Similarity: {similarity:.4f}\n")

def require_voice_auth(func):
    """Decorator to require voice authentication before sensitive function"""
    def wrapper(*args, **kwargs):
        auth = VoiceAuthenticator()
        
        # In real use, would record audio here
        # For now, placeholder - assumes audio file path passed
        if "auth_audio" not in kwargs:
            print("ERROR: Voice authentication required but no audio provided")
            return None
        
        authenticated, similarity = auth.authenticate(Path(kwargs.pop("auth_audio")))
        
        if authenticated:
            return func(*args, **kwargs)
        else:
            print(f"Authentication failed (similarity: {similarity:.2%})")
            return None
    
    return wrapper

# Example usage
if __name__ == "__main__":
    auth = VoiceAuthenticator()
    
    # To enroll:
    # auth.enroll(Path("path/to/thad_voice_sample.wav"))
    
    # To authenticate:
    # authenticated, similarity = auth.authenticate(Path("path/to/test_sample.wav"))
    # print(f"Authenticated: {authenticated}, Similarity: {similarity:.2%}")
    
    print("Voice biometric system ready")
