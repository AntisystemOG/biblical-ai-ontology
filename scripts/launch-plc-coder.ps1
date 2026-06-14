#Requires -Version 5.1
<#
.SYNOPSIS
    Desktop shortcut launcher for PLCTools Coder agent.
    Spawns the agent and opens the chat window.
#>

Write-Host "🔧 Spawning PLCTools Coder..." -ForegroundColor Cyan

# Change to workspace directory
Set-Location "C:\Users\thadd\.openclaw\workspace"

# Spawn the agent
openclaw sessions spawn --label plctool-coder --mode run --runtime subagent --task "Spawn PLCTools coding assistant"

Write-Host "Opening Control UI..." -ForegroundColor Green
Start-Process "http://127.0.0.1:18789/"

Write-Host "Done!" -ForegroundColor Green
Start-Sleep -Seconds 2