---
name: conversation-protocols
description: User interaction patterns, communication rules, and behavioral protocols for conversational sessions.
version: 1.0.0
category: productivity
---

# Conversation Protocols

## Purpose
Capture how the user expects conversational interactions to work — message ordering, interruptions, behavioral rules, and how to interpret requests for conversational features like "queues."

## Triggers
- User establishes communication rules (FIFO, ordering, interruption policies)
- User asks for a "queue," "buffer," or "don't interrupt" behavior
- User corrects your conversational style or timing
- User says "remember this" about how you should respond

## Core Rules

### Task Continuity — Do Not Interrupt
When in the middle of a task (terminal running, code executing, tool calls in progress, etc.), **continue to completion** before acknowledging any new messages. Do NOT stop mid-task to answer. The user can say **"Stop"** to abort immediately.

### FIFO Message Processing
Messages are handled in order (first in, first out), one at a time. No skipping around to answer the newest message unless it contains the word **"Stop."**

### Don't Over-Engineer Simple Rules
When the user asks for a behavioral change like "queue messages" or "don't interrupt," they usually mean a **simple operational rule**, not a complex file-based queue system, cron job, or persistent message buffer. Default to policy over infrastructure.

## Pitfalls

### Building File-Based Queue Systems for Simple FIFO Requests
The user asking to "queue" messages typically wants them processed in order — not persisted to `~/queue/messages.json`, not flushed via scripts, not tracked in state files. A behavioral rule suffices.

See `references/queue-lesson.md` for the specific session where this was corrected.

### Interrupting Running Tasks to Answer New Messages
Killing a terminal command, abandoning a file write, or halting a search to reply breaks task state and wastes the user's time. Finish, then acknowledge.

### Assuming "Queue" Means Persistence
In conversational context, "queue" nearly always means **process-ordering policy** (FIFO), not a durable message buffer. Ask for clarification if the request truly needs persistence.

## Corrective Keywords
- **"Stop"** — Immediate halt, regardless of pending tasks or queued messages.
- **"Just make a rule"** — Indicates the user wants a simple behavioral change, not scaffolding or infrastructure.

## References
- `references/queue-lesson.md` — Session detail: user corrected over-engineering into a simple FIFO rule.
