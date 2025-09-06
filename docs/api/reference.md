# API Reference

Complete documentation for all Supa-Crawl components and methods.

## Core Classes

### AdvancedWebCrawler

The main crawling engine with multiple dispatch strategies and LLM integration.

#### Methods

##### `crawl_with_memory_adaptive_dispatcher(urls: List[str]) -> List[Dict[str, Any]]`

Crawls URLs using memory-adaptive resource management.

**Parameters:**
- `urls` (List[str]): List of URLs to crawl

**Returns:**
- `List[Dict[str, Any]]`: Crawl results with URL, raw_markdown, and metadata

**Example:**
```python
crawler = AdvancedWebCrawler()
results = await crawler.crawl_with_memory_adaptive_dispatcher([
    "https://example.com",
    "https://docs.crawl4ai.com"
])
```

##### `crawl_with_semaphore_dispatcher(urls: List[str]) -> List[Dict[str, Any]]`

Crawls URLs with controlled concurrency using semaphore pattern.

**Parameters:**
- `urls` (List[str]): List of URLs to crawl

**Returns:**
- `List[Dict[str, Any]]`: Crawl results with timing and success metrics

**Example:**
```python
results = await crawler.crawl_with_semaphore_dispatcher(urls)
for result in results:
    print(f"URL: {result['url']}, Success: {result['success']}")
```

##### `crawl_with_llm_analysis(urls: List[str]) -> List[Dict[str, Any]]`

Performs intelligent crawling with LLM-powered content analysis.

**Parameters:**
- `urls` (List[str]): List of URLs to crawl and analyze

**Returns:**
- `List[Dict[str, Any]]`: Results including LLM analysis with title and summary

**Response Structure:**
```python
{
    'url': 'https://example.com',
    'raw_markdown': '# Example Domain...',
    'analysis': [{
        'title': 'Example Domain',
        'summary': 'A demonstration page for documentation examples.'
    }],
    'success': True
}
```

**Example:**
```python
results = await crawler.crawl_with_llm_analysis([
    "https://docs.crawl4ai.com"
])

for result in results:
    analysis = result['analysis'][0]
    print(f"Title: {analysis['title']}")
    print(f"Summary: {analysis['summary']}")
```

##### `crawl_and_store_in_supabase(urls: List[str]) -> bool`

Complete pipeline: crawl URLs, perform LLM analysis, and store in Supabase.

**Parameters:**
- `urls` (List[str]): List of URLs to process

**Returns:**
- `bool`: True if all operations completed successfully

**Example:**
```python
success = await crawler.crawl_and_store_in_supabase([
    "https://example.com",
    "https://docs.crawl4ai.com/api/parameters/"
])

if success:
    print("All URLs processed and stored successfully!")
```

### SupabaseHandler

Manages database operations and data persistence.

#### Methods

##### `store_page_summary(url: str, title: str, summary: str, raw_markdown: str = None) -> Dict[str, Any]`

Stores page analysis results using the structured schema.

**Parameters:**
- `url` (str): The webpage URL
- `title` (str): AI-generated page title
- `summary` (str): AI-generated content summary
- `raw_markdown` (str, optional): Raw page content

**Returns:**
- `Dict[str, Any]`: Supabase response object

**Example:**
```python
storage = SupabaseHandler()
response = storage.store_page_summary(
    url="https://example.com",
    title="Example Domain",
    summary="A demonstration page for documentation examples.",
    raw_markdown="# Example Domain\nThis domain is for use in examples..."
)
```

##### `store_crawl_results(results: List[Dict[str, Any]]) -> int`

Legacy method for storing crawl results (use store_page_summary for new code).

**Parameters:**
- `results` (List[Dict[str, Any]]): List of crawl result dictionaries

**Returns:**
- `int`: Number of successfully stored records

#### Properties

##### `is_available: bool`

Indicates whether Supabase client is properly configured and available.

**Example:**
```python
storage = SupabaseHandler()
if storage.is_available:
    print("Supabase connection ready")
else:
    print("Check SUPABASE_URL and SUPABASE_KEY environment variables")
```

## Data Models

### PageSummary

Pydantic model defining the structure for LLM-extracted content.

```python
from pydantic import BaseModel, Field

class PageSummary(BaseModel):
    title: str = Field(description="The main title of the web page")
    summary: str = Field(description="A short paragraph summary of the page content")
```

**Usage in LLM Strategy:**
```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy

strategy = LLMExtractionStrategy(
    provider="openai/gpt-4o-mini",
    api_token=os.getenv('OPENAI_API_KEY'),
    schema=PageSummary.model_json_schema(),
    instruction="Extract the main title and create a concise summary..."
)
```

## Configuration Classes

### Environment Configuration

Managed by `src/config/environment.py`:

```python
from src.config.environment import env_config

# Access configuration
print(f"Supabase URL: {env_config.supabase_url}")
print(f"OpenAI configured: {env_config.openai_api_key is not None}")
```

## Error Handling

All methods include comprehensive error handling:

```python
try:
    results = await crawler.crawl_with_llm_analysis(urls)
    if not results:
        print("No results returned - check URLs and network connection")
except Exception as e:
    print(f"Crawling failed: {str(e)}")
```

## Database Schema

### Pages Table

```sql
CREATE TABLE pages (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url TEXT NOT NULL,
    title TEXT,           -- AI-generated title
    summary TEXT,         -- AI-generated summary
    content TEXT          -- Raw markdown content
);
```

### Query Examples

```sql
-- Get all pages with summaries
SELECT url, title, summary FROM pages WHERE summary IS NOT NULL;

-- Search by title content
SELECT * FROM pages WHERE title ILIKE '%crawl4ai%';

-- Get recent entries
SELECT * FROM pages ORDER BY id DESC LIMIT 10;
```

## Rate Limiting & Performance

### Concurrency Control

```python
# Semaphore dispatcher with custom limits
from asyncio import Semaphore

# Configure in crawler initialization
MAX_CONCURRENT = 5
semaphore = Semaphore(MAX_CONCURRENT)
```

### Memory Management

```python
# Memory adaptive dispatcher automatically adjusts based on:
# - Content size
# - Available system memory  
# - Processing complexity
```

## Response Formats

### Standard Crawl Result

```python
{
    'url': 'https://example.com',
    'raw_markdown': '# Page Content...',
    'success': True,
    'error': None,
    'timestamp': '2025-09-06T04:00:00Z'
}
```

### LLM Analysis Result

```python
{
    'url': 'https://example.com',
    'raw_markdown': '# Page Content...',
    'analysis': [{
        'title': 'Page Title',
        'summary': 'Content summary...'
    }],
    'success': True,
    'llm_tokens_used': 150
}
```

### Supabase Storage Response

```python
{
    'data': [{
        'id': 42,
        'url': 'https://example.com',
        'title': 'Page Title',
        'summary': 'Content summary...',
        'content': '# Page Content...'
    }],
    'count': 1,
    'status': 201
}
```