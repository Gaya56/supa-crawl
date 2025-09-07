---
mode: agent
---
Define the task to achieve, including specific requirements, constraints, and success criteria.**Agent Prompt – Supabase Chatbot Plan (LLM‑playground branch)**

To add a lightweight terminal chatbot to the `supa‑crawl` repository, re‑use existing configuration modules and follow patterns from the official Supabase and Crawl4AI documentation. Below is a suggested plan:
Build a Terminal Chatbot for Supabase (LLM-playground branch)

Analyze only:


* Create a new `chatbot/` directory at the project root. Keeping it separate from `src/` isolates conversational logic from crawling and storage code while still allowing imports.
* Inside `chatbot/`, add `chatbot.py` as the main entry point and possibly a `queries.py` module for SQL snippets. Avoid placing chatbot code in `supabase/` (reserved for database migrations) or `src/` (contains crawler logic).
* Reuse `EnvironmentConfig` from `src/config/environment.py` to load `SUPABASE_URL`, `SUPABASE_KEY` and validate credentials.

### 2. Supabase client set‑up

* Follow the official Supabase‑py initialisation pattern used in `SupabaseHandler`: call `create_client(env_config.supabase_url, env_config.supabase_key)`.
* Read and validate credentials via `env_config` just as the crawler does, ensuring the chatbot fails gracefully if keys are missing.
* For local development, use the Supabase CLI to start the services (`supabase init`, then `supabase start`) and verify that the `pages` table exists via migrations in `supabase/migrations`.

### 3. Natural‑language processing strategy

* To translate natural language questions into SQL queries, you have two options:

  1. **Hand‑crafted patterns:** define common question patterns (e.g. “show latest summaries”) in `queries.py` and map them to Supabase queries. Use the Supabase Python client’s `.select()` and `.eq()` methods to fetch data.
  2. **LLM assistance:** leverage Crawl4AI’s LLM extraction to interpret arbitrary user input. Official LLM strategy documentation explains that `LLMExtractionStrategy` can be used to extract structured JSON from unstructured text. You could define a Pydantic schema like `{question: str, sql_query: str}` and prompt an LLM (via Crawl4AI or OpenAI API) to generate SQL. This would require providing the LLM with table schema context (columns `url`, `title`, `summary`, `content`).
* For a minimal viable product, start with hand‑crafted patterns and only add LLM interpretation if flexibility is needed.

### 4. Building the terminal chatbot

* Implement a loop in `chatbot.py` that prompts the user for input and handles exit commands.
* On each question, call `supabase.table("pages").select(...)` or other Supabase‑py methods to execute queries. The `.execute()` call returns a response with `.data` similar to the storage handler’s insertion logic.
* Format the response data into a readable string and print it back to the user.
* Optionally, call `LLMExtractionStrategy` via Crawl4AI to summarise long results before displaying them—Crawl4AI docs note that summarisation is ideal for unstructured content.

### 5. Additional considerations

* Place reusable query logic (e.g. list all page summaries, fetch by URL) in `chatbot/queries.py`.
* Ensure new modules are imported correctly by adding `chatbot/` to `sys.path` in `chatbot.py` or by packaging it under `src/` if preferred.
* Update `.env` to include any extra variables needed for LLM access (e.g. `OPENAI_API_KEY`) and rely on existing validation methods.
* Document usage in the repository’s README, explaining how to run the chatbot and that Supabase services must be running via CLI commands.

This plan keeps the chatbot separate yet integrated with existing environment handling and Supabase connectivity, aligns with official documentation, and remains lightweight for terminal use.
