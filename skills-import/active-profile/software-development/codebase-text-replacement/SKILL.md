---
name: codebase-text-replacement
description: Safely perform bulk string replacement (rebrand, rename, deprecation sweep) across an entire project tree.
trigger: User asks to rename a term, rebrand a project, or replace a string across many files.
---

# Codebase Text Replacement

Replace a string (or family of strings) across an entire project while avoiding common pitfalls: binary corruption, build-artifact mutation, partial-word false positives, and hyphenated config-key breakage.

## When to use this skill

- Rebranding (e.g., product name change across UI strings, docs, manifests).
- API deprecation sweeps (rename a function/variable across source).
- Trademark or compliance-driven text updates.
- Any request of the form “make every file that says X say Y instead.”

## Why not sed/awk

`sed -i` and `awk` are fine for 1–3 files. For 50+ files they become dangerous:
- No automatic binary-safety.
- Hard to skip `.git/`, `__pycache__/`, `node_modules/`, compiled artifacts.
- Case-variant handling requires multiple passes.
- No easy verification / diff reporting afterward.

## Procedure

### 1. Discover the blast radius

```python
import os, re
BASE = '/path/to/project'
TERM = 'OldName'
matches = []
for root, dirs, files in os.walk(BASE):
    if any(skip in root for skip in ['.git', '__pycache__', 'node_modules', '.venv', 'dist', 'build']):
        continue
    for f in files:
        if f.endswith(BINARY_EXTS):
            continue
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
        except Exception:
            continue
        if TERM in content:
            matches.append(path)
```

Report the count to the user and ask for confirmation before mutating.

### 2. Choose the replacement strategy

| Variant present? | Regex pattern | Notes |
|---|---|---|
| Only one case | `r'\bOldName\b'` | Simple word-boundary guard |
| Mixed case (`OldName`, `oldName`, `OLDNAME`) | `r'\b(OldName|oldName|OLDNAME)\b'` with a replacer dict | Preserves casing semantics |
| Compound config keys (`old-name`, `old_name`) | **Do NOT** use bare `\b`; explicitly enumerate or post-review | See pitfall §3 |

### 3. Two-pass execution (mandatory for UI/server rebrandings)

**Pass 1 — Word-boundary safe replacement**
Use regex with `\b` for standalone tokens to avoid partial-word false positives.

**Pass 2 — Compound-token sweep**
`\b` deliberately misses merged forms (`openOldNameDialog`, `__OLDNAME__`, `old-name`, `_oldname_`). After Pass 1 returns "zero survivors," run an unconditional `str.replace()` pass for these common compounds:

```python
compounds = [
    ('__OLDNAME__', '__NEWNAME__'),
    ('__OLDNAME_CONFIG__', '__NEWNAME_CONFIG__'),
    ('openOldNameDialog', 'openNewNameDialog'),
    ('openOldNameDashboard', 'openNewNameDashboard'),
    ('old-name', 'new-name'),
    ('OLDNAME-', 'NEWNAME-'),
    ('_oldname_', '_newname_'),
    ('_OLDNAME_', '_NEWNAME_'),
]

# Run inside the same file walk, AFTER the regex pass
for old, new in compounds:
    new_content = new_content.replace(old, new)
```

Then verify again — the compound pass often catches the *majority* of UI-visible leaks.

### 4. Execute with a Python walk (not shell loops)

```python
import os, re

REPLACEMENTS = {
    'OldName': 'NewName',
    'oldName': 'newName',
    'OLDNAME': 'NEWNAME',
}

def replacer(m):
    return REPLACEMENTS.get(m.group(0), m.group(0))

pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in REPLACEMENTS) + r')\b')

total = 0
for root, dirs, files in os.walk(BASE):
    # Exclude directories
    dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'dist', 'build'}]
    for f in files:
        if any(f.endswith(ext) for ext in BINARY_EXTS):
            continue
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
        except Exception:
            continue
        new_content, count = pattern.subn(replacer, content)
        if count:
            total += count
            with open(path, 'w', encoding='utf-8') as fhw:
                fhw.write(new_content)
```

### 4. Verify

Run a second search for the **old** string to confirm zero survivors:

```python
# Same walk, report any files still containing old term
```

Also run `git diff --stat` (or equivalent) to sanity-check the magnitude.

## Pitfalls

1. **Word boundaries break compound tokens**
   - `\b` treats `-` and `_` as non-word characters, so `old-name` and `old_name` **will** match.
   - If the term is used in directory names, Docker volume names, CSS classes, or config keys, these will be mutated too.
   - **Fix:** After the bulk pass, search for surviving compound forms (`old-name`, `old_name`) and decide case-by-case whether to replace.

2. **CamelCase / PascalCase boundaries**
   - `\bOldName\b` **does not** match inside `openOldNameDialog` because there is no word boundary between `e` and `D`.
   - This is usually correct (you don't want to rename internal API signatures by accident), but verify with the user whether code identifiers are in scope.

3. **Compiled artifacts and lockfiles**
   - `package-lock.json`, `poetry.lock`, `Pipfile.lock`, `.pyc`, `.min.js` may contain the string in hashed URLs or checksums.
   - Always skip common binary/artifact extensions.

4. **Server-side template injection**
   - If the server injects the term into HTML via template strings (e.g., `__HERMES_CONFIG__` or `{{ hermes_title }}`), the Python/JS source may be clean but the *runtime rendered output* still shows the old name.
   - **Fix:** Search backend templates for injected strings, not just static files.

5. **Browser cache desync**
   - After replacing text in `index.html`, JS, CSS, and `manifest.json`, the browser may still show the old branding from `localStorage` defaults, Service Worker caches, or in-memory JS variables.
   - **Fix:** Add a post-replacement checklist: (a) hard-refresh browser (`Ctrl+Shift+R`), (b) unregister Service Worker, (c) clear `localStorage` for any cached default strings, (d) verify rendered DOM, not just source files.

6. **Internationalization (i18n) key breakage**
   - If the old term appears in translation keys (e.g., `data-i18n="oldname_greeting"`), renaming the visible text but leaving the key intact can desync the UI.
   - Either update the key too, or confirm the key mapping is regenerated elsewhere.

5. **Server/client contract mismatch**
   - HTTP headers (`X-OldName-CSRF-Token`), API path segments, or WebSocket message types may get renamed in the frontend but not the backend (or vice versa).
   - After replacement, grep for the new term in both frontend and backend to ensure both sides changed.

## Support files

- `references/compound-token-survivors.md` — post-replacement checklist of hyphenated/underscored forms to manually review.