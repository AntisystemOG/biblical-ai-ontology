"""Generate a PDF summarizing best practices for coding agent configuration."""
from fpdf import FPDF
from pathlib import Path

REPORTS = Path.home() / "OneDrive" / "Desktop" / "Spocks Reports"

class Doc(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.set_auto_page_break(True, 20)
        self.add_font("Segoe", "", r"C:\Windows\Fonts\segoeui.ttf")
        self.add_font("Segoe", "B", r"C:\Windows\Fonts\segoeuib.ttf")
        self.add_font("Segoe", "I", r"C:\Windows\Fonts\segoeuii.ttf")
        self.section_y = 0

    def header(self):
        if self.page_no() > 1:
            self.set_font("Segoe", "I", 7)
            self.set_text_color(128, 128, 128)
            self.cell(0, 4, "Coding Agent Best Practices — May 2026", align="R")
            self.ln(6)

    def title_page(self):
        self.add_page()
        self.ln(40)
        self.set_font("Segoe", "B", 26)
        self.set_text_color(44, 62, 80)
        self.multi_cell(0, 10, "Coding Agent\nBest Practices", align="C")
        self.ln(8)
        self.set_font("Segoe", "", 13)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "OpenClaw Sub-agent Configuration Guide", align="C")
        self.ln(14)
        self.set_draw_color(52, 152, 219)
        self.set_line_width(1.5)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(14)
        self.set_font("Segoe", "", 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 7, "May 6, 2026", align="C")
        self.ln(7)
        self.cell(0, 7, "Source: OpenClaw docs + community best practices", align="C")

    def h1(self, text):
        self.set_font("Segoe", "B", 16)
        self.set_text_color(44, 62, 80)
        self.ln(4)
        self.cell(0, 8, text)
        self.ln(8)
        self.set_draw_color(52, 152, 219)
        self.set_line_width(0.6)
        self.line(15, self.get_y(), 80, self.get_y())
        self.ln(4)

    def h2(self, text):
        self.set_font("Segoe", "B", 12)
        self.set_text_color(52, 73, 94)
        self.ln(3)
        self.cell(0, 7, text)
        self.ln(9)

    def body(self, text):
        self.set_font("Segoe", "", 9.5)
        self.set_text_color(40, 40, 40)
        self.set_x(15)
        self.multi_cell(180, 5.5, text)
        self.ln(1)

    def bullet(self, text):
        self.set_font("Segoe", "", 9.5)
        self.set_text_color(40, 40, 40)
        self.set_x(18)
        self.cell(4, 5.5, chr(8226))
        self.multi_cell(173, 5.5, text)

    def table(self, headers, rows):
        ncols = len(headers)
        widths = [180 / ncols] * ncols
        # Header
        self.set_x(15)
        for c, h in enumerate(headers):
            self.set_font("Segoe", "B", 8)
            self.set_fill_color(52, 152, 219)
            self.set_text_color(255, 255, 255)
            self.cell(widths[c], 6, h, fill=True)
        self.ln()
        # Rows
        for i, row in enumerate(rows):
            self.set_x(15)
            fill = i % 2 == 0
            for c, cell in enumerate(row):
                self.set_font("Segoe", "", 8)
                self.set_text_color(30, 30, 30)
                if fill: self.set_fill_color(248, 249, 250)
                else: self.set_fill_color(255, 255, 255)
                self.cell(widths[c], 5.5, str(cell), fill=True)
            self.ln()
        self.ln(3)

    def code_block(self, text):
        self.set_font("Segoe", "", 8)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(60, 60, 60)
        self.set_x(18)
        for line in text.strip().split('\n'):
            self.set_x(18)
            self.cell(174, 4, line, fill=True)
            self.ln()
        self.ln(3)


pdf = Doc()
pdf.title_page()

