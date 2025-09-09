---
applyTo: '**'
---
## Supa-crawl (supabase-docs): Architecture and Workflow

### Overview

Supa-crawl is a Python web-crawling pipeline that integrates Crawl4AI with Supabase for storage. It supports multi-URL crawling, rate limiting, and LLM-powered JSON summarization.

- Headless Chromium via BrowserConfig
- Two dispatcher modes: memory-adaptive and semaphore
- LLM extraction strategy for structured summaries
- Optional Supabase upsert for URL, title, summary, and content
- Orchestrated by [main.py](http://main.py)

### High-level Architecture

1. Configure browser and run parameters
2. Crawl URLs with selected dispatcher
3. Optionally run LLM extraction to produce JSON summaries
4. Persist results to Supabase

### Key Components

- Config: src/config/[environment.py](http://environment.py)
    - Loads SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY
    - Builds BrowserConfig and CrawlerRunConfig defaults
- Models: src/models/[schemas.py](http://schemas.py)
    - PageSummary Pydantic schema for LLM outputs
- Crawler: src/crawlers/async_[crawler.py](http://crawler.py)
    - AdvancedWebCrawler with dispatcher variants and LLM analysis
- Storage: src/storage/supabase_[handler.py](http://handler.py)
    - Supabase client init, content trimming, insert and upsert helpers
- Entrypoint: [main.py](http://main.py)
    - Demonstrates dispatcher usage, LLM analysis, and storage

### Workflows

- Memory-adaptive crawl
    - Uses MemoryAdaptiveDispatcher for adaptive concurrency and rate limiting
- Semaphore crawl
    - Uses SemaphoreDispatcher for fixed concurrency
- LLM analysis
    - Builds LLMExtractionStrategy with prompt and schema, returns parsed JSON
- Store in Supabase
    - Upserts url, title, summary, optional content

### Minimal Sequence Diagram

> [[main.py](http://main.py)] → AdvancedWebCrawler
> 

> → crawl_with_memory_adaptive_dispatcher or crawl_with_semaphore_dispatcher
> 

> → crawl_with_llm_analysis
> 

> → crawl_and_store_in_supabase → [SupabaseHandler.store](http://SupabaseHandler.store)_page_summary
> 

### Directory Overview

supa-crawl/

- src/
    - config/
        - [environment.py](http://environment.py) — env loading and crawler config
    - crawlers/
        - async_[crawler.py](http://crawler.py) — AdvancedWebCrawler and crawl methods
    - models/
        - [schemas.py](http://schemas.py) — Pydantic schemas for LLM extraction
    - storage/
        - supabase_[handler.py](http://handler.py) — Supabase client and storage
- [main.py](http://main.py) — demo entrypoint
- supabase/ — migrations and config
- docs/ — documentation
- [supabase-cli-commands.md](http://supabase-cli-commands.md) — local CLI reference
- tests/ — pytest scripts

### File Roles at a Glance

- src/config/[environment.py](http://environment.py)
    - Defines EnvironmentConfig and helpers to create BrowserConfig and CrawlerRunConfig
- src/models/[schemas.py](http://schemas.py)
    - PageSummary and related wrappers for LLM outputs
- src/crawlers/async_[crawler.py](http://crawler.py)
    - AdvancedWebCrawler
        - crawl_with_memory_adaptive_dispatcher
        - crawl_with_semaphore_dispatcher
        - crawl_with_llm_analysis
        - crawl_and_store_in_supabase
- src/storage/supabase_[handler.py](http://handler.py)
    - store_crawl_results, store_page_summary
- [main.py](http://main.py)
    - Orchestrates end-to-end demo

### Setup and Requirements

- Environment variables
    - SUPABASE_URL
    - SUPABASE_KEY
    - OPENAI_API_KEY
- Supabase CLI basics
    - Initialize: supabase init
    - Start local: supabase start
    - Stop: supabase stop
    - See reference: [supabase-cli-commands.md](http://supabase-cli-commands.md)

### Typical Usage

1. Populate .env with Supabase and OpenAI keys
2. Run [main.py](http://main.py)
3. Inspect results in Supabase pages table