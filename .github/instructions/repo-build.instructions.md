---
applyTo: '*/workspaces/codespaces-blank*'
---

# Supa-Crawl (LLM-Playground) Instructions

## Overview
Supa-Crawl is a Python web-crawling pipeline that integrates the Crawl4AI framework with Supabase storage. It supports memory-adaptive and semaphore dispatchers for multi-URL crawling and includes an LLM extraction strategy to produce JSON summaries. Results (URL, raw markdown, analysis) are stored in a Supabase `pages` table. The `main.py` script orchestrates tests for each dispatcher and the LLM pipeline. Environment variables specify the Supabase URL/key and OpenAI API key.

### Key Features
- **Crawl4AI Integration**: Adaptive crawling with rate limiting.
- **LLM Extraction**: JSON summaries for unstructured/semantic data.
- **Supabase Storage**: Results stored in a `pages` table.

### Sources Referenced
- **Crawl4AI Docs**: LLM extraction strategy, dispatcher behavior.
- **Supabase Docs**: CLI commands for local development.
- **Repository Code**: Key files include `src/config/environment.py`, `src/crawlers/async_crawler.py`, `src/storage/supabase_handler.py`, `src/models/schemas.py`, and `main.py`.

## Directory Structure
```
supa-crawl/
├─ src/
│  ├─ config/
│  │  └─ environment.py  # Loads env vars, creates browser/crawler config
│  ├─ crawlers/
│  │  └─ async_crawler.py  # Defines AdvancedWebCrawler and crawl methods
│  ├─ models/
│  │  └─ schemas.py  # Pydantic model for LLM extraction
│  └─ storage/
│     └─ supabase_handler.py  # Handles Supabase client and insertion/upsert
├─ main.py  # Demo entry point testing each pipeline stage
├─ supabase/
│  ├─ config.toml
│  └─ migrations/
│     ├─ 20250905230727_create_pages_table.sql
│     ├─ 20250906194420_remote_schema.sql
│     └─ 20250906195530_remote_schema.sql
├─ tests/
│  ├─ crawl4ai/test_basic_crawling.py
│  ├─ integration/test_crawl4ai_supabase.py
│  ├─ supabase/test_database_operations.py
│  └─ README.md
├─ docs/
├─ supabase-cli-commands.md
├─ requirements.txt
└─ ...
```

## File Breakdown

### `src/config/environment.py`
- **Role**: Centralized environment and crawler configuration.
- **Key Functions**:
  - `EnvironmentConfig`: Reads `SUPABASE_URL`, `SUPABASE_KEY`, `OPENAI_API_KEY`.
  - `CrawlerConfig.create_browser_config`: Builds a `BrowserConfig` with stealth settings.
  - `create_crawler_run_config`: Returns a `CrawlerRunConfig` with default extraction strategy.

### `src/models/schemas.py`
- **Role**: Pydantic schemas for LLM extraction.
- **Key Classes**:
  - `PageSummary`: Defines title and summary fields.
  - `CrawlResult`, `Crawl4AIResponse`: Wrap results.

### `src/crawlers/async_crawler.py`
- **Role**: Implements `AdvancedWebCrawler`.
- **Key Functions**:
  - `crawl_with_memory_adaptive_dispatcher`: Configures a `MemoryAdaptiveDispatcher`.
  - `crawl_with_semaphore_dispatcher`: Uses `SemaphoreDispatcher` for concurrency.
  - `crawl_with_llm_analysis`: Builds an `LLMExtractionStrategy` and parses JSON results.
  - `crawl_and_store_in_supabase`: Calls the LLM crawl and stores summaries in Supabase.

### `src/storage/supabase_handler.py`
- **Role**: Wraps Supabase client and storage operations.
- **Key Functions**:
  - `_initialize_client`: Creates a Supabase client.
  - `store_crawl_results`: Inserts URL and truncated content into the `pages` table.
  - `store_page_summary`: Upserts URL, title, summary, and optional content.

### `main.py`
- **Role**: Demonstration script.
- **Key Features**:
  - Initializes `AdvancedWebCrawler`.
  - Tests memory-adaptive crawling, semaphore dispatching, LLM analysis, and full pipeline storage.

