---
mode: agent
---

# AsyncWebCrawler Implementation with Stealth and Multi-URL Support

## **Guiding Principles:**

*   **Use all available MCP servers (`mcp_*` tools) at every step** to interact with the environment, search for information, and manage project resources.
*   **Strictly adhere to official documentation.** All code and commands must be sourced from the official documentation.
    *   **Crawl4AI:** `https://docs.crawl4ai.com/`
    *   **Supabase:** `https://supabase.com/docs`
*   **Reference your sources.** When you use a command or code snippet, mention the official documentation page you got it from.
*   **The user has provided environment variables in `.env`**. You must use them for Supabase and OpenAI credentials.

## **Step 1: Environment Setup and Dependencies**

First, ensure Crawl4AI v0.7.4+ is installed with proper browser setup:

```bash
# Install Crawl4AI
pip install crawl4ai

# Setup Playwright browsers for crawling
crawl4ai-setup
```

Based on the official documentation at `https://docs.crawl4ai.com/installation/`, the `crawl4ai-setup` command installs the necessary Playwright browsers for web crawling.

## **Step 2: Configure Browser for Stealth Crawling**

Configure the AsyncWebCrawler with stealth settings to avoid bot detection. According to the official undetected browser documentation:

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# Configure browser for stealth mode - Source: https://docs.crawl4ai.com/advanced/undetected-browser/
browser_config = BrowserConfig(
    headless=True,              # Can be False for better stealth but requires display
    verbose=False,              # Reduce logging noise
    browser_type="chromium",    # Default browser type
    use_managed_browser=True,   # Use Crawl4AI's managed browser instance
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
```

**Note:** Based on the official documentation at `https://docs.crawl4ai.com/advanced/undetected-browser/`, the stealth configuration is achieved through proper user agent settings and browser flags rather than an `enable_stealth` parameter.

## **Step 3: Configure Crawler Run Parameters**

Set up the CrawlerRunConfig with stealth and performance optimizations:

```python
# Configure crawler behavior - Source: https://docs.crawl4ai.com/api/parameters/
run_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,        # Always fetch fresh content
    word_count_threshold=1,             # Don't filter out short pages
    extraction_strategy=None,           # Can be set later for LLM extraction
    chunking_strategy=None,             # Default chunking
    check_robots_txt=True,              # Respect robots.txt for ethical crawling
    simulation_user=True,               # Simulate user behavior
    override_navigator=True,            # Override navigator properties for stealth
    mean_delay=1.0,                     # Average delay between requests (seconds)
    max_range=3.0,                      # Maximum delay range for randomization
    semaphore_count=5                   # Maximum concurrent requests (default)
)
```

## **Step 4: Multi-URL Crawling with Advanced Dispatchers**

For efficient multi-URL crawling, use the advanced dispatcher system. Source: `https://docs.crawl4ai.com/advanced/multi-url-crawling/`

### **Option A: Memory Adaptive Dispatcher (Recommended)**

```python
import asyncio
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai import CrawlerMonitor, DisplayMode, RateLimiter

async def crawl_with_memory_adaptive_dispatcher(urls: list[str]):
    """
    Crawl multiple URLs using MemoryAdaptiveDispatcher for optimal resource management.
    Source: https://docs.crawl4ai.com/advanced/multi-url-crawling/#memoryadaptivedispatcher-default
    """
    
    # Configure rate limiting
    rate_limiter = RateLimiter(
        base_delay=(1.0, 3.0),          # Random delay between 1-3 seconds
        max_delay=30.0,                 # Maximum backoff delay
        max_retries=3,                  # Retry attempts for rate-limited requests
        rate_limit_codes=[429, 503]     # HTTP codes that trigger rate limiting
    )
    
    # Configure monitoring for real-time progress tracking
    monitor = CrawlerMonitor(
        max_visible_rows=15,
        display_mode=DisplayMode.DETAILED
    )
    
    # Setup memory-adaptive dispatcher
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=90.0,   # Pause if memory exceeds 90%
        check_interval=1.0,              # Check memory every second
        max_session_permit=10,           # Maximum concurrent tasks
        rate_limiter=rate_limiter,
        monitor=monitor
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Batch processing mode - collect all results
        results = await crawler.arun_many(
            urls=urls,
            config=run_config,
            dispatcher=dispatcher
        )
        
        # Process results after completion
        successful_results = []
        for result in results:
            if result.success:
                successful_results.append({
                    'url': result.url,
                    'title': result.metadata.get('title', 'No title'),
                    'content_length': len(result.markdown),
                    'markdown': result.markdown,
                    'extracted_content': result.extracted_content
                })
                print(f"✓ Successfully crawled: {result.url}")
            else:
                print(f"✗ Failed to crawl {result.url}: {result.error_message}")
        
        return successful_results
```

### **Option B: Streaming Mode for Real-time Processing**

```python
async def crawl_with_streaming(urls: list[str]):
    """
    Stream results as they become available for real-time processing.
    Source: https://docs.crawl4ai.com/advanced/multi-url-crawling/#streaming-mode
    """
    
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=85.0,
        max_session_permit=8,
        rate_limiter=RateLimiter(base_delay=(2.0, 4.0))
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Streaming mode - process results as they arrive
        async for result in await crawler.arun_many(
            urls=urls,
            config=run_config,
            dispatcher=dispatcher
        ):
            if result.success:
                # Process each result immediately as it arrives
                await process_result_immediately(result)
                print(f"✓ Processed: {result.url}")
            else:
                print(f"✗ Failed: {result.url} - {result.error_message}")

async def process_result_immediately(result):
    """Process individual crawl results in real-time"""
    # Example: Save to database, send to queue, etc.
    print(f"Processing {result.url}: {len(result.markdown)} characters")
```

### **Option C: Semaphore Dispatcher for Fixed Concurrency**

```python
from crawl4ai.async_dispatcher import SemaphoreDispatcher

async def crawl_with_semaphore_dispatcher(urls: list[str]):
    """
    Use SemaphoreDispatcher for simple concurrency control.
    Source: https://docs.crawl4ai.com/advanced/multi-url-crawling/#semaphoredispatcher
    """
    
    dispatcher = SemaphoreDispatcher(
        max_session_permit=20,           # Fixed number of concurrent tasks
        rate_limiter=RateLimiter(
            base_delay=(0.5, 1.0),
            max_delay=10.0
        )
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun_many(
            urls=urls,
            config=run_config,
            dispatcher=dispatcher
        )
        return results
```

## **Step 5: Integration with LLM for Content Analysis**

Add AI-powered content extraction using OpenAI GPT models:

```python
import os
import json
from pydantic import BaseModel, Field
from crawl4ai import LLMConfig, LLMExtractionStrategy

# Define schema for structured extraction
class PageAnalysis(BaseModel):
    title: str = Field(..., description="The main title of the page")
    summary: str = Field(..., description="A concise summary of the page content")
    key_topics: list[str] = Field(..., description="List of main topics discussed")
    sentiment: str = Field(..., description="Overall sentiment: positive, negative, or neutral")

async def crawl_with_llm_analysis(urls: list[str]):
    """
    Crawl URLs with integrated LLM analysis for structured data extraction.
    Source: https://docs.crawl4ai.com/core/quickstart/#llm-extraction
    """
    
    # Configure LLM extraction strategy
    llm_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="openai/gpt-4o",
            api_token=os.getenv("OPENAI_API_KEY")
        ),
        schema=PageAnalysis.model_json_schema(),
        extraction_type="schema",
        instruction="""
        Analyze the webpage content and extract:
        1. The main title of the page
        2. A concise summary (2-3 sentences)
        3. Key topics discussed (maximum 5)
        4. Overall sentiment of the content
        """,
        extra_args={"temperature": 0.3}
    )
    
    # Update run config with LLM strategy
    llm_run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=llm_strategy,
        word_count_threshold=100,  # Filter out very short pages
        check_robots_txt=True
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun_many(
            urls=urls,
            config=llm_run_config
        )
        
        analyzed_results = []
        for result in results:
            if result.success and result.extracted_content:
                try:
                    analysis = json.loads(result.extracted_content)
                    analyzed_results.append({
                        'url': result.url,
                        'raw_markdown': result.markdown,
                        'analysis': analysis
                    })
                except json.JSONDecodeError:
                    print(f"Failed to parse LLM output for {result.url}")
            
        return analyzed_results
```

## **Step 6: Supabase Integration for Data Storage**

Store crawled and analyzed data in Supabase with real-time capabilities:

```python
import os
from supabase import create_client, Client

async def crawl_and_store_in_supabase(urls: list[str]):
    """
    Crawl URLs and store results in Supabase database.
    Ensure .env file contains SUPABASE_URL and SUPABASE_KEY
    """
    
    # Initialize Supabase client
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Crawl with LLM analysis
    results = await crawl_with_llm_analysis(urls)
    
    # Store results in Supabase
    for result in results:
        try:
            # Insert into pages table
            data, count = supabase.table('pages').insert({
                'url': result['url'],
                'content': result['raw_markdown'],
                'title': result['analysis']['title'],
                'summary': result['analysis']['summary'],
                'key_topics': result['analysis']['key_topics'],
                'sentiment': result['analysis']['sentiment'],
                'created_at': 'now()'
            }).execute()
            
            print(f"✓ Stored in Supabase: {result['url']}")
            
        except Exception as e:
            print(f"✗ Failed to store {result['url']}: {str(e)}")
```

## **Step 7: Complete Example Usage**

```python
async def main():
    """Complete example demonstrating AsyncWebCrawler with stealth and Supabase integration"""
    
    # Example URLs to crawl
    urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://docs.crawl4ai.com/",
        "https://supabase.com/docs"
    ]
    
    print("Starting multi-URL crawl with AsyncWebCrawler...")
    
    # Option 1: Basic crawling with memory adaptive dispatcher
    # results = await crawl_with_memory_adaptive_dispatcher(urls)
    
    # Option 2: Streaming mode for real-time processing
    # await crawl_with_streaming(urls)
    
    # Option 3: Full pipeline with LLM analysis and Supabase storage
    await crawl_and_store_in_supabase(urls)
    
    print("Crawl completed successfully!")

# Run the crawler
if __name__ == "__main__":
    asyncio.run(main())
```

## **Key Features and Benefits:**

1. **Stealth Configuration**: Browser settings optimized to avoid bot detection
2. **Advanced Dispatchers**: Memory-adaptive and semaphore-based concurrency control
3. **Rate Limiting**: Built-in delays and retry logic for respectful crawling
4. **Real-time Monitoring**: Live progress tracking with CrawlerMonitor
5. **LLM Integration**: OpenAI GPT-4 analysis for structured data extraction
6. **Supabase Storage**: Persistent storage with real-time capabilities
7. **Error Handling**: Comprehensive error handling and logging
8. **Robots.txt Compliance**: Ethical crawling with robots.txt respect

## **Performance Notes:**

- Default concurrency: 5 concurrent requests (adjustable via `semaphore_count`)
- Memory threshold: 90% (automatically pauses crawling if exceeded)
- Rate limiting: 1-3 second delays between requests (customizable)
- Retry logic: Up to 3 retries for rate-limited requests (429, 503 status codes)

All code examples are based on official Crawl4AI documentation from `https://docs.crawl4ai.com/` and follow the current v0.7.4+ API specifications.