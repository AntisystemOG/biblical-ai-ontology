---
name: webui-voice-input
author: Hermes Agent
version: 1.0.0
description: Add browser-native voice input (Web Speech API) to the Hermes WebUI chat component, and fix associated build/reload issues.
tags: [hermes-web-ui, voice, speech, web-speech-api, vite, vue, scss, build]
---

# WebUI Voice Input Skill

## Context
The Hermes WebUI is a Vue 3 + TypeScript + Vite application.
- Client source: `packages/client/src/`
- Chat input component: `packages/client/src/components/hermes/chat/ChatInput.vue`
- SCSS variables: `packages/client/src/styles/variables.scss`
- Built client assets: `dist/client/`
- Server serves static files from `dist/client/` (see `packages/server/src/index.ts`)

## 1. Adding Voice Input to ChatInput.vue

### Script — add inside `script setup`

```typescript
const isListening = ref(false)
const isVoiceSupported = ref(false)
let voiceRecognition: any = null

function initVoiceRecognition() {
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  if (!SpeechRecognition) return

  isVoiceSupported.value = true
  voiceRecognition = new SpeechRecognition()
  voiceRecognition.continuous = true
  voiceRecognition.interimResults = true
  voiceRecognition.lang = 'en-US'

  voiceRecognition.onresult = (event: any) => {
    let finalTranscript = ''
    let interimTranscript = ''
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript
      } else {
        interimTranscript += event.results[i][0].transcript
      }
    }
    if (finalTranscript) {
      inputText.value += (inputText.value ? ' ' : '') + finalTranscript
    }
    if (interimTranscript) {
      inputText.value += (inputText.value ? ' ' : '') + interimTranscript
    }
    nextTick(() => {
      const el = textareaRef.value
      if (el && textareaHeight.value === null) {
        el.style.height = 'auto'
        el.style.height = Math.min(el.scrollHeight, 100) + 'px'
      }
    })
  }

  voiceRecognition.onerror = (event: any) => {
    console.error('Voice recognition error:', event.error)
    isListening.value = false
  }

  voiceRecognition.onend = () => {
    isListening.value = false
  }
}

function toggleVoiceInput() {
  if (!isVoiceSupported.value) return
  if (isListening.value) {
    voiceRecognition?.stop()
    isListening.value = false
  } else {
    voiceRecognition?.start()
    isListening.value = true
  }
}
```

Merge `initVoiceRecognition()` into the existing `onMounted` block rather than creating a second one.

### Template — insert after attach button

Place the microphone button between the attach-button NTooltip and the `auto-play-speech-switch` div.

```vue
<NTooltip trigger="hover">
  <template #trigger>
    <NButton
      quaternary
      size="tiny"
      @click="toggleVoiceInput"
      circle
      :class="{ 'voice-btn-listening': isListening }"
      :disabled="!isVoiceSupported"
    >
      <template #icon>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          <line x1="12" y1="19" x2="12" y2="23"/>
          <line x1="8" y1="23" x2="16" y2="23"/>
        </svg>
      </template>
    </NButton>
  </template>
  {{ isListening ? 'Stop listening' : 'Start voice input' }}
</NTooltip>
```

### Style — add to the `style scoped lang="scss"` block

```scss
.voice-btn-listening {
  color: #e85d4a !important;
  animation: pulse-mic 1.5s infinite ease-in-out;
}

@keyframes pulse-mic {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

## 2. Build & Deploy

### Run from the correct directory
**Critical:** Must run from the project root where `vite.config.ts` lives.
```bash
cd C:\Users\thadd\hermes-web-ui
# or in WSL:
cd /mnt/c/Users/thadd/hermes-web-ui
```

### Build commands
```bash
# Full build (type-check + client + server)
npm run build

# Client bundle only (if full build times out)
npx vite build --outDir dist/client

