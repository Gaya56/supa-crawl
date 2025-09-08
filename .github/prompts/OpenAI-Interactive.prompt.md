---
mode: agent
---
ystem — Make Terminal Chatbot OpenAI‑Interactive (branch: chatbot)

Scope:

Repo: https://github.com/Gaya56/supa-crawl (branch: chatbot)

Use only official docs for references/citations:

OpenAI: Structured Outputs, Python SDK, Quickstart

Supabase: CLI, Python client (select, ilike, order, range, limit)

Crawl4AI (optional summarization)

Pre‑flight Checklist:

Always double‑check with official Supabase documentation:

Python client reference (select/eq/order/limit)

Local development with CLI (supabase init, supabase start)

Database migrations

AI integration guide

Keep implementation simple:

Use direct table operations via .select(), .eq(), .order(), .limit()

Start with a local Supabase instance (supabase init, supabase start)

Create a simple migration for the pages table if it doesn’t exist

Focus on basic REPL functionality before adding advanced features

Key MCP Usage:
Use all MCPs in each step:

sequentialthinking — outline a clear plan before coding.

supabase — run queries, validate schema, and insert test data.

brave-search — verify statements against official Supabase docs.

filesystem — read/write your report or code files as needed.

memory — track lessons learned and maintain context between steps.

Deliverables (step‑by‑step with code + citations):

Prereqs & ENV: Define the task clearly and update .env to include OPENAI_API_KEY along with SUPABASE_URL/SUPABASE_KEY. Install the official OpenAI Python SDK and keep Supabase CLI ready for local DB. Verify Supabase variables load via env_config and create_client().

NL Router (chatbot/nl_router.py): Implement a parse(prompt: str) function. Start with lightweight rules for intents (e.g., “latest X pages,” “find URL,” “search title KEYWORD,” etc.) and return a JSON structure like {"action":"latest","limit":10}. If no rule matches, call OpenAI’s API with a structured‑output request to extract {action, filters, limit} JSON. Validate and return the result.

Wire‑up in chatbot/chatbot.py: Import the router and modify the REPL. For any input not starting with a known command, invoke nl_router.parse() and dispatch to the appropriate query helper (e.g., latest_pages(limit), search_pages_by_title(filters["query"]), get_page_content(filters["id"])). Keep existing commands and graceful error messages.

Extend chatbot/queries.py: Add a generic search_by_keyword(column, query, limit) using .select()/.ilike()/.order()/.limit().execute(). Add a with_summaries(limit) helper using .range() for pagination. Reuse existing helpers (latest_pages, find_page_by_url, get_page_content).

Optional summarization: Introduce an opt‑in flag (e.g., --summarize). When results are lengthy, send the content to Crawl4AI’s LLM extraction strategy to generate concise summaries; display the summary instead of the full content.

Tests & examples: Provide at least six natural‑language prompts with expected intent mappings and example outputs. Include commands to start the local stack (supabase start) and run the chatbot (python -m chatbot.chatbot).

Validation: Ensure imports (env_config, openai, nl_router) resolve. Confirm the pages table schema includes id, url, title, summary, and content columns. Check that environment variables load correctly and errors are logged clearly.**Prereqs & ENV**

   * Add an `OPENAI_API_KEY` line to your `.env` alongside `SUPABASE_URL`/`SUPABASE_KEY`.
   * Install the official OpenAI Python SDK and keep Supabase CLI for local DB:

     ```bash
     pip install openai supabase
     supabase start  # starts the local Postgres/Auth services
     ```
   * Verify Supabase variables load via `env_config` and `create_client()`.  [Supabase CLI][3]

2. **Create `chatbot/nl_router.py`**

   * Define a `parse(prompt: str) -> dict` function that first matches simple patterns (“latest X pages”, “find URL”, “search title KEYWORD”, etc.) and returns a JSON like `{"action": "latest", "limit": 10}`.
   * If no rule matches, send the prompt to OpenAI’s `ChatCompletion` with a `response_format={"type":"json_object"}` and a system prompt describing the expected JSON schema `{action, filters, limit}`.  Validate the returned JSON before dispatch.  [OpenAI Structured Outputs Guide][1]

3. **Wire up free‑form questions in `chatbot/chatbot.py`**

   * Import `nl_router.parse` and modify the REPL loop: for any input not starting with a known command, call `parse(user_input)`.
   * Dispatch based on `action`: call `latest_pages(limit)`, `search_pages_by_title(filters["query"])`, `get_page_content(filters["id"])`, etc.  Keep graceful error messages and fall back to `help` when action is unknown.
   * Continue using `create_client()` and Supabase queries; no changes to environment handling.  [OpenAI Python SDK GitHub][2]

4. **Extend `chatbot/queries.py`**

   * Add a generic `search_by_keyword(column: str, query: str, limit: int)` using `.select("id,url,title,summary")`, `.ilike(column, f"%{query}%")`, `.order("id", desc=True)`, `.limit(limit)` and `.execute()`.
   * Add `with_summaries(limit)` that filters where `title` and `summary` are non‑null and supports `.range(offset, offset+limit-1)` for pagination.  Use `.range()` as described in Supabase Python select docs.
   * Reuse existing helpers for `latest_pages`, `find_page_by_url`, `get_page_content`.  [Supabase Python select docs][5]

5. **Optional summarization**

   * Introduce an opt‑in flag (e.g., `--summarize`) in the REPL. If the result’s `content` or combined summaries exceed a threshold, pass the text to Crawl4AI’s `LLMExtractionStrategy` configured with a schema (`{summary: str}`) and instruction to “summarize this page”.  Only call the LLM when explicitly requested.  [Crawl4AI LLM strategies docs][4]

6. **Tests & examples**

   * Start the local stack (`supabase start`) and run the chatbot: `python -m chatbot.chatbot`.
   * Example prompts and expected routing:

     1. “show me the latest 10 pages” → `{"action":"latest","limit":10}` → `latest_pages(10)`.
     2. “find [https://example.com/post”](https://example.com/post”) → `{"action":"find_url","url":"https://example.com/post"}` → `find_page_by_url`.
     3. “search title AI ethics” → `{"action":"search_title","query":"AI ethics"}`.
     4. “search summary machine learning” → `{"action":"search_summary","query":"machine learning"}`.
     5. “how many pages are there?” → `{"action":"count"}`.
     6. “content 42” → `{"action":"content_by_id","id":42}` → `get_page_content`.  [Supabase CLI Docs][3]

7. **Validation**

   * Ensure imports resolve (`env_config`, `openai`, `nl_router`), and that your `.env` has `OPENAI_API_KEY`.
   * Confirm the `pages` table includes `id`, `url`, `title`, `summary`, and `content` columns (see migration).
   * After adding logging (already implemented), check that errors are logged with `logger.error(..., exc_info=True)`.  [Supabase Python introduction][6]

[1]: https://platform.openai.com/docs/guides/structured-outputs?utm_source=chatgpt.com
[2]: https://github.com/openai/openai-python?utm_source=chatgpt.com
[3]: https://supabase.com/docs/guides/local-development/cli/getting-started?utm_source=chatgpt.com
[4]: https://docs.crawl4ai.com/extraction/llm-strategies/?utm_source=chatgpt.com
[5]: https://supabase.com/docs/reference/python/select?utm_source=chatgpt.com
[6]: https://supabase.com/docs/reference/python/introduction?utm_source=chatgpt.com
