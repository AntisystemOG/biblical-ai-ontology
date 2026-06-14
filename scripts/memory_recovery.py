"""Recover daily memory from session transcripts (April 8-25, 2026) - v3"""
import json, os, glob
from datetime import datetime, timedelta
from collections import defaultdict

SESSION_DIR = r"C:\Users\thada\.openclaw\agents\main\sessions"
MEMORY_DIR = r"C:\Users\thada\.openclaw\workspace\memory"

# Group session files by their modification date
day_sessions = defaultdict(list)
for f in glob.glob(os.path.join(SESSION_DIR, "*.jsonl")):
    basename = os.path.basename(f)
    if 'trajectory' in basename or 'checkpoint' in basename or 'deleted' in basename:
        continue
    mtime = datetime.fromtimestamp(os.path.getmtime(f))
    day_sessions[mtime.date()].append(f)

def extract_content(filepath):
    """Extract meaningful content from a session JSONL file"""
    messages = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except:
                    continue
                
                if entry.get('type') != 'message':
                    continue
                
                msg = entry.get('message', {})
                role = msg.get('role', '')
                content = msg.get('content', '')
                
                # Handle list content (OpenAI/Anthropic format)
                if isinstance(content, list):
                    texts = []
                    for part in content:
                        if isinstance(part, dict):
                            ptype = part.get('type', '')
                            if ptype == 'text':
                                texts.append(part.get('text', ''))
                            elif ptype == 'thinking':
                                pass  # skip thinking
                            elif ptype == 'toolCall':
                                texts.append(f"[Called: {part.get('name', '?')}]")
                            elif ptype == 'toolResult':
                                # Get first 150 chars of result
                                rc = part.get('content', '')
                                if isinstance(rc, list):
                                    rc = ' '.join([p.get('text','') for p in rc if isinstance(p, dict)])
                                texts.append(f"[Result: {str(rc)[:150]}]")
                        elif isinstance(part, str):
                            texts.append(part)
                    content = '\n'.join(texts)
                
                if not isinstance(content, str):
                    continue
                
                content = content.strip()
                if not content or content in ('HEARTBEAT_OK', 'NO_REPLY'):
                    continue
                if len(content) < 10:
                    continue
                
                messages.append({'role': role, 'content': content[:600]})
    except Exception as e:
        pass
    return messages

def build_daily_note(date, all_messages):
    """Build a daily note from extracted messages"""
    if not all_messages:
        return None
    
    lines = [f"# {date} Daily Notes\n"]
    
    user_msgs = [m for m in all_messages if m['role'] == 'user']
    asst_msgs = [m for m in all_messages if m['role'] == 'assistant']
    
    # Extract key topics from user messages
    for msg in user_msgs[:10]:
        text = msg['content'].strip()
        if 'heartbeat' in text.lower() and len(text) < 100:
            continue
        if 'cron:' in text.lower() and len(text) < 100:
            continue
        if len(text) > 5:
            # Truncate very long messages
            lines.append(f"## User\n{text[:400]}\n")
    
    # Extract key actions from assistant messages
    actions = []
    for msg in asst_msgs:
        text = msg['content']
        # Look for meaningful content
        if any(kw in text.lower() for kw in ['created', 'updated', 'fixed', 'added', 'deleted', 'installed', 'error', 'cron', 'report', 'dashboard', 'trading', 'whale', 'history', 'brief', 'financial', 'bible', 'memory', 'push', 'commit', 'pull']):
            # Get first 200 chars
            snippet = text[:200].replace('\n', ' ').strip()
            if snippet not in [a[:50] for a in actions]:
                actions.append(snippet)
    
    if actions:
        lines.append("## Activity\n")
        for a in actions[:10]:
            lines.append(f"- {a}\n")
    
    content = '\n'.join(lines)
    return content if len(content) > 80 else None

# Process each day
start = datetime(2026, 4, 9).date()
end = datetime(2026, 4, 26).date()

for date in sorted(day_sessions.keys()):
    if date < start or date >= end:
        continue
    
    day_str = date.strftime('%Y-%m-%d')
    mem_path = os.path.join(MEMORY_DIR, f"{day_str}.md")
    
    # Skip if already has real content
    if os.path.exists(mem_path):
        with open(mem_path, 'r') as f:
            existing = f.read()
        if 'Quiet day' not in existing and len(existing) > 100:
            print(f"  {day_str}: exists with content, skipping")
            continue
        os.remove(mem_path)
    
    # Collect all messages from this day's sessions
    all_messages = []
    for fpath in day_sessions[date]:
        msgs = extract_content(fpath)
        all_messages.extend(msgs)
    
    note = build_daily_note(date, all_messages)
    
    if note:
        with open(mem_path, 'w', encoding='utf-8') as f:
            f.write(note)
        print(f"  {day_str}: wrote note ({len(all_messages)} msgs from {len(day_sessions[date])} sessions)")
    else:
        with open(mem_path, 'w', encoding='utf-8') as f:
            f.write(f"# {day_str} Daily Notes\n\nQuiet day — no significant sessions recorded.\n")
        print(f"  {day_str}: quiet day")

print("\nDone!")