# Step-by-step if building full:
npx vue-tsc -b
npx vite build --outDir dist/client
npx tsc --noEmit -p packages/server/tsconfig.json
node scripts/build-server.mjs
```

**Pitfall:** Running `npx vite build` from `C:\Users\thadd` causes `[UNRESOLVED_ENTRY] Cannot resolve entry module index.html` because Vite defaults to the current directory and there is no `index.html` there. Always change directory first.

### Restart server
The server serves static assets from `dist/client/` but may cache aggressively. After building:
```bash
pkill -f "node dist/server/index.js"
nohup node dist/server/index.js > ~/.hermes-web-ui/server.log 2>&1 &
```
Or use the Windows launcher: `Desktop\Launch Hermes WebUI.bat`

## 3. Browser Requirements
- **Chrome / Edge only** — uses `webkitSpeechRecognition`.
- **HTTPS or localhost** — Chrome blocks SpeechRecognition on plain HTTP (non-localhost).
- **Microphone permission** — browser asks on first use. User must allow.

## 4. Troubleshooting Checklist

| Symptom | Cause | Fix |
|---|---|---|
| No mic button | SpeechRecognition not supported | Use Chrome/Edge; check DevTools console |
| Mic button grayed out | `isVoiceSupported` false | Verify HTTPS or localhost; check browser |
| Click mic → no text | Mic permission denied or onerror | Allow mic in browser settings |
| Words run together | Missing space on append | Ensure `(inputText.value ? ' ' : '')` prefix |
| `[UNRESOLVED_ENTRY] Cannot resolve entry module index.html` | Ran build from wrong directory | `cd C:\Users\thadd\hermes-web-ui` first |
| Build never finishes | Stale `vite` process | `pkill -f "vite build"` then rebuild |
| UI unchanged on refresh | Stale `dist/client` | Rebuild + Ctrl+Shift+R or restart server |

## 5. SCSS Variable Fix Pitfall (Session Lesson)

When adding new components or modifying existing ones, you may hit:

```
[sass] Undefined variable.
    background: $bg-hover;
                ^^^^^^^^^
```

**Root cause:** The SCSS variable is used in a component file but not declared in the shared `variables.scss`.

**Fix pattern:**
1. Find the file via the build error: `packages/client/src/styles/variables.scss`
2. Add the CSS custom property in `:root` (light) and `.dark` (dark):
```scss
:root {
  --bg-hover: #f0f0f0;
  --primary-light: #f0f0f0;
}
.dark {
  --bg-hover: #3a3a3a;
  --primary-light: #4a4a4a;
}
```
3. Add the SCSS variable alias:
```scss
$bg-hover: var(--bg-hover, #f0f0f0);
$primary: var(--accent-primary);
$primary-light: var(--primary-light, #f0f0f0);
```

**Important:** Do not overwrite the existing accent section. Add new variables **above** the existing block, not in place of it.

## 6. Common Pitfalls
- Do **not** create duplicate `onMounted()` hooks. Merge `initVoiceRecognition()` into the existing one.
- Do **not** forget the space-prefix before appending transcript: `(inputText.value ? ' ' : '') + transcript`
- Do **not** assume `interimResults` are final. Append both; the user will see live text.
- Do **not** use `continuous = false` for dictation mode. It times out too quickly.
- Do **not** hardcode auth tokens in the `.bat` launcher. Use the existing token file pattern.

## 7. Environment Notes
- **Username:** Paths must use `C:\Users\thadd` (two-d). Single-d `thad` is a typo and will fail. Audit any new scripts or shortcuts.
- **WebUI source path:** `/mnt/c/Users/thadd/hermes-web-ui` (WSL) or `C:\Users\thadd\hermes-web-ui` (Windows)
- **Spock branding icon:** `C:\Users\thadd\Desktop\Icons\spock-emblem.jpg`
- **Desktop launcher:** `C:\Users\thadd\Desktop\Hermes\Launch Hermes WebUI.bat`
