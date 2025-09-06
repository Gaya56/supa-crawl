---
mode: agent
---

# Task: Implement Crawl4AI LLM Title/Summary Extraction → Supabase Storage

## Objective
Implement a complete end-to-end pipeline that:
1. Uses Crawl4AI's LLMExtractionStrategy to extract title + summary from web pages
2. Stores results in Supabase using official upsert patterns
3. Follows official documentation patterns exactly
4. Maintains existing class/file structure without renaming

## Requirements

### Files to Modify (DO NOT rename or move):
- `src/models/schemas.py` → Update PageSummary schema for LLM extraction
- `src/crawlers/async_crawler.py` → Wire LLMExtractionStrategy in AdvancedWebCrawler
- `src/storage/supabase_handler.py` → Add store_page_summary() method using upsert

### Official Documentation Sources (ONLY allowed references):
- Crawl4AI LLM strategies: https://docs.crawl4ai.com/extraction/llm-strategies/
- Supabase Python upsert: https://supabase.com/docs/reference/python/upsert

### Success Criteria:
1. PageSummary schema correctly defined for LLM extraction (title, summary only)
2. LLMExtractionStrategy properly configured with OpenAI provider
3. Supabase upsert method implemented following official patterns
4. Complete usage example demonstrating the full pipeline
5. All code follows official documentation patterns exactly

## Implementation Steps

### Step 1: Update PageSummary Schema
- Modify `src/models/schemas.py`
- Remove `url` field from PageSummary (url is metadata, not extracted content)
- Add Field descriptions for LLM guidance
- Follow Pydantic BaseModel pattern from official docs

### Step 2: Configure LLMExtractionStrategy
- Modify `src/crawlers/async_crawler.py`
- Update existing `crawl_with_llm_analysis()` method
- Use LLMConfig with "openai/gpt-4o-mini" provider
- Set extraction_type="schema"
- Configure proper instruction for title/summary extraction
- Follow official CrawlerRunConfig pattern

### Step 3: Implement Supabase Storage
- Modify `src/storage/supabase_handler.py`
- Add store_page_summary(url, title, summary, raw_markdown, content_hash=None)
- Use official Supabase upsert pattern: client.table("pages").upsert(data).execute()
- Handle unique constraint on url field
- Return success/failure status

### Step 4: Create Usage Example
- Demonstrate complete pipeline in 10-15 lines
- Show crawl → extract → store workflow
- Include error handling

## Constraints
1. Keep all existing class names: AdvancedWebCrawler, PageSummary, SupabaseHandler
2. No file renaming or moving
3. Follow official documentation patterns exactly
4. Minimal code changes - only what's necessary
5. Reference official URLs in code comments
6. Use existing environment configuration

## Expected Output
Working pipeline that extracts structured title/summary data from web pages and stores in Supabase using official patterns from both Crawl4AI and Supabase documentation.