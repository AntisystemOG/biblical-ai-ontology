---
name: web-search
description: Web search for OpenClaw via DuckDuckGo (local Python script, no API key) or Brave Search (native plugin, requires API key). Use for research, fact-checking, recent information, news, images, videos. Covers both provider setup and day-to-day querying.
---

# Web Search

## Overview

OpenClaw supports two search backends:

1. **DuckDuckGo** — zero-config, runs through a local Python script (`scripts/search.py`). Good for quick lookups.
2. **Brave Search** — native plugin, requires a `BRAVE_API_KEY`, integrates directly with the `web_search` tool. Better result quality, LLM-context endpoint, rate-limit tracking.

Pick the provider that matches the user's environment. If they already have an OpenClaw `openclaw.json`, prefer Brave when an API key is available.

## When to Use This Skill

- User asks to "search the web" or "look up X"
- User wants to configure, rotate, or update a Brave Search API key
- User wants to change the default search provider in OpenClaw
- Research, fact-checking, finding recent information, images, videos

## When to Use This Skill

Use this skill when users request:
- Web searches for information or resources
- Finding current or recent information online
- Looking up news articles about specific topics
- Searching for images by description or topic
- Finding videos on specific subjects
- Research requiring current web data
- Fact-checking or verification using web sources
- Gathering URLs and resources on a topic

## Prerequisites

### DuckDuckGo route

```bash
pip install ddgs
```

On Hermes (WSL or Linux), if system `pip` is unavailable, install into Hermes' own venv instead:
```bash
/home/thadd/.hermes/hermes-agent/venv/bin/pip install ddgs
```

### Brave Search route

Requires:
1. A Brave Search API key from https://brave.com/search/api/ (Search plan; $5/mo credit covers ~1,000 queries)
2. The `@openclaw/brave-plugin` installed (bundled with recent OpenClaw versions)

## Provider: Brave Search (Native Plugin)

### Config Path

### Provider: Brave Search (Hermes)

Hermes has native Brave Search support via the `web` toolset. No separate plugin is required.

#### Config path

Edit `~/.hermes/config.yaml`. Under the `web:` section, set `search_backend` to `brave` and add your `brave_api_key`:

```yaml
web:
  backend: firecrawl
  search_backend: brave          # NOT 'brave-free' — free tier burns out fast
  brave_api_key: BSA-XXXXXXXXXXXXXXXXXXXXXXXXX
  extract_backend: ''
```

After editing, restart the Gateway:
```bash
hermes gateway restart
```

**Hermes internal venv location:**
If you ever need to install Python packages that a search script depends on (e.g., `duckduckgo-search`), target Hermes' own venv:
```bash
/home/thadd/.hermes/hermes-agent/venv/bin/pip install <package>
# or activate it:
source /home/thadd/.hermes/hermes-agent/venv/bin/activate && pip install <package>
```

### Provider: Brave Search (OpenClaw)

Store the key inside `openclaw.json` under `plugins.entries.brave.config.webSearch.apiKey`.  **Do not** rely on the legacy `tools.web.search.apiKey` shim; it is deprecated.

**Minimal working snippet:**

```json5
{
  plugins: {
    entries: {
      brave: {
        config: {
          webSearch: {
            apiKey: "BSA-XXXXXXXXXXXXXXXXXXXXXXXXX",
            mode: "web",           // or "llm-context"
            baseUrl: "https://api.search.brave.com"
          }
        }
      }
    }
  },
  tools: {
    web: {
      search: {
        provider: "brave",
        maxResults: 5,
        timeoutSeconds: 30
      }
    }
  }
}
```

### Rotating / Updating an API Key

**Hermes:**
1. Back up `~/.hermes/config.yaml`
2. Patch the `brave_api_key` line under `web:`
3. Save and `hermes gateway restart`

**OpenClaw:**
1. **Back up** the current config before editing:
   ```bash
   cp openclaw.json openclaw.json.bak.pre-brave-api
   ```