# 1. Architecture
pdf.add_page()
pdf.h1("1. Agent Architecture")
pdf.body("A coding agent in OpenClaw is a sub-agent — a background worker spawned from the main agent. Key architectural facts:")
pdf.bullet("Sub-agents run in their own isolated session: agent:<id>:subagent:<uuid>")
pdf.bullet("They get ONLY AGENTS.md + TOOLS.md injected (no SOUL, IDENTITY, USER, HEARTBEAT) — stays focused on task")
pdf.bullet("Default context mode is \"isolated\" (clean transcript each spawn) — recommended for coding")
pdf.bullet("Use \"fork\" only when the child needs the requester's conversation context")
pdf.bullet("Completion is push-based — don't poll, just wait for the announce event")
pdf.bullet("Each sub-agent is tracked as a background task")

pdf.h2("Nesting")
pdf.bullet("Max spawn depth default: 1 (sub-agents can't spawn their own)")
pdf.bullet("Set maxSpawnDepth: 2 for orchestrator pattern (main -> orchestrator -> workers)")
pdf.bullet("Depth-2 workers are leaf nodes — cannot spawn further")

# 2. Model & Thinking
pdf.h1("2. Model & Thinking Settings")
pdf.body("These settings determine the intelligence and cost of your coding agent:")

pdf.table(
    ["Setting", "Recommendation", "Why"],
    [
        ["Model", "kimi-k2.5:cloud (primary)\nqwen3-coder:cloud (fallback)", "Kimi strong at coding logic;\nQwen-Coder tuned for code generation"],
        ["thinkingDefault", "medium or high", "Medium for routine tasks;\nhigh for complex architecture/debugging"],
        ["reasoningDefault", "off", "Reasoning adds latency; only enable for deep analysis"],
        ["Sub-agent model", "Same or cheaper", "Use cheaper model for repetitive sub-tasks;\nkeep good model for main orchestrator"],
        ["Fast mode", "false (default)", "Coding needs careful thought, not speed"],
    ]
)

pdf.h2("Model budget note")
pdf.body("Each sub-agent has its own context and token usage. For heavy/repetitive tasks, set a cheaper model via agents.defaults.subagents.model. Keep your main agent on a higher-quality model.")

# 3. Memory
pdf.h1("3. Persistent Memory Design")
pdf.body("Sub-agents don't retain memory between sessions natively. The standard pattern:")

pdf.h2("The Memory File Pattern (our approach)")
pdf.bullet("Create a dedicated markdown file: agents/coder-memory.md")
pdf.bullet("Sub-agent reads it FIRST every session (mandatory)")
pdf.bullet("Sub-agent updates it LAST every session (mandatory)")
pdf.bullet("Include: active projects, architecture decisions, known issues, TODO items")
pdf.bullet("Keep it structured with clear sections for fast scanning")
pdf.bullet("This is analogous to PROJECT_MEMORY.md in PLCTools Coder")

pdf.h2("What to store")
pdf.bullet("Project context and current state")
pdf.bullet("Decisions made and their rationale")
pdf.bullet("Known bugs or technical debt")
pdf.bullet("Pending work items (TODO)")
pdf.bullet("Completed work log (reverse chronological)")

pdf.h2("Why markdown files work better than 'mental notes'")
pdf.bullet("Survives session restarts")
pdf.bullet("Human-readable and human-editable")
pdf.bullet("Git-tracked — full version history")
pdf.bullet("Can be shared across agent instances")
pdf.bullet("Tokens are cheaper than context window for long-running knowledge")

# 4. Tools
pdf.h1("4. Tool Configuration")
pdf.body("Sub-agents use the same tool policy pipeline as the parent, then get the sub-agent restriction layer applied:")

pdf.table(
    ["Tool Category", "Status", "Notes"],
    [
        ["File tools (read, write, edit)", "ALLOWED", "Core coding tools"],
        ["Shell (exec, process)", "ALLOWED", "Build, test, run"],
        ["Web (search, fetch)", "ALLOWED", "Research, docs lookup"],
        ["Session tools (spawn, list, history)", "DENIED by default", "Depth-1 orchestrators get these when maxSpawnDepth >= 2"],
        ["System tools (gateway, cron)", "DENIED", "Not needed for coding"],
        ["Browser", "OPTIONAL", "Add via tools.alsoAllow if needed for web testing"],
    ]
)

