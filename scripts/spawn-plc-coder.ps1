#Requires -Version 5.1
<#
.SYNOPSIS
    Quick spawn the PLCTools Coder agent with persistent memory.
.DESCRIPTION
    Spawns a subagent that reads PROJECT_MEMORY.md first, so it knows what you were working on.
#>

Write-Host "🔧 Spawning PLCTools Coder..." -ForegroundColor Cyan
openclaw sessions spawn --label plctool-coder --mode run --runtime subagent --task "Spawn PLCTools coding assistant"