2. Patch `plugins.entries.brave.config.webSearch.apiKey` to the new value.
3. Ensure `tools.web.search.provider` is `"brave"`.
4. Save and restart the Gateway (`openclaw gateway restart`).

### Pitfalls

- **`search_backend: brave-free` is worthless**: Hermes defaults to `brave-free` with a $0.01 monthly cap. It burns out on the first real query and returns HTTP 402 `USAGE_LIMIT_EXCEEDED`. Always switch to `search_backend: brave` with a paid API key from https://brave.com/search/api/ — $5/month covers ~1,000 queries.
- **OpenClaw vs Hermes config paths differ**: Hermes uses flat YAML under `web:` (`brave_api_key`, `search_backend`); OpenClaw uses nested JSON under `plugins.entries.brave.config.webSearch.apiKey`. Do not copy OpenClaw snippets into a Hermes `config.yaml`.
- **Wrong Python environment**: DuckDuckGo scripts need `ddgs` installed in Hermes' venv, not system Python. Hermes' venv lives at `/home/thadd/.hermes/hermes-agent/venv/`. Use the full path:
  ```bash
  /home/thadd/.hermes/hermes-agent/venv/bin/pip install ddgs
  ```
  System `pip` is often missing in WSL — the venv path is the reliable way.
- **Rate limit exhaustion (HTTP 402 / `USAGE_LIMIT_EXCEEDED`)**: Brave returns this when the monthly quota burns out. The JSON response includes `current_spend`, `usage_limit`, and `usage_limit_type`. If you hit this, switch to paid tier or wait for the next billing cycle (~30 days). There is no workaround.
- **Package renamed `duckduckgo_search` → `ddgs` (v9+)**: The import changed from `from duckduckgo_search import DDGS` to `from ddgs import DDGS`. The parameter name also changed from `keywords=query` to `query=query` across `.text()`, `.images()`, `.news()`, `.videos()`. Legacy scripts using `keywords=` will fail with `TypeError: ... missing 1 required positional argument: 'query'`. Fix: update the import and parameter name. See `references/ddgs-migration.md`.
- **Getting Brave results when DuckDuckGo fails**: If `ddgs` image search hits a 403 or rate limit, fall back to the Brave Search API directly:
  ```bash
  curl -s "https://api.search.brave.com/res/v1/images/search?q=QUERY&count=N" \
    -H "X-Subscription-Token: $BRAVE_API_KEY" -H "Accept: application/json"
  ```
- Forgetting to flip `tools.web.search.provider` leaves searches silently routed to the old provider.
- `llm-context` mode (grounded chunks) does **not** support `ui_lang`; `date_before` alone is rejected—pass both `date_after` and `date_before`.
- Cache TTL is 15 minutes by default. Custom `baseUrl` values are included in cache identity.
- Brave returns 429 when rate limits are hit. Set a usage limit in the Brave dashboard.

See `references/brave-openclaw-config.md` for full JSON template, legacy-vs-current path table, cost/limit notes, and key-rotation checklist.

## Provider: DuckDuckGo (Local Script)

## DuckDuckGo Package Migration (2025+)

The Python package `duckduckgo_search` has been renamed to `ddgs`. The old import (`from duckduckgo_search import DDGS`) now raises a deprecation warning and may break on newer versions.

**Current import:**
```python
from ddgs import DDGS
```

**Install command:**
```bash
# On Hermes (WSL): install into Hermes' venv, NOT system pip
/home/thadd/.hermes/hermes-agent/venv/bin/pip install ddgs
# or activate first:
source /home/thadd/.hermes/hermes-agent/venv/bin/activate && pip install ddgs
```

**Breaking changes from `duckduckgo_search` to `ddgs` (v9+):**
- Import changed: `from duckduckgo_search import DDGS` → `from ddgs import DDGS`
- Parameter name changed across ALL methods: `keywords=query` → `query=query`
  - Affects: `.text()`, `.images()`, `.news()`, `.videos()`
  - Calling with `keywords=` raises: `TypeError: DDGS.text() ... missing 1 required positional argument: 'query'`