### `tests/`
- **Role**: Pytest scripts for unit and integration testing.
- **Key Tests**:
  - `test_basic_crawling.py`: Basic Crawl4AI tests.
  - `test_crawl4ai_supabase.py`: End-to-end crawl → Supabase.
  - `test_database_operations.py`: Supabase CRUD tests.

## Workflow Diagram
```
+-----------------+ (async list of URLs)
| main.py         |-----------------------------+
+-----------------+                             |
                  v                             v
+---------------------+       +---------------------+
| AdvancedWebCrawler |       | AdvancedWebCrawler |
| crawl_with_memory  |       | crawl_with_semaphore|
+---------------------+       +---------------------+
                  |                             |
returns list of crawl results   returns list of basic results
                  |                             |
                  +-----------------------------+
                                    |
                                    v
                        +-----------------------------+
                        | crawl_with_llm_analysis     |
                        | - builds LLMExtractionStrategy |
                        | - uses PageSummary schema   |
                        +-----------------------------+
                                    |
returns analyses                   |
                                    v
                        +-------------------------------------------+
                        | crawl_and_store_in_supabase              |
                        | - loops through analyzed results         |
                        | - calls store_page_summary               |
                        +-------------------------------------------+
                                    |
                                    v
                        +---------------------------------------------+
                        | SupabaseHandler.store_page_summary         |
                        | - upserts (url, title, summary, content)   |
                        +---------------------------------------------+
```

## Configuration & Environment Variables
- **`.env`**: Must define `SUPABASE_URL`, `SUPABASE_KEY`, and `OPENAI_API_KEY`.
- **Crawler Config**:
  - `BrowserConfig`: Parameters include headless mode, browser type, user agent.
  - `CrawlerRunConfig`: Settings include cache mode, word count, extraction strategy.
- **Dispatchers**:
  - `MemoryAdaptiveDispatcher`: Pauses based on RAM usage; includes rate limiter.
  - `SemaphoreDispatcher`: Fixed concurrency.
- **LLM Extraction**:
  - Define a `PageSummary` schema.
  - Specify `LLMExtractionStrategy` parameters (provider, API token, instruction, chunking).
- **Supabase Client**:
  - Initialized via `create_client(SUPABASE_URL, SUPABASE_KEY)`.
  - Local commands:
    - `supabase init`: Set up a project.
    - `supabase start`: Launch services.
    - `supabase stop`: Stop services.

## Limitations & Next Steps

### Current Limitations
1. **Manual URL List**: `main.py` hard-codes test URLs.
2. **Schema Rigidity**: `PageSummary` contains only title and summary.
3. **Error Handling**: Minimal logging; no retry/backoff logic.
4. **Supabase Table Schema**: Assumes `pages` table with `url`, `title`, `summary`, `content` columns.
5. **Client Dependencies**: Requires the Supabase Python client.

### Next Steps
1. **Automate Ingestion**: Integrate a queue or scheduler for dynamic URL supply.
2. **Custom Extraction**: Extend `schemas.py` for domain-specific data (e.g., prices, code examples).
3. **Database Migrations**: Ensure alignment between migrations and `store_page_summary` fields.
4. **Monitoring & Logging**: Use logging libraries and Crawl4AI monitor API for real-time dashboards.
5. **Cost Optimization**: Implement schema-based extraction as a fallback to reduce LLM costs.

---

### References
- [async_crawler.py](https://github.com/Gaya56/supa-crawl/blob/LLM-playground/src/crawlers/async_crawler.py)
- [supabase_handler.py](https://github.com/Gaya56/supa-crawl/blob/LLM-playground/src/storage/supabase_handler.py)
- [main.py](https://github.com/Gaya56/supa-crawl/blob/LLM-playground/main.py)
- [environment.py](https://github.com/Gaya56/supa-crawl/blob/LLM-playground/src/config/environment.py)
- [LLM Strategies - Crawl4AI Documentation](https://docs.crawl4ai.com/extraction/llm-strategies/)
- [Supabase CLI Docs](https://supabase.com/docs/guides/local-development/cli/getting-started)
