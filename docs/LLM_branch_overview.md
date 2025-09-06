# Supa-Crawl LLM Branch Overview

## Title & Scope
This document provides a detailed breakdown of the `src/` directory in the Supa-Crawl LLM branch, mapping code lines to official documentation URLs for easy reference by new contributors.

## Repo Map of `src/`
- `models/`
- `crawlers/`
- `storage/`
- `config/`

## Per-file sections

### **Path & Purpose:** `src/models/schemas.py`
Defines data models for structured data extraction and storage.

### **Key Exports:**
- `PageSummary`

### **How it aligns with official docs:**
- Uses Pydantic for data validation and serialization. [Pydantic Docs](https://pydantic-docs.helpmanual.io/)

### **Code snippet:**
```python
# filepath: /workspaces/codespaces-blank/src/models/schemas.py
from pydantic import BaseModel, Field

class PageSummary(BaseModel):
    title: str = Field(description="The main title of the web page")
    summary: str = Field(description="A short paragraph summary of the page content")
```

### **Cross-refs:**
- Called from `src/crawlers/async_crawler.py` (lines 10)

---

### **Path & Purpose:** `src/crawlers/async_crawler.py`
Implements the main crawling logic using Crawl4AI.

### **Key Exports:**
- `AdvancedWebCrawler`

### **How it aligns with official docs:**
- Implements LLM extraction strategy as per [Crawl4AI LLM Integration](https://docs.crawl4ai.com/core/quickstart/#llm-extraction).
- Uses async capabilities for efficient crawling. [Crawl4AI Async](https://docs.crawl4ai.com/core/quickstart/#async-crawling)

### **Code snippet:**
```python
# filepath: /workspaces/codespaces-blank/src/crawlers/async_crawler.py
async def crawl_with_llm_analysis(self, urls: List[str]) -> List[Dict[str, Any]]:
    # Crawl URLs with integrated LLM analysis for structured data extraction.
    llm_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="openai/gpt-4o-mini",
            api_token=env_config.openai_api_key
        ),
        schema=PageSummary.model_json_schema(),
        extraction_type="schema",
        instruction="Extract the main title and create a concise summary from this web page content."
    )
```

### **Cross-refs:**
- Called from `src/crawlers/async_crawler.py` (lines 90)

---

### **Path & Purpose:** `src/storage/supabase_handler.py`
Handles interactions with the Supabase database for data storage.

### **Key Exports:**
- `SupabaseHandler`

### **How it aligns with official docs:**
- Uses Supabase's upsert functionality to avoid duplicates. [Supabase Upsert](https://supabase.com/docs/reference/python/upsert)

### **Code snippet:**
```python
# filepath: /workspaces/codespaces-blank/src/storage/supabase_handler.py
def store_page_summary(self, url: str, title: str, summary: str, raw_markdown: str = None):
    data = {
        'url': url,
        'title': title,
        'summary': summary,
        'content': self._extract_first_paragraph(raw_markdown)
    }
    return self.client.table('pages').upsert(data).execute()
```

### **Cross-refs:**
- Called from `src/crawlers/async_crawler.py` (lines 150)

---

### **Path & Purpose:** `src/config/environment.py`
Manages environment configurations and API keys.

### **Key Exports:**
- `env_config`

### **How it aligns with official docs:**
- Centralizes environment variable management. [Supabase Python Init](https://supabase.com/docs/reference/python/initialize)

### **Code snippet:**
```python
# filepath: /workspaces/codespaces-blank/src/config/environment.py
class EnvConfig:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
```

### **Cross-refs:**
- Used in `src/crawlers/async_crawler.py` (lines 30)

---

## Integration Flow
1. **URL** → Crawl4AI fetches pages → **LLM** extracts `PageSummary` (title + summary) → **Supabase** stores structured results.
   - [Crawl4AI Quickstart](https://docs.crawl4ai.com/core/quickstart/)
   - [Supabase Insert](https://supabase.com/docs/reference/python/insert)

## Table: Feature ↔ Official Doc URL
| Feature                     | Official Doc URL                                           |
|-----------------------------|-----------------------------------------------------------|
| LLM Extraction              | [Crawl4AI LLM Strategies](https://docs.crawl4ai.com/extraction/llm-strategies/) |
| Async Crawling              | [Crawl4AI Async](https://docs.crawl4ai.com/core/quickstart/#async-crawling) |
| Upsert Functionality        | [Supabase Upsert](https://supabase.com/docs/reference/python/upsert) |
| Environment Management       | [Supabase Python Init](https://supabase.com/docs/reference/python/initialize) |
| Rate Limiting               | [Crawl4AI Rate Limiting](https://docs.crawl4ai.com/advanced/rate-limiting/) |
| Error Handling              | [Crawl4AI Error Handling](https://docs.crawl4ai.com/core/error-handling/) |
| Schema Validation           | [Pydantic Docs](https://pydantic-docs.helpmanual.io/) |
| Memory Management           | [Crawl4AI Memory Management](https://docs.crawl4ai.com/advanced/memory-management/) |

## Gaps/Questions
- Need official ref for specific error handling patterns in Crawl4AI.

## Quickstart
1. Set environment variables for OpenAI and Supabase.
2. Run `main.py` to start the crawling process.

## Appendix: Line-Anchored Index
| Path                                      | Lines         | Doc URL                                           |
|-------------------------------------------|---------------|---------------------------------------------------|
| `src/models/schemas.py`                   | 1–6           | [Pydantic Docs](https://pydantic-docs.helpmanual.io/) |
| `src/crawlers/async_crawler.py`           | 1–150         | [Crawl4AI LLM Integration](https://docs.crawl4ai.com/core/quickstart/#llm-extraction) |
| `src/storage/supabase_handler.py`         | 1–20          | [Supabase Upsert](https://supabase.com/docs/reference/python/upsert) |
| `src/config/environment.py`               | 1–10          | [Supabase Python Init](https://supabase.com/docs/reference/python/initialize) |
