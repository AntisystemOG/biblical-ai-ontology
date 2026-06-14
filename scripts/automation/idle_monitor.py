#!/usr/bin/env python3
"""
Idle Monitor - Detects when PC is idle and triggers learning tasks
Monitors keyboard/mouse activity
Runs background learning when idle
Reports findings daily
"""

import time
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from pynput import mouse, keyboard
import threading

# Configuration
IDLE_THRESHOLD_MINUTES = 5
REPORTS_DIR = Path(r"C:\Users\thada\OneDrive\Desktop\Spocks Reports")
LEARNING_QUEUE_FILE = REPORTS_DIR / "learning_queue.json"
IDLE_STATE_FILE = REPORTS_DIR / "idle_state.json"

# Learning topics (prioritized)
LEARNING_TOPICS = [
    {"name": "Chuck Missler Methodology", "priority": 1, "status": "pending"},
    {"name": "Bible Study: Genesis", "priority": 2, "status": "pending"},
    {"name": "Christian Theology & Prophecy", "priority": 3, "status": "pending"},
    {"name": "Investing Psychology", "priority": 4, "status": "pending"},
    {"name": "Financial Independence Strategies", "priority": 5, "status": "pending"},
    {"name": "Integration of Knowledge Systems", "priority": 6, "status": "pending"},
]

