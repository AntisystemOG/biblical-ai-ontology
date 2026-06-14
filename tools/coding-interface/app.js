/**
 * Coder Interface App - Full Integration with OpenClaw
 */

// State
let sessionId = null;
let isAgentSpawned = false;
let currentTask = null;

const API_BASE = 'http://localhost:18790/api';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('welcome-time').textContent = formatTime(new Date());
    document.getElementById('user-input').focus();
    checkServerStatus();
});

// Format time
function formatTime(date) {
    return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
    });
}

// Check server status
async function checkServerStatus() {
    try {
        const response = await fetch(`${API_BASE}/check`);
        const data = await response.json();
        
        if (data.status === 'ok') {
            updateAgentStatus('online', 'Server Ready');
        }
    } catch (error) {
        updateAgentStatus('offline', 'Server Offline - Run start-coder.bat');
        addMessage('assistant', 'System', 'Server not running. Start it with: start-coder.bat');
    }
}

// Input handling
const textarea = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

textarea.addEventListener('input', function() {
    sendBtn.disabled = textarea.value.trim().length === 0;
});

textarea.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send message
async function sendMessage() {
    const text = textarea.value.trim();
    if (!text) return;

    // Add user message
    addMessage('user', 'You', text);
    textarea.value = '';
    sendBtn.disabled = true;
    textarea.style.height = 'auto';

    // Show typing indicator
    showTypingIndicator();

    try {
        let response;
        
        if (!isAgentSpawned) {
            // First message - spawn agent
            response = await spawnAgent(text);
        } else {
            // Continue existing session
            response = await sendToSession(sessionId, text);
        }
        
        hideTypingIndicator();
        
        if (response.success) {
            addMessage('assistant', 'Coder', formatAgentResponse(response.response));
        } else {
            addMessage('assistant', 'Coder', 'Error: ' + (response.error || 'Unknown error') + '\n\nTry restarting the server.');
        }
    } catch (error) {
        hideTypingIndicator();
        addMessage('assistant', 'Coder', 'Connection Error: ' + error.message + '\n\nMake sure the server is running: start-coder.bat');
    }
}

// Spawn agent via API
async function spawnAgent(task) {
    updateAgentStatus('connecting', 'Spawning agent...');
    updatePlanStep(0, 'active');
    
    const response = await fetch(`${API_BASE}/spawn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: task })
    });
    
    const data = await response.json();
    
    if (data.success) {
        isAgentSpawned = true;
        sessionId = 'coder-session-' + Date.now();
        
        updatePlanStep(0, 'completed');
        updatePlanStep(1, 'completed');
        updatePlanStep(2, 'completed');
        
        const isDone = data.response && (data.response.includes('Done') || data.response.includes('Complete'));
        if (isDone) {
            updatePlanStep(3, 'completed');
        }
        
        updateAgentStatus('online', 'Agent Active');
        updateAgentInfo();
    } else {
        updateAgentStatus('offline', 'Spawn Failed');
    }
    
    return data;
}

// Send to existing session
async function sendToSession(sessionId, message) {
    updateAgentStatus('connecting', 'Processing...');
    
    const response = await fetch(`${API_BASE}/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: message })
    });
    
    const data = await response.json();
    
    if (data.success) {
        updateAgentStatus('online', 'Agent Active');
    } else {
        updateAgentStatus('offline', 'Error');
    }
    
    return data;
}

// Format agent response
function formatAgentResponse(text) {
    if (!text) return "No response received";
    
    // Escape HTML first
    let formatted = escapeHtml(text);
    
    // Highlight file paths
    const filePathRegex = /([A-Z]:\\[\w\\.\-]+|agents\/[\w\-]+\.md|[\w\-]+\.py|[\w\-]+\.js)/g;
    formatted = formatted.replace(filePathRegex, function(match) {
        if (match.endsWith('.md') || match.endsWith('.py') || match.endsWith('.js') || match.indexOf('\\') > -1) {
            return '<span class="file-mention">' + match + '</span>';
        }
        return match;
    });
    
    // Format markdown
    formatted = formatted
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/\n/g, '<br>');
    
    return formatted;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add message to chat
