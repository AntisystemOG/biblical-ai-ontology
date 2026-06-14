"""
Idle Monitor System
Detects when Thad stops using PC and automatically starts learning tasks.
Saves findings to Spocks Reports.

Features:
- 5-minute idle threshold
- Auto-starts learning with Ollama Mistral
- Pauses when activity detected
- Saves results to OneDrive\Desktop\Spocks Reports
- Topics: Chuck Missler, Bible study, theology, investing
"""

import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
import threading

# Configuration
IDLE_THRESHOLD_SECONDS = 300  # 5 minutes
REPORTS_DIR = Path.home() / "OneDrive" / "Desktop" / "Spocks Reports"
LEARNING_LOG = REPORTS_DIR / "learning_log.json"

# Learning topics prioritized
LEARNING_TOPICS = [
    "Chuck Missler methodology",
    "Bible study (Genesis deep dive)",
    "Christian theology & prophecy",
    "Investing psychology",
    "Financial independence strategies",
    "Integration of knowledge systems"
]

class IdleMonitor:
    """Monitor system idle time and trigger learning tasks"""
    
    def __init__(self):
        self.running = False
        self.idle_start = None
        self.learning_active = False
        self.monitor_thread = None
        
    def get_idle_time(self) -> float:
        """Get system idle time in seconds"""
        try:
            # Windows-specific: use GetLastInputInfo
            import ctypes
            from ctypes import Structure, windll, c_uint, sizeof, byref
            
            class LASTINPUTINFO(Structure):
                _fields_ = [
                    ("cbSize", c_uint),
                    ("dwTime", c_uint),
                ]
            
            user32 = windll.user32
            lii = LASTINPUTINFO()
            lii.cbSize = sizeof(LASTINPUTINFO)
            user32.GetLastInputInfo(byref(lii))
            
            millis = windll.kernel32.GetTickCount() - lii.dwTime
            return millis / 1000.0
        except Exception:
            # Fallback: check if we can detect idle differently
            return 0
    
    def start_monitoring(self):
        """Start the idle monitoring loop"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("Idle monitor started")
    
    def stop_monitoring(self):
        """Stop the idle monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("Idle monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            idle_time = self.get_idle_time()
            
            if idle_time >= IDLE_THRESHOLD_SECONDS and not self.learning_active:
                # Thad is idle, start learning
                self._start_learning()
            elif idle_time < IDLE_THRESHOLD_SECONDS and self.learning_active:
                # Thad is back, pause learning
                self._pause_learning()
            
            time.sleep(10)  # Check every 10 seconds
    
    def _start_learning(self):
        """Trigger learning task"""
        self.learning_active = True
        self.idle_start = datetime.now()
        
        topic = self._select_topic()
        print(f"Learning started: {topic}")
        
        # In actual implementation, would call Ollama here
        # For now, just log it
        self._log_learning(topic, "started")
        
        # Example: Call Ollama for learning
        # self._run_learning_prompt(topic)
    
    def _pause_learning(self):
        """Pause learning when user returns"""
        if self.learning_active:
            duration = (datetime.now() - self.idle_start).total_seconds() if self.idle_start else 0
            print(f"Learning paused after {duration:.0f} seconds (Thad returned)")
            self._log_learning("", f"paused after {duration:.0f}s")
            self.learning_active = False
    
    def _select_topic(self) -> str:
        """Select learning topic (rotate through list)"""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        state_file = REPORTS_DIR / ".learning_state.json"
        
        if state_file.exists():
            state = json.loads(state_file.read_text())
            last_index = state.get("last_topic_index", -1)
        else:
            last_index = -1
        
        next_index = (last_index + 1) % len(LEARNING_TOPICS)
        
        state = {"last_topic_index": next_index, "last_run": datetime.now().isoformat()}
        state_file.write_text(json.dumps(state))
        
        return LEARNING_TOPICS[next_index]
    
    def _run_learning_prompt(self, topic: str):
        """Run Ollama learning prompt"""
        prompt = f"""Research topic: {topic}
        
Provide insights, connections to other knowledge areas, and practical applications.
Structure your response with clear sections."""
        
        try:
            # Call Ollama via subprocess
            result = subprocess.run(
                ["ollama", "run", "mistral", prompt],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute max
            )
            
            self._save_learning_result(topic, result.stdout)
        except Exception as e:
            print(f"Learning task failed: {e}")
    
    def _save_learning_result(self, topic: str, result: str):
        """Save learning result to file"""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"learning_{timestamp}_{topic.replace(' ', '_')[:20]}.txt"
        
        filepath = REPORTS_DIR / filename
        filepath.write_text(f"Topic: {topic}\n\n{result}")
        print(f"Learning saved: {filepath}")
    
    def _log_learning(self, topic: str, status: str):
        """Log learning activity"""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "status": status
        }
        
        if LEARNING_LOG.exists():
            logs = json.loads(LEARNING_LOG.read_text())
        else:
            logs = []
        
        logs.append(log_entry)
        LEARNING_LOG.write_text(json.dumps(logs, indent=2))

# Global instance
_monitor = None

def start():
    """Start idle monitoring"""
    global _monitor
    _monitor = IdleMonitor()
    _monitor.start_monitoring()

def stop():
    """Stop idle monitoring"""
    global _monitor
    if _monitor:
        _monitor.stop_monitoring()

def status() -> str:
    """Get current monitor status"""
    if _monitor:
        return f"Running: {_monitor.running}, Learning active: {_monitor.learning_active}"
    return "Not started"

if __name__ == "__main__":
    print("Idle Monitor System")
    print(f"Reports dir: {REPORTS_DIR}")
    print(f"Idle threshold: {IDLE_THRESHOLD_SECONDS}s")
    print("\nRun start() to begin monitoring")
