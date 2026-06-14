# OpenClaw Control UI - Remove Sidebar

## Quick Fix (Recommended)

Use a browser extension to inject the CSS override:

### Stylus Extension (Chrome/Firefox/Edge)
1. Install **Stylus** from:
   - Chrome: https://chrome.google.com/webstore/detail/stylus/clngdbkpkpeebahjckkjfobafhncgmne
   - Firefox: https://addons.mozilla.org/en-US/firefox/addon/styl-us/
   - Edge: https://microsoftedge.microsoft.com/addons/detail/stylus/klbibkeccnjlkjkiokjodocebajanakg

2. Open your OpenClaw Control UI page

3. Click the Stylus extension icon → **"Write style for: [your-domain]"**

4. Paste this CSS:

```css
/* Hide the main sidebar navigation */
aside.sidebar,
.sidebar,
.sidebar-shell,
.sidebar-panel,
.sidebar-header,
.sidebar-content,
.sidebar-title,
.chat-sidebar,
.sidebar--collapsed,
.sidebar-shell__header,
.sidebar-shell__body,
.sidebar-version__status,
.sidebar-connection-status--online,
.sidebar-connection-status--offline {
  display: none !important;
  width: 0 !important;
  min-width: 0 !important;
  max-width: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
}

/* Expand main content to full width */
main,
.main,
.main-content,
.chat-thread,
.chat-container,
.config-layout,
.usage-overview-layout {
  width: 100% !important;
  max-width: 100% !important;
  margin-left: 0 !important;
  margin-right: 0 !important;
  padding-left: 1rem !important;
  padding-right: 1rem !important;
}

/* Remove any left margin/padding from body/app container */
openclaw-app,
body,
html,
.app,
.app-container {
  margin-left: 0 !important;
  padding-left: 0 !important;
}

/* Hide sidebar toggle buttons */
button[aria-label*="sidebar"],
button[title*="sidebar"],
.sidebar-toggle,
.toggle-sidebar {
  display: none !important;
}
```

5. Name it "OpenClaw No Sidebar" and click **Save**

Done! The sidebar is now hidden and the page uses full width.

---

## Alternative: Tampermonkey Script

If you prefer userscripts:

1. Install **Tampermonkey** extension
2. Create new script with:

```javascript
// ==UserScript==
// @name         OpenClaw No Sidebar
// @match        *://*/*openclaw*/*
// @grant        GM_addStyle
// ==/UserScript==

GM_addStyle(`
  aside.sidebar, .sidebar, .sidebar-shell, .sidebar-panel,
  .sidebar-header, .sidebar-content, .sidebar-title,
  .chat-sidebar, .sidebar--collapsed { display: none !important; }
  main, .main, .main-content { width: 100% !important; margin: 0 !important; }
`);
```

---

## File Location

The CSS override is saved at:
`C:\Users\thada\OneDrive\Desktop\Spocks Reports\workspace\control-ui-no-sidebar.css`