function addMessage(role, author, content) {
    const messages = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar ' + role;
    avatar.textContent = role === 'user' ? 'T' : 'C';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const header = document.createElement('div');
    header.className = 'message-header';
    header.innerHTML = '<span class="message-author">' + escapeHtml(author) + '</span><span class="message-time">' + formatTime(new Date()) + '</span>';

    const body = document.createElement('div');
    body.className = 'message-body';
    body.innerHTML = content;

    contentDiv.appendChild(header);
    contentDiv.appendChild(body);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    const indicator = document.getElementById('thinking-indicator');
    if (indicator) {
        indicator.classList.add('active');
        const video = document.getElementById('thinking-spinner');
        if (video) {
            video.currentTime = 0;
            video.play().catch(() => {});
        }
    }
}

// Hide typing indicator
function hideTypingIndicator() {
    const indicator = document.getElementById('thinking-indicator');
    if (indicator) {
        indicator.classList.remove('active');
        const video = document.getElementById('thinking-spinner');
        if (video) video.pause();
    }
}

// Update agent status
function updateAgentStatus(status, text) {
    const indicator = document.getElementById('agent-indicator');
    const statusText = document.getElementById('agent-status-text');
    
    indicator.className = 'status-indicator ' + status;
    statusText.textContent = text;
    
    if (status === 'online') {
        document.getElementById('agent-status-body').innerHTML = '<strong>Status:</strong> Running<br><strong>Session:</strong> ' + (sessionId || 'Active') + '<br><strong>Model:</strong> kimi-k2.5:cloud<br><strong>Memory:</strong> Loaded';
    }
}

function updateAgentInfo() {
    document.getElementById('agent-status-body').innerHTML = '<strong>Status:</strong> Running<br><strong>Session:</strong> ' + (sessionId || 'Active') + '<br><strong>Model:</strong> kimi-k2.5:cloud<br><strong>Memory:</strong> Loaded from coder-memory.md';
}

// Update plan step
function updatePlanStep(index, state) {
    const steps = document.querySelectorAll('.plan-step');
    if (steps[index]) {
        steps[index].className = 'plan-step ' + state;
    }
}

// Clear plan
function clearPlan() {
    const steps = document.querySelectorAll('.plan-step');
    steps.forEach(function(step) {
        step.className = 'plan-step';
    });
    if (steps[0]) steps[0].className = 'plan-step active';
}

// New session
function newSession() {
    sessionId = null;
    isAgentSpawned = false;
    currentTask = null;
    
    document.getElementById('messages').innerHTML = '<div class="message"><div class="message-avatar assistant">C</div><div class="message-content"><div class="message-header"><span class="message-author">Coder</span><span class="message-time">' + formatTime(new Date()) + '</span></div><div class="message-body"><p>New session started. Ready when you are.</p><p style="color: var(--text-muted);">Type your first message to spawn the agent with persistent memory.</p></div></div></div>';
    
    clearPlan();
    updateAgentStatus('online', 'Agent Ready');
    document.getElementById('agent-status-body').textContent = 'Ready to spawn sub-agent on first message...';
}

// Restart agent
function restartAgent() {
    isAgentSpawned = false;
    sessionId = null;
    addMessage('assistant', 'Coder', 'Agent state reset. Next message will spawn a fresh agent instance.');
    clearPlan();
    updateAgentStatus('online', 'Agent Ready');
}

// Show memory
async function showMemory() {
    try {
        const response = await fetch(`${API_BASE}/memory`);
        const data = await response.json();
        
        addMessage('assistant', 'Coder', '<strong>Current Memory:</strong><pre><code>' + escapeHtml(data.content) + '</code></pre>');
    } catch (error) {
        // Fallback - inform user
        addMessage('assistant', 'Coder', 'Memory file: agents/coder-memory.md');
    }
}

// Edit agent config
function editAgent() {
    addMessage('assistant', 'Coder', 'Agent config: agents/coder.md<br>Memory file: agents/coder-memory.md');
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        document.getElementById('user-input').value = '';
        document.getElementById('user-input').focus();
    }
    if (e.ctrlKey && e.key === '/') {
        e.preventDefault();
        addMessage('assistant', 'Coder', '<strong>Keyboard Shortcuts:</strong><br>Enter - Send message<br>Shift+Enter - New line<br>Ctrl+K - Clear input<br>Ctrl+/ - This help<br>Ctrl+N - New session');
    }
    if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        newSession();
    }
});