pdf.h2("Tool profiles")
pdf.bullet("\"coding\" profile includes: read, write, edit, exec, process, web_search, web_fetch, sessions_spawn")
pdf.bullet("\"full\" profile adds: browser, canvas, cron, gateway, etc.")
pdf.bullet("Per-agent override: agents.list[].tools.alsoAllow to add specific tools")

# 5. Timeouts
pdf.h1("5. Timeout & Reliability")
pdf.table(
    ["Parameter", "Recommended", "Why"],
    [
        ["runTimeoutSeconds", "600-900 (10-15 min)", "Coding tasks often take 5-10 minutes;\ncomplex ones need headroom"],
        ["Agent timeout", "600s", "Default agent turn timeout"],
        ["Sub-agent archive", "60 min (default)", "Auto-archives old sub-agent sessions"],
        ["Heartbeat timeout", "45s (default)", "Keep short for prompt housekeeping"],
    ]
)

pdf.h2("Why timeouts matter")
pdf.body("Without a timeout, a stuck sub-agent can hang indefinitely. Our earlier issues with trading-arena timing out at 300s confirmed: coding/analysis agents need AT LEAST 600s. For the coder agent, 900s is safer for tasks that involve building, testing, and iterating.")

# 6. Cron Management
pdf.h1("6. Cron Auto-Spawn Pattern")
pdf.body("Keep coding agents warm with staggered auto-spawn:");
pdf.code_block("""Cron: coder-auto-spawn
Schedule: "0 1,5,9,13,17,21 * * *" (every 4h, offset from PLC)
Payload: agentTurn with task to read memory and wait
Timeout: 600s
Delivery: --no-deliver (no Telegram spam)""")
pdf.body("Stagger from plc-coder-auto-spawn (0,4,8,12,16,20) by 1 hour to avoid resource contention.")

# 7. What We Have
pdf.h1("7. Current Setup vs Best Practices")
pdf.table(
    ["Area", "Current", "Best Practice", "Status"],
    [
        ["Model", "kimi-k2.5:cloud", "kimi-k2.5 or qwen3-coder", "GOOD"],
        ["Memory", "coder-memory.md", "Markdown file, read first/update last", "GOOD"],
        ["Identity", "Separate IDENTITY file", "Don't reference being Spock", "GOOD"],
        ["Timeout", "600s via cron", "600-900s", "GOOD"],
        ["Context", "Isolated", "Isolated for fresh tasks", "GOOD"],
        ["Thinking", "Not set explicitly", "medium for coding", "ADD"],
        ["Fallback model", "Not set", "qwen3-coder:cloud", "ADD"],
    ]
)

pdf.h2("Recommended additions")
pdf.bullet("Add thinkingDefault: \"medium\" to coder config")
pdf.bullet("Add fallback model: ollama/qwen3-coder:cloud")
pdf.bullet("Consider tools.allow to restrict to coding-specific tools only")

# 8. Quick Reference
pdf.h1("8. Quick Reference Card")
pdf.h2("Spawning a coding sub-agent")
pdf.code_block("""sessions_spawn(
  label: "my-task",
  task: "Read coder-memory.md first, then [task description]",
  runTimeoutSeconds: 900
)""")

pdf.h2("Key agent config file")
pdf.code_block("""Location: agents/coder.md
Memory: agents/coder-memory.md
Registry: agents/REGISTRY.md""")

pdf.h2("Key docs")
pdf.bullet("Local: node_modules/openclaw/docs/tools/subagents.md")
pdf.bullet("Local: node_modules/openclaw/docs/gateway/config-agents.md")
pdf.bullet("Web: https://docs.openclaw.ai/subagents")
pdf.bullet("Web: https://docs.openclaw.ai/gateway/config-agents")

out = REPORTS / "agent_config" / "2026-05-06_coding_agent_best_practices.pdf"
out.parent.mkdir(parents=True, exist_ok=True)
pdf.output(str(out))
print(f"PDF saved: {out.name} ({out.stat().st_size:,} bytes)")
