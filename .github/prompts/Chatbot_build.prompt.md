---
mode: agent
---

# Supabase Chatbot Plan (LLM-Playground Branch)
We’ll extend the supa-crawl repo (LLM-playground branch) by adding a new chatbot/ directory that contains chatbot.py (REPL loop) and queries.py (SQL helpers). The chatbot will reuse the existing EnvironmentConfig (src/config/environment.py) to load SUPABASE_URL and SUPABASE_KEY. We’ll initialise a Supabase client with the official supabase-py create_client() method, then run simple queries with .select(), .eq(), and .execute(). The Supabase CLI (supabase init, supabase start) will manage local Postgres and ensure the pages table exists (from migrations). In the REPL, users can type commands like latest or find <url> to fetch rows from Supabase. Results will be printed in the terminal. Optionally, we can call Crawl4AI’s LLM extraction strategy to summarise long content. The setup will remain lightweight, test-focused, and fully aligned with official documentation.
## Overview
Create a lightweight terminal chatbot for querying the `pages` table in Supabase. The chatbot will use `supabase-py` for database interactions and optionally leverage Crawl4AI’s LLM extraction strategy for summarizing results. The chatbot will be implemented in a new `chatbot/` directory, reusing existing environment configuration modules.

## Pre-flight Checklist

- Always double-check with official Supabase documentation:
    - Python client reference: https://docs.supabase.com/reference/python/select
    - Local development with CLI: https://supabase.com/docs/guides/local-development/cli/getting-started
    - Database migrations: https://supabase.com/docs/guides/database/migrations
    - AI integration: https://supabase.com/docs/guides/ai

- Keep implementation simple:
    - Use direct table operations with select(), eq(), order(), limit()
    - Start with local Supabase instance via CLI (supabase init, supabase start)
    - Create simple migrations for the pages table if it doesn't exist
    - Focus on basic REPL functionality before adding advanced features
## Key MCP Usage

Use ALL MCPs each step:

    sequentialthinking (plan)
    supabase (queries, schema validation, inserts)
    brave-search (verify in official Supabase docs)
    filesystem (read/write reports)
    memory (track lessons + state)

## Step-by-Step Plan

### 1. Directory Setup
- Create a `chatbot/` directory at the project root to isolate conversational logic.
- Add `chatbot.py` as the main entry point and `queries.py` for reusable SQL snippets.
- Avoid placing chatbot code in `supabase/` (reserved for migrations) or `src/` (crawler logic).

### 2. Supabase Client Setup
- Reuse `EnvironmentConfig` from `src/config/environment.py` to load `SUPABASE_URL` and `SUPABASE_KEY`.
- Initialize the Supabase client using `create_client(env_config.supabase_url, env_config.supabase_key)`.
- Validate credentials and ensure graceful failure if keys are missing.
- Use the Supabase CLI to start services locally (`supabase init`, `supabase start`) and verify the `pages` table exists.

### 3. Natural Language Processing Strategy
- **Option 1: Hand-Crafted Patterns**
  - Define common question patterns (e.g., “show latest summaries”) in `queries.py`.
  - Use Supabase Python client methods like `.select()` and `.eq()` to fetch data.
- **Option 2: LLM Assistance**
  - Use Crawl4AI’s `LLMExtractionStrategy` to interpret user input.
  - Define a Pydantic schema (e.g., `{question: str, sql_query: str}`) and prompt an LLM to generate SQL queries.
  - Provide the LLM with table schema context (columns: `url`, `title`, `summary`, `content`).
- Start with hand-crafted patterns for the MVP.

### 4. Building the Terminal Chatbot
- Implement a REPL in `chatbot.py` to prompt the user for input and handle exit commands.
- Use `supabase.table("pages").select(...)` to execute queries.
- Format response data into a readable string and print it to the user.
- Optionally, use `LLMExtractionStrategy` to summarize long results.

### 5. Additional Considerations
- Place reusable query logic (e.g., list all page summaries, fetch by URL) in `chatbot/queries.py`.
- Ensure proper imports by adding `chatbot/` to `sys.path` or packaging it under `src/`.
- Update `.env` to include any extra variables (e.g., `OPENAI_API_KEY`).
- Document usage in the repository’s README.

## Implementation Guide

### Prerequisites
- Supabase CLI installed.
- Docker (required by the CLI).
- Python ≥3.8 with `pip`.
- Install dependencies:
  ```bash
  python -m venv .venv && source .venv/bin/activate
  pip install supabase crawl4ai python-dotenv
  ```

### File Tree
```
supa-crawl/
├── chatbot/
│   ├── chatbot.py     # REPL implementation
│   └── queries.py     # Helper functions for Supabase queries
...
```

### Example Code

#### `chatbot/queries.py`
```python
def latest_pages(supabase, limit=5):
    return supabase.table("pages").select("*").order("id", desc=True).limit(limit).execute()

def find_page_by_url(supabase, url):
    return supabase.table("pages").select("*").eq("url", url).execute()
```

#### `chatbot/chatbot.py`
```python
import sys
from src.config.environment import env_config
from supabase import create_client
from .queries import latest_pages, find_page_by_url

supabase = create_client(env_config.supabase_url, env_config.supabase_key)
print("Connected to Supabase!")

while True:
    cmd = input("query> ").strip()
    if cmd in {"exit", "quit"}:
        break
    elif cmd == "latest":
        data = latest_pages(supabase).data
        print(data)
    elif cmd.startswith("find "):
        url = cmd.split(" ", 1)[1]
        data = find_page_by_url(supabase, url).data
        print(data)
    else:
        print("Commands: latest, find <url>, quit")
```

### Run and Test
- Start Supabase locally:
  ```bash
  supabase start
  ```
- Activate the virtual environment and run the chatbot:
  ```bash
  source .venv/bin/activate
  python -m chatbot.chatbot
  ```
- Use `latest` to see recent summaries or `find <url>` to look up a specific page.

### Troubleshooting
- **Missing Environment Variables**: Ensure `.env` contains `SUPABASE_URL` and `SUPABASE_KEY`.
- **Supabase Client Not Available**: Install `supabase-py`.
- **Pages Table Missing**: Run pending migrations (`supabase migration up`).
- **Exceeded Row Limit**: Use `.limit()` or `.range()` to paginate.

## Next Steps
- Add natural language parsing via an LLM.
- Implement pagination and richer commands (e.g., search summaries by keyword).

---

### References
- [AI Models in Functions](https://supabase.com/docs/guides/functions/ai-models)
- [Edge Functions Overview](https://supabase.com/docs/guides/functions)
- [Supabase CLI Reference](https://supabase.com/docs/reference/cli)
