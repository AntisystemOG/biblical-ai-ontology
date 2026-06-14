# Lesson: "Queue" Does Not Mean a File-Based Queue System

## Signal
User asked: "Please automatically add messages from telegram to a queue, don't interrupt."

## What I Did Wrong
Built a complex file-based queue system:
- `~/.hermes/queue/state.json` (tracking queue mode)
- `~/.hermes/queue/messages.json` (persisted message store)
- `~/.hermes/queue/flush.sh` (processing script)
- Replied "[Queued — waiting for /flush]" after every message, which itself broke the "don't interrupt" intent

## What the User Actually Wanted
A simple behavioral rule: process messages in order, don't interrupt running tasks. When asked for clarification, user said: *"Just make a rule to process my messages in order unless I say 'Stop.'"*

## Key Learning
When the user asks for a "queue" or "don't interrupt" behavioral change:
1. Default to **simple policy** (FIFO, finish running tasks first)
2. Ask clarifying questions if you truly don't understand
3. **Do not** build file-based systems, cron jobs, state tracking, or scripts for a conversational behavior change
4. "Just make a rule" is the user's signal that you're over-engineering

## Correct Implementation
Add a Communication Rules section to SOUL.md (or equivalent):
- Task Continuity — Do Not Interrupt
- FIFO Message Processing
- Stop keyword for immediate abort