- **Recommended**: Uninstall the old package first to avoid conflicts:
  ```bash
  pip uninstall -y duckduckgo-search && pip install ddgs
  ```

## Core Capabilities

### 1. Basic Web Search

Search for web pages and information:

```bash
python scripts/search.py "<query>"
```

**Example:**
```bash
python scripts/search.py "python asyncio tutorial"
```

Returns the top 10 web results with titles, URLs, and descriptions in a clean text format.

### 2. Limiting Results

Control the number of results returned:

```bash
python scripts/search.py "<query>" --max-results <N>
```

**Example:**
```bash
python scripts/search.py "machine learning frameworks" --max-results 20
```

Useful for:
- Getting more comprehensive results (increase limit)
- Quick lookups with fewer results (decrease limit)
- Balancing detail vs. processing time

### 3. Time Range Filtering

Filter results by recency:

```bash
python scripts/search.py "<query>" --time-range <d|w|m|y>
```

**Time range options:**
- `d` - Past day
- `w` - Past week
- `m` - Past month
- `y` - Past year

**Example:**
```bash
python scripts/search.py "artificial intelligence news" --time-range w
```

Great for:
- Finding recent news or updates
- Filtering out outdated content
- Tracking recent developments

### 4. News Search

Search specifically for news articles:

```bash
python scripts/search.py "<query>" --type news
```

**Example:**
```bash
python scripts/search.py "climate change" --type news --time-range w --max-results 15
```

News results include:
- Article title
- Source publication
- Publication date
- URL
- Article summary/description

### 5. Image Search

Search for images:

```bash
python scripts/search.py "<query>" --type images
```

**Example:**
```bash
python scripts/search.py "sunset over mountains" --type images --max-results 20
```

**Image filtering options:**

Size filters:
```bash
python scripts/search.py "landscape photos" --type images --image-size Large
```
Options: `Small`, `Medium`, `Large`, `Wallpaper`

Color filters:
```bash
python scripts/search.py "abstract art" --type images --image-color Blue
```
Options: `color`, `Monochrome`, `Red`, `Orange`, `Yellow`, `Green`, `Blue`, `Purple`, `Pink`, `Brown`, `Black`, `Gray`, `Teal`, `White`

Type filters:
```bash
python scripts/search.py "icons" --type images --image-type transparent
```
Options: `photo`, `clipart`, `gif`, `transparent`, `line`

Layout filters:
```bash
python scripts/search.py "wallpapers" --type images --image-layout Wide
```
Options: `Square`, `Tall`, `Wide`

Image results include:
- Image title
- Image URL (direct link to image)
- Thumbnail URL
- Source website
- Dimensions (width x height)

### 6. Video Search

Search for videos:

```bash
python scripts/search.py "<query>" --type videos
```

**Example:**
```bash
python scripts/search.py "python tutorial" --type videos --max-results 15
```

**Video filtering options:**

Duration filters:
```bash
python scripts/search.py "cooking recipes" --type videos --video-duration short
```
Options: `short`, `medium`, `long`

Resolution filters:
```bash
python scripts/search.py "documentary" --type videos --video-resolution high
```
Options: `high`, `standard`

Video results include:
- Video title
- Publisher/channel
- Duration
- Publication date
- Video URL
- Description

### 7. Region-Specific Search

Search with region-specific results:

```bash
python scripts/search.py "<query>" --region <region-code>
```

**Common region codes:**
- `us-en` - United States (English)
- `uk-en` - United Kingdom (English)
- `ca-en` - Canada (English)
- `au-en` - Australia (English)
- `de-de` - Germany (German)
- `fr-fr` - France (French)
- `wt-wt` - Worldwide (default)

**Example:**
```bash
python scripts/search.py "local news" --region us-en --type news
```

### 8. Safe Search Control

Control safe search filtering:

```bash
python scripts/search.py "<query>" --safe-search <on|moderate|off>
```

