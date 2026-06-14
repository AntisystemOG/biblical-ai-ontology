#!/usr/bin/env python3
"""
Analyze why work PC shut down unexpectedly at 6:05 AM on 2026-02-24
"""

import requests

OLLAMA = "http://localhost:11434/api/generate"

prompt = """
A Windows 10 PC shut down unexpectedly at 6:05 AM on February 24, 2026.

EVENT LOG DATA:
- Event ID 6008: "The previous system shutdown was UNEXPECTED"
- Event ID 1074: "RuntimeBroker.exe has initiated the power action"
- Multiple RuntimeBroker restart events in history
- No external wake source detected
- PC was idle (running background Python script for investment research)

CONTEXT:
- A background research script was running (investment analysis via Ollama)
- PC was supposed to stay on for idle-time learning
- User found PC off when waking up

ANALYSIS NEEDED:
1. What most likely caused this shutdown?
2. Was it automatic Windows system action, or external?
3. Is this preventable for future background tasks?
4. What's the recommendation?

Possible causes:
- Windows Update with auto-restart
- Scheduled task/maintenance
- RuntimeBroker service crash causing restart
- Power settings (sleep → shutdown)
- Windows Defender scan with restart
- Disk cleanup or defrag

Be specific and diagnostic. What actually happened here?
"""

try:
    print("[Analyzing shutdown event...]")
    response = requests.post(
        OLLAMA,
        json={"model": "mistral", "prompt": prompt, "stream": False},
        timeout=120
    )
    
    if response.status_code == 200:
        analysis = response.json()["response"]
        report = f"""
SHUTDOWN INVESTIGATION REPORT
Generated: 2026-02-24
PC: DESKTOP-2TDTEHU

EVENT LOG SUMMARY:
- Shutdown time: 6:05:10 AM
- Type: UNEXPECTED (Event 6008)
- Initiated by: RuntimeBroker.exe
- User: System

ANALYSIS:
{analysis}

RECOMMENDATION FOR FUTURE:
- Adjust Windows Update settings if applicable
- Check power settings for sleep/shutdown timers
- Use Windows Task Scheduler to prevent updates during research sessions
- Consider pinning power state during background tasks

Report prepared by Spock
"""
        
        with open("shutdown_analysis_report.txt", "w") as f:
            f.write(report)
        
        print(report)
        print("\n[Report saved to: shutdown_analysis_report.txt]")
    else:
        print(f"Ollama error: {response.status_code}")

except Exception as e:
    print(f"Connection error: {str(e)}")
    print("\nFallback Analysis:")
    print("Most likely cause: Windows Update auto-restart OR scheduled maintenance")
    print("Evidence: RuntimeBroker.exe is Windows system process (not user-initiated)")
    print("Solution: Check Windows Update settings, disable auto-restart for research tasks")
