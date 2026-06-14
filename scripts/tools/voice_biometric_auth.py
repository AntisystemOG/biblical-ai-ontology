#!/usr/bin/env python3
"""
Voice Biometric Authentication System
Verifies Thad's identity via speaker verification
Uses ECAPA-TDNN for speaker embedding comparison
"""

import torch
import torchaudio
from speechbrain.pretrained import SpeakerRecognition
from pathlib import Path
import json
from datetime import datetime

# Configuration
BIOMETRIC_DIR = Path(r"C:\Users\thada\OneDrive\Desktop\Spocks Reports\biometric_data")
REFERENCE_AUDIO = BIOMETRIC_DIR / "thad_reference_audio.wav"
VERIFICATION_LOG = BIOMETRIC_DIR / "verification_log.json"
SIMILARITY_THRESHOLD = 0.95  # 95% match required

class VoiceBiometricAuth:
    def __init__(self):
        self.biometric_dir = BIOMETRIC_DIR
        self.biometric_dir.mkdir(parents=True, exist_ok=True)
        
        print("[Initializing] Voice Biometric System...")
        try:
            # Load pretrained speaker verification model
            self.model = SpeakerRecognition.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb",
                savedir="pretrained_models/spkrec-ecapa-voxceleb",
                run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
            )
            print("[OK] ECAPA-TDNN model loaded")
        except Exception as e:
            print(f"[ERROR] Failed to load model: {str(e)}")
            self.model = None
    
    def set_reference_audio(self, audio_file_path):
        """
        Set reference audio sample (Thad's voice)
        audio_file_path: path to WAV file of Thad saying passphrase
        """
        try:
            audio_path = Path(audio_file_path)
            if not audio_path.exists():
                return {"success": False, "message": f"Audio file not found: {audio_file_path}"}
            
            # Copy reference to biometric directory
            import shutil
            shutil.copy(audio_path, REFERENCE_AUDIO)
            
            self.log_action("reference_audio_set", f"Reference set from {audio_file_path}")
            return {"success": True, "message": "Reference audio set successfully"}
        
        except Exception as e:
            return {"success": False, "message": f"Error setting reference: {str(e)}"}
    
    def verify_speaker(self, test_audio_file_path):
        """
        Verify if speaker in test_audio matches reference (Thad)
        Returns: {"verified": bool, "similarity": float, "message": str}
        """
        try:
            if not self.model:
                return {"verified": False, "similarity": 0, "message": "Model not loaded"}
            
            if not REFERENCE_AUDIO.exists():
                return {"verified": False, "similarity": 0, "message": "Reference audio not set. Run set_reference_audio() first"}
            
            test_path = Path(test_audio_file_path)
            if not test_path.exists():
                return {"verified": False, "similarity": 0, "message": f"Test audio file not found: {test_audio_file_path}"}
            
            # Load and verify
            score, prediction = self.model.verify_files(
                str(REFERENCE_AUDIO),
                str(test_path)
            )
            
            similarity = float(score)
            verified = similarity >= SIMILARITY_THRESHOLD
            
            self.log_action(
                "speaker_verification",
                {"similarity": similarity, "verified": verified, "test_file": str(test_path)}
            )
            
            return {
                "verified": verified,
                "similarity": round(similarity, 4),
                "threshold": SIMILARITY_THRESHOLD,
                "message": f"Speaker {'verified' if verified else 'NOT verified'} ({similarity:.2%} match)"
            }
        
        except Exception as e:
            self.log_action("verification_error", str(e))
            return {"verified": False, "similarity": 0, "message": f"Verification error: {str(e)}"}
    
    def log_action(self, action, details):
        """Log security events"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        
        # Load existing log
        log_data = []
        if VERIFICATION_LOG.exists():
            with open(VERIFICATION_LOG, 'r') as f:
                log_data = json.load(f)
        
        log_data.append(event)
        
        # Save updated log
        with open(VERIFICATION_LOG, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def get_verification_status(self):
        """Check if system is ready"""
        if not self.model:
            return {"ready": False, "reason": "Model not loaded"}
        
        if not REFERENCE_AUDIO.exists():
            return {"ready": False, "reason": "Reference audio not set"}
        
        return {"ready": True, "reason": "System ready for verification"}

# Singleton instance
_auth = None

def get_voice_auth():
    """Get or create voice auth system"""
    global _auth
    if _auth is None:
        _auth = VoiceBiometricAuth()
    return _auth

# Test when run directly
if __name__ == "__main__":
    auth = get_voice_auth()
    status = auth.get_verification_status()
    print(f"Status: {status}")
