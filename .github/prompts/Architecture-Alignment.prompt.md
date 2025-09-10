# file breakdown

- LLM-powered web intelligence pipeline structured into config, crawling, models, and storage layers. Environment and crawler settings are centralized; multiple crawl modes are supported, including memory-adaptive, semaphore-based, and LLM-assisted extraction with GPT‑4o‑mini. Pydantic schemas define the extraction output for reliable parsing. Results are upserted into Supabase with health checks and defensive error handling. Design mirrors Crawl4AI and Supabase best practices, enabling easy swaps of dispatchers, LLMs, or storage backends.

## Repository Overview

The `src/` directory is organized into four main packages—`config`, `crawlers`, `models`, and `storage`—plus a top-level `__init__.py`. Together they implement an LLM‑powered web intelligence workflow that pulls environment settings from `.env`,
 crawls pages with Crawl4AI, extracts structured data via GPT‑4o‑mini, 
and persists results to Supabase. Each module mirrors patterns from the 
official Crawl4AI and Supabase documentation, ensuring compatibility and
 clarity.

---

### 1. `src/config/environment.py`

**Purpose & Role:**

Centralizes environment and crawler configuration. `EnvironmentConfig` loads `SUPABASE_URL`, `SUPABASE_KEY`, and `OPENAI_API_KEY` using `python-dotenv` and validates their presence, warning when keys are missing. `CrawlerConfig` exposes factory methods for generating `BrowserConfig` and `CrawlerRunConfig`
 objects, matching examples in the Crawl4AI docs. This file keeps 
runtime settings in one place, so other modules can simply import `env_config` or `crawler_config`.

**Key Functions & Classes:**

- `EnvironmentConfig._validate_environment` prints warnings for absent variables.
- `EnvironmentConfig.has_supabase_config` / `has_openai_config` quickly tell the rest of the system if external services are ready.
- `CrawlerConfig.create_browser_config` and `create_crawler_run_config` encapsulate official parameter defaults such as `CacheMode.BYPASS` and `use_managed_browser=True`.

**Alignment with Docs:**

Inline comments reference the Crawl4AI browser/dispatcher documentation 
and Supabase initialization pages. Implementation follows those patterns
 verbatim, ensuring that future upgrades to Crawl4AI or Supabase SDKs 
can reuse the same configuration structure.

---

### 2. `src/crawlers/async_crawler.py`

**Purpose & Role:**

Implements `AdvancedWebCrawler`, a high‑level orchestration class that wraps `crawl4ai.AsyncWebCrawler`
 with multiple dispatch strategies, LLM extraction, and database 
storage. It shows three crawl modes—memory adaptive, semaphore‑based, 
and LLM‑assisted—then exposes a fourth workflow that persists summaries 
to Supabase.

**Key Functions & Workflows:**

- `crawl_with_memory_adaptive_dispatcher` uses `MemoryAdaptiveDispatcher` with a `RateLimiter` and `CrawlerMonitor` to dynamically throttle tasks when memory crosses 90%.
- `crawl_with_semaphore_dispatcher` switches to `SemaphoreDispatcher` for deterministic concurrency limits.
- `crawl_with_llm_analysis` configures `LLMExtractionStrategy` using `PageSummary.model_json_schema()`; GPT‑4o‑mini returns structured title/summary JSON parsed with `json.loads`.
- `crawl_and_store_in_supabase` calls `crawl_with_llm_analysis`, then for each result extracts title and summary and delegates persistence to `SupabaseHandler.store_page_summary`.

**Integration Notes:**

The file mirrors examples from Crawl4AI’s quickstart, multi‑URL 
crawling, and LLM extraction docs. It also respects Supabase 
requirements by checking `env_config.has_openai_config` and `self.storage_handler.is_available`
 before invoking the network. Error handling covers JSON decode issues 
and missing URLs, ensuring idempotent upsert behavior downstream.

---

### 3. `src/models/schemas.py`

**Purpose & Role:**

Defines Pydantic models that describe both the LLM extraction schema and the overall crawler response envelope. `PageSummary` declares the fields GPT‑4o‑mini should return—`title` and `summary`—matching the `schema` block passed to `LLMExtractionStrategy`. `CrawlResult` and `Crawl4AIResponse` provide structured containers for more complex workflows.

**Key Classes:**

- `PageSummary`: Field-level descriptions help LLMs infer desired output; documentation cites official Crawl4AI extraction guidance.
- `CrawlResult` & `Crawl4AIResponse`: Compose results, enabling validation and downstream typing if the project grows.

**Alignment:**

These schemas line up with Crawl4AI’s recommended approach: design a 
Pydantic model, feed its JSON schema to the extraction strategy, and 
parse the returned JSON into the same model.

---

### 4. `src/storage/supabase_handler.py`

**Purpose & Role:**

Manages all Supabase interactions. On instantiation, it uses `env_config` to create a `supabase.Client`. Methods cover health checks, page summarization upserts, and a legacy `store_crawl_results` that formats Markdown into a compact first paragraph.

**Key Functions & Classes:**

- `_initialize_client` handles setup and logs failures, exactly as shown in Supabase’s Python initialization docs.
- `_extract_first_paragraph` trims Markdown to ~500 characters for storage efficiency.
- `store_page_summary` assembles an upsert payload containing `url`, `title`, `summary`, and optional `content`, then executes `client.table("pages").upsert(data).execute()`.
- `check_connection` runs a lightweight `select` to confirm connectivity.

**Alignment:**

Every interaction—`create_client`, `table().insert()`, `upsert()`—tracks
 the official Supabase API. The code provides defensive checks around 
missing clients and wraps calls in try/except to avoid crashing during 
transient network issues.

---

### 5. Package `__init__.py` Files

Each package (`src`, `config`, `crawlers`, `models`, `storage`) includes a minimal `__init__.py`. They serve as namespace markers, enabling relative imports (e.g., `from ..config.environment import env_config`).
 Although they contain only comments now, they maintain Python package 
semantics and can later expose package-level symbols if needed.

---

## Overall Workflow & Architecture

1. **Configuration Layer:** `EnvironmentConfig` reads credentials and flags; `CrawlerConfig` supplies reusable Crawl4AI settings. These globals allow the rest of the stack to remain declarative and testable.
2. **Crawling Layer:** `AdvancedWebCrawler` bootstraps Crawl4AI with `BrowserConfig` from `config`, then selects the desired dispatcher and, if configured, attaches an LLM extraction strategy.
3. **Modeling Layer:** Pydantic schemas define the expected format for LLM output, ensuring consistent parsing and easy validation.
4. **Storage Layer:** `SupabaseHandler` encapsulates database logic, performing idempotent upserts of titles and summaries. The crawler’s `crawl_and_store_in_supabase` method bridges crawling and storage, demonstrating an end‑to‑end pipeline.

This
 modular design mirrors best practices from official Crawl4AI and 
Supabase documentation while remaining extensible: new dispatchers, 
alternative LLM providers, or different storage backends can be plugged 
in with minimal friction.