class IdleMonitor:
    def __init__(self):
        self.last_activity = datetime.now()
        self.is_idle = False
        self.learning_active = False
        self.current_topic = None
        self.last_learning_start = None
        self.min_learning_interval = 300  # Don't start new task for 5 minutes after last one
        
    def on_move(self, x, y):
        """Mouse moved - reset idle timer"""
        self.last_activity = datetime.now()
        if self.is_idle:
            self.stop_learning()
            
    def on_press(self, key):
        """Key pressed - reset idle timer"""
        self.last_activity = datetime.now()
        if self.is_idle:
            self.stop_learning()
    
    def check_idle(self):
        """Check if PC is idle"""
        time_idle = datetime.now() - self.last_activity
        idle_minutes = time_idle.total_seconds() / 60
        
        if idle_minutes >= IDLE_THRESHOLD_MINUTES and not self.is_idle:
            self.is_idle = True
            self.start_learning()
            print(f"[{datetime.now().isoformat()}] PC idle. Starting learning task.")
            
        elif idle_minutes < IDLE_THRESHOLD_MINUTES and self.is_idle:
            self.is_idle = False
            self.stop_learning()
            print(f"[{datetime.now().isoformat()}] Activity detected. Stopping learning.")
    
    def start_learning(self):
        """Start a background learning task"""
        if self.learning_active:
            return
        
        # Don't start if too soon since last learning
        if self.last_learning_start:
            time_since_last = (datetime.now() - self.last_learning_start).total_seconds()
            if time_since_last < self.min_learning_interval:
                return
        
        self.learning_active = True
        self.last_learning_start = datetime.now()
        topic = self.get_next_topic()
        self.current_topic = topic
        
        # Start learning task in background thread
        thread = threading.Thread(
            target=self.run_learning_task,
            args=(topic,),
            daemon=True
        )
        thread.start()
        
        print(f"[{datetime.now().isoformat()}] Learning started: {topic['name']}")
    
    def stop_learning(self):
        """Stop learning task"""
        if self.learning_active:
            self.learning_active = False
            print(f"[{datetime.now().isoformat()}] Learning paused (activity detected)")
    
    def get_next_topic(self):
        """Get next topic to learn"""
        # Find first pending topic, or rotate through completed
        for topic in LEARNING_TOPICS:
            if topic['status'] == 'pending':
                return topic
        
        # If all done, reset and pick first
        for topic in LEARNING_TOPICS:
            topic['status'] = 'pending'
        return LEARNING_TOPICS[0]
    
    def run_learning_task(self, topic):
        """Execute learning task for a topic"""
        try:
            # Call learning script
            result = self.execute_ollama_learning(topic)
            
            # Mark topic as done
            topic['status'] = 'completed'
            
            # Save result
            self.save_learning_result(topic, result)
            
        except Exception as e:
            print(f"[ERROR] Learning task failed: {str(e)}")
    
    def execute_ollama_learning(self, topic):
        """Query Ollama for learning"""
        import requests
        import time
        
        prompt = self.generate_learning_prompt(topic['name'])
        
        try:
            # Add delay to avoid hammering Ollama
            time.sleep(2)
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                },
                timeout=300  # 5 minute timeout (was 10)
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return f"Error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            print(f"[WARNING] Ollama request timeout for {topic['name']}")
            return "Request timeout - Ollama may be busy"
        except requests.exceptions.ConnectionError:
            print(f"[WARNING] Cannot connect to Ollama")
            return "Cannot connect to Ollama"
        except Exception as e:
            return f"Connection failed: {str(e)}"
    
    def generate_learning_prompt(self, topic):
        """Generate learning prompt based on topic"""
        prompts = {
            "Chuck Missler Methodology": """
                Deep dive into Chuck Missler's methodology for Bible study.
                Key areas:
                1. How he approaches prophetic interpretation
                2. His method for connecting Scripture across books
                3. How he integrates historical/cultural context
                4. His approach to finding "hidden treasures" in biblical text
                
                Provide actionable insights that could inform Bible study approach.
                Be specific and methodological.
            """,
            "Bible Study: Genesis": """
                Detailed analysis of Genesis chapters 1-5.
                Focus on:
                1. Theological themes (creation, fall, redemption arc)
                2. Historical-cultural context
                3. Connections to New Testament (Jesus as fulfillment)
                4. Prophetic elements (if any)
                5. Key lessons for modern application
                
                Use Chuck Missler's methodology as lens.
            """,
            "Christian Theology & Prophecy": """
                Explore connections between theology and prophecy.
                1. How does prophecy function in Scripture?
                2. What's the relationship between fulfillment and interpretation?
                3. How do major Bible teachers (like Missler) approach prophecy?
                4. What's the Christian Zionist perspective?
                
                Be theological and practical.
            """,
            "Investing Psychology": """
                Why do investors fail? Psychological barriers to wealth-building.
                1. Emotional biases (fear, greed, FOMO)
                2. Common mistakes (timing market, chasing hot stocks)
                3. How to build psychological resilience
                4. Long-term thinking vs. short-term stress
                
                Apply to someone building wealth over 15-25 years.
            """,
            "Financial Independence Strategies": """
                Detailed strategies for reaching financial independence.
                1. Tax-advantaged account optimization
                2. Asset allocation for different life stages
                3. Passive income strategies
                4. Real estate vs. stocks vs. bonds
                5. Timeline-specific planning
                
                Focus on boring, consistent wealth-building.
            """,
            "Integration of Knowledge Systems": """
                How do different knowledge domains connect?
                1. How does faith inform financial decisions?
                2. How does theology integrate with science?
                3. How does history inform prophecy?
                4. System thinking across disciplines
                
                This is how Chuck Missler thought - integrated, not compartmentalized.
            """
        }
        
        return prompts.get(topic, f"Deep research on: {topic}")
    
    def save_learning_result(self, topic, result):
        """Save learning result to file"""
        timestamp = datetime.now().isoformat()
        filename = REPORTS_DIR / f"learning_{topic['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        content = f"""
LEARNING TASK REPORT
====================
Topic: {topic['name']}
Date: {timestamp}
Duration: Started when idle, paused when activity detected

FINDINGS:
{result}

---
Generated by Spock Idle Monitor
"""
        
        with open(filename, 'w', encoding='utf-8', errors='replace') as f:
            f.write(content)
        
        print(f"[{timestamp}] Learning saved: {filename}")
    
    def start_monitoring(self):
        """Start monitoring keyboard/mouse"""
        print("[Starting] Idle Monitor")
        print(f"[Config] Idle threshold: {IDLE_THRESHOLD_MINUTES} minutes")
        
        # Listen for mouse
        mouse_listener = mouse.Listener(on_move=self.on_move)
        mouse_listener.start()
        
        # Listen for keyboard
        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        keyboard_listener.start()
        
        # Check idle status every 60 seconds
        try:
            while True:
                self.check_idle()
                time.sleep(60)  # Check every 60 seconds (was 30)
        except KeyboardInterrupt:
            print("\n[Stopped] Idle Monitor")

if __name__ == "__main__":
    monitor = IdleMonitor()
    monitor.start_monitoring()