**Options:**
- `on` - Strict filtering
- `moderate` - Balanced filtering (default)
- `off` - No filtering

**Example:**
```bash
python scripts/search.py "medical information" --safe-search on
```

### 9. Output Formats

Choose how results are formatted:

**Text format (default):**
```bash
python scripts/search.py "quantum computing"
```

Clean, readable plain text with numbered results.

**Markdown format:**
```bash
python scripts/search.py "quantum computing" --format markdown
```

Formatted markdown with headers, bold text, and links.

**JSON format:**
```bash
python scripts/search.py "quantum computing" --format json
```

Structured JSON data for programmatic processing.

### 10. Saving Results to File

Save search results to a file:

```bash
python scripts/search.py "<query>" --output <file-path>
```

**Example:**
```bash
python scripts/search.py "artificial intelligence" --output ai_results.txt
python scripts/search.py "AI news" --type news --format markdown --output ai_news.md
python scripts/search.py "AI research" --format json --output ai_data.json
```

The file format is determined by the `--format` flag, not the file extension.

## Output Format Examples

### Text Format
```
1. Page Title Here
   URL: https://example.com/page
   Brief description of the page content...

2. Another Result
   URL: https://example.com/another
   Another description...
```

### Markdown Format
```markdown
## 1. Page Title Here

**URL:** https://example.com/page

Brief description of the page content...

## 2. Another Result

**URL:** https://example.com/another

Another description...
```

### JSON Format
```json
[
  {
    "title": "Page Title Here",
    "href": "https://example.com/page",
    "body": "Brief description of the page content..."
  },
  {
    "title": "Another Result",
    "href": "https://example.com/another",
    "body": "Another description..."
  }
]
```

## Common Usage Patterns

### Research on a Topic

Gather comprehensive information about a subject:

```bash
# Get overview from web
python scripts/search.py "machine learning basics" --max-results 15 --output ml_web.txt

# Get recent news
python scripts/search.py "machine learning" --type news --time-range m --output ml_news.txt

# Find tutorial videos
python scripts/search.py "machine learning tutorial" --type videos --max-results 10 --output ml_videos.txt
```

### Current Events Monitoring

Track news on specific topics:

```bash
python scripts/search.py "climate summit" --type news --time-range d --format markdown --output daily_climate_news.md
```

### Finding Visual Resources

Search for images with specific criteria:

```bash
python scripts/search.py "data visualization examples" --type images --image-type photo --image-size Large --max-results 25 --output viz_images.txt
```

### Fact-Checking

Verify information with recent sources:

```bash
python scripts/search.py "specific claim to verify" --time-range w --max-results 20
```

### Academic Research

Find resources on scholarly topics:

```bash
python scripts/search.py "quantum entanglement research" --time-range y --max-results 30 --output quantum_research.txt
```

### Market Research

Gather information about products or companies:

```bash
python scripts/search.py "electric vehicle market 2025" --max-results 20 --format markdown --output ev_market.md
python scripts/search.py "EV news" --type news --time-range m --output ev_news.txt
```

## Implementation Approach

When users request web searches:

1. **Identify search intent**:
   - What type of content (web, news, images, videos)?
   - How recent should results be?
   - How many results are needed?
   - Any filtering requirements?

2. **Configure search parameters**:
   - Choose appropriate search type (`--type`)
   - Set time range if currency matters (`--time-range`)
   - Adjust result count (`--max-results`)
   - Apply filters (image size, video duration, etc.)

3. **Select output format**:
   - Text for quick reading
   - Markdown for documentation
   - JSON for further processing

4. **Execute search**:
   - Run the search command
   - Save to file if results need to be preserved
   - Print to stdout for immediate review

5. **Process results**:
   - Read saved files if needed
   - Extract URLs or specific information
   - Combine results from multiple searches

## Quick Reference

**Command structure:**
```bash
python scripts/search.py "<query>" [options]
```

