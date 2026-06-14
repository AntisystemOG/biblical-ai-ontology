#!/usr/bin/env python3
"""
Coder Interface Server - Hosts the web UI and bridges to OpenClaw
"""

import http.server
import socketserver
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

PORT = 18790
WORKSPACE = Path("C:/Users/thadd/.openclaw/workspace")
MEMORY_FILE = WORKSPACE / "agents/coder-memory.md"

class CoderHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/api/memory":
            self.send_json({"content": read_memory()})
        elif parsed.path == "/api/check":
            self.send_json({"status": "ok", "workspace": str(WORKSPACE)})
        else:
            super().do_GET()
    
    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data)
        except:
            data = {}
        
        if parsed.path == "/api/spawn":
            result = spawn_agent(data.get('task', ''))
            self.send_json(result)
        elif parsed.path == "/api/send":
            result = send_to_session(data.get('session_id'), data.get('message', ''))
            self.send_json(result)
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def read_memory():
    """Read the coder memory file"""
    if MEMORY_FILE.exists():
        try:
            return MEMORY_FILE.read_text(encoding='utf-8')
        except:
            return "# Error reading memory"
    return "# No memory file yet"

def spawn_agent(task):
    """Spawn the Coder agent"""
    full_prompt = """MANDATORY FIRST: Read C:\\Users\\thadd\\.openclaw\\workspace\\agents\\coder-memory.md

Then execute: """ + task + """

AFTER: Update coder-memory.md with what you did, files changed, decisions made, and any open issues. End with "Done" or "Complete".

Remember: You are CODER, not Spock. Coding tasks only."""
    
    try:
        # Get openclaw path
        openclaw_path = "C:/Users/thadd/AppData/Roaming/npm/openclaw.ps1"
        
        # Build the command for PowerShell
        cmd = [
            "powershell.exe",
            "-Command",
            f"& '{openclaw_path}' sessions spawn --task '{full_prompt.replace(\"'\", \"'\"'\")}' --agent-id coder --model kimi-k2.5:cloud --thinking medium --timeout-seconds 600 --mode run --label coder-session-{int(__import__('time').time())}"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=610,
            cwd=str(WORKSPACE)
        )
        
        return {
            "success": result.returncode == 0,
            "response": result.stdout,
            "error": result.stderr if result.stderr else None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def send_to_session(session_id, message):
    """Send message to existing session"""
    # For now, spawn a new session each time (stateless approach)
    return spawn_agent(message)

def main():
    with socketserver.TCPServer(("", PORT), CoderHandler) as httpd:
        print("=" * 60)
        print("Coder Interface Server")
        print("http://localhost:" + str(PORT))
        print("=" * 60)
        print()
        print("Workspace:", WORKSPACE)
        print("Agent:", WORKSPACE / 'agents/coder.md')
        print("Memory:", MEMORY_FILE)
        print()
        print("Press Ctrl+C to stop")
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")

if __name__ == "__main__":
    main()
