
#!/usr/bin/env python3
"""
Coder Bridge - OpenClaw Integration for Coding Interface
Spawns the Coder sub-agent with persistent memory and handles communication.
"""

import json
import sys
import os
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("C:/Users/thadd/.openclaw/workspace")
AGENT_CONFIG = WORKSPACE / "agents/coder.md"
MEMORY_FILE = WORKSPACE / "agents/coder-memory.md"

def log(message):
    """Log to stderr for debugging"""
    print(f"[CoderBridge] {message}", file=sys.stderr, flush=True)

def read_memory():
    """Read the coder's persistent memory"""
    if MEMORY_FILE.exists():
        return MEMORY_FILE.read_text(encoding='utf-8')
    return "# No memory file yet"

def spawn_coder_agent(task: str, context: dict = None) -> dict:
    """
    Spawn the Coder sub-agent via OpenClaw.
    Returns the agent response.
    """
    # Prepare the spawn command
    # This uses OpenClaw's sessions_spawn functionality via the CLI
    
    full_prompt = f"""You are CODER, a general-purpose coding assistant with persistent memory.

MANDATORY FIRST ACTIONS:
1. Read your memory file: C:\Users\thadd\.openclaw\workspace\agents\coder-memory.md
2. Acknowledge what you read (briefly)
3. Execute the coding task below

TASK FROM USER:
{task}

AFTER COMPLETING:
- Update coder-memory.md with:
  - What you did
  - Files changed/created
  - Decisions and why
  - Any open issues or next steps
- End with "Done" or "Complete"

Remember: You are NOT Spock. You are CODER. Stay focused on coding only.
"""
    
    try:
        # Use openclaw CLI to spawn a subagent
        result = subprocess.run(
            [
                "openclaw", "sessions", "spawn",
                "--task", full_prompt,
                "--agent-id", "coder",
                "--model", "kimi-k2.5:cloud",
                "--thinking", "medium",
                "--timeout-seconds", "600",
                "--mode", "run",
                "--label", f"coder-session-{datetime.now().strftime('%H%M%S')}"
            ],
            capture_output=True,
            text=True,
            timeout=605
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "response": result.stdout,
                "session_id": extract_session_id(result.stdout)
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "stdout": result.stdout
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Agent timed out after 10 minutes"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def extract_session_id(output: str) -> str:
    """Extract session ID from spawn output"""
    # Look for patterns like "session:xxx" or similar
    import re
    match = re.search(r'session[\/:\s]+([\w-]+)', output, re.IGNORECASE)
    if match:
        return match.group(1)
    return "unknown"

def send_message_to_session(session_id: str, message: str) -> dict:
    """Send a follow-up message to an existing session"""
    try:
        result = subprocess.run(
            [
                "openclaw", "sessions", "send",
                "--session-key", f"session:{session_id}",
                "--message", message,
                "--timeout-seconds", "600"
            ],
            capture_output=True,
            text=True,
            timeout=605
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "response": result.stdout
            }
        else:
            return {
                "success": False,
                "error": result.stderr
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def check_session_status(session_id: str) -> dict:
    """Check if a session is still active"""
    try:
        result = subprocess.run(
            ["openclaw", "sessions", "list", "--limit", "20"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "active": session_id in result.stdout
            }
        return {"success": False, "error": "Failed to list sessions"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Coder Bridge for OpenClaw")
    parser.add_argument("command", choices=["spawn", "send", "status", "memory"])
    parser.add_argument("--task", help="Task for spawn command")
    parser.add_argument("--session-id", help="Session ID for send/status")
    parser.add_argument("--message", help="Message for send command")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    if args.command == "spawn":
        if not args.task:
            print("Error: --task required for spawn", file=sys.stderr)
            sys.exit(1)
        
        result = spawn_coder_agent(args.task)
        
        if args.json:
            print(json.dumps(result))
        else:
            if result["success"]:
                print(f"✓ Agent spawned successfully")
                print(f"Session ID: {result.get('session_id', 'unknown')}")
                print("\n" + "="*50)
                print(result["response"])
            else:
                print(f"✗ Failed to spawn agent")
                print(f"Error: {result.get('error', 'Unknown error')}")
                if result.get('stdout'):
                    print("\nOutput:")
                    print(result['stdout'])
                sys.exit(1)
    
    elif args.command == "send":
        if not args.session_id or not args.message:
            print("Error: --session-id and --message required", file=sys.stderr)
            sys.exit(1)
        
        result = send_message_to_session(args.session_id, args.message)
        
        if args.json:
            print(json.dumps(result))
        else:
            if result["success"]:
                print(result["response"])
            else:
                print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
                sys.exit(1)
    
    elif args.command == "status":
        if not args.session_id:
            print("Error: --session-id required", file=sys.stderr)
            sys.exit(1)
        
        result = check_session_status(args.session_id)
        print(json.dumps(result))
    
    elif args.command == "memory":
        print(read_memory())

if __name__ == "__main__":
    main()