**Essential options:**
- `-t, --type` - Search type (web, news, images, videos)
- `-n, --max-results` - Maximum results (default: 10)
- `--time-range` - Time filter (d, w, m, y)
- `-r, --region` - Region code (e.g., us-en, uk-en)
- `--safe-search` - Safe search level (on, moderate, off)
- `-f, --format` - Output format (text, markdown, json)
- `-o, --output` - Save to file

**Image-specific options:**
- `--image-size` - Size filter (Small, Medium, Large, Wallpaper)
- `--image-color` - Color filter
- `--image-type` - Type filter (photo, clipart, gif, transparent, line)
- `--image-layout` - Layout filter (Square, Tall, Wide)

**Video-specific options:**
- `--video-duration` - Duration filter (short, medium, long)
- `--video-resolution` - Resolution filter (high, standard)

**Get full help:**
```bash
python scripts/search.py --help
```

## Best Practices

1. **Be specific** - Use clear, specific search queries for better results
2. **Use time filters** - Apply `--time-range` for current information
3. **Adjust result count** - Start with 10-20 results, increase if needed
4. **Save important searches** - Use `--output` to preserve results
5. **Choose appropriate type** - Use news search for current events, web for general info
6. **Use JSON for automation** - JSON format is easiest to parse programmatically
7. **Respect usage** - Don't hammer the API with rapid repeated searches

## Troubleshooting

**Common issues:**

- **Package migration error (`duckduckgo_search` → `ddgs`)**: Update the import and parameter names:
  - `from duckduckgo_search import DDGS` → `from ddgs import DDGS`
- `keywords=query` → `query=query` (parameter name changed in v9+; causes `TypeError: ... missing 1 required positional argument: 'query'`)
  Install: `pip uninstall -y duckduckgo-search && pip install ddgs`
  (If you are on OpenClaw rather than Hermes, use `sudo apt-get install python3-pip` on Debian/Ubuntu, or equivalent.)
- **Rate limit error (HTTP 402 / `USAGE_LIMIT_EXCEEDED`)**: Your Brave API key has exhausted its monthly quota. If on the free tier, upgrade at https://brave.com/search/api/. Otherwise wait for the next billing cycle.
- **No results found**: Try broader search terms or remove time filters
- **Timeout errors**: The search service may be temporarily unavailable; retry after a moment
- **Rate limiting**: Space out searches if making many requests
- **Unexpected results**: DuckDuckGo's results may differ from Google; try refining the query

**Limitations:**

- Results quality depends on DuckDuckGo's index and algorithms
- No advanced search operators (unlike Google's site:, filetype:, etc.)
- Image and video searches may have fewer results than web search
- No control over result ranking or relevance scoring
- Some specialized searches may work better on dedicated search engines

## Advanced Use Cases

### Combining Multiple Searches

Gather comprehensive information by combining search types:

```bash
# Web overview
python scripts/search.py "topic" --max-results 15 --output topic_web.txt

# Recent news
python scripts/search.py "topic" --type news --time-range w --output topic_news.txt

# Images
python scripts/search.py "topic" --type images --max-results 20 --output topic_images.txt
```

### Programmatic Processing

Use JSON output for automated processing:

```bash
python scripts/search.py "research topic" --format json --output results.json
# Then process with another script
python analyze_results.py results.json
```

### Building a Knowledge Base

Create searchable documentation from web results:

```bash
# Search multiple related topics
python scripts/search.py "topic1" --format markdown --output kb/topic1.md
python scripts/search.py "topic2" --format markdown --output kb/topic2.md
python scripts/search.py "topic3" --format markdown --output kb/topic3.md
```

## Resources

### scripts/search.py

The main search tool implementing DuckDuckGo search functionality. Key features:

- **Multiple search types** - Web, news, images, and videos
- **Flexible filtering** - Time range, region, safe search, and type-specific filters
- **Multiple output formats** - Text, Markdown, and JSON
- **File output** - Save results for later processing
- **Clean formatting** - Human-readable output with all essential information
- **Error handling** - Graceful handling of network errors and empty results

The script can be executed directly and includes comprehensive command-line help via `--help`.
