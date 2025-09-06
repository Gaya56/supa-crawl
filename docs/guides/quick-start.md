# 🚀 Quick Start Guide

## Getting Started with AsyncWebCrawler

This guide will help you get up and running with the AsyncWebCrawler Advanced Implementation in under 10 minutes.

## Prerequisites

- Python 3.8+
- Active internet connection
- Supabase account (for storage features)
- OpenAI API key (for LLM analysis)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd asyncwebcrawler-advanced
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory:

```env
# Required: Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Optional: OpenAI Configuration (for LLM analysis)
OPENAI_API_KEY=your_openai_api_key
```

### 4. Database Setup
Make sure your Supabase project has a `pages` table with this structure:

```sql
CREATE TABLE pages (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    content TEXT,
    analysis_header TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Your First Crawl

### Basic Crawling Example
```python
import asyncio
from src.crawlers.async_crawler import AdvancedWebCrawler

async def first_crawl():
    # Initialize crawler
    crawler = AdvancedWebCrawler()
    
    # Crawl some URLs
    urls = [
        "https://docs.crawl4ai.com/",
        "https://example.com"
    ]
    
    # Use memory adaptive dispatcher
    results = await crawler.crawl_with_memory_adaptive_dispatcher(urls)
    
    # Display results
    for result in results:
        print(f"✅ URL: {result.url}")
        print(f"📄 Content Length: {len(result.content)} chars")
        print(f"🕐 Timestamp: {result.timestamp}")
        print("-" * 50)

# Run the crawler
asyncio.run(first_crawl())
```

**Expected Output:**
```
✅ URL: https://docs.crawl4ai.com/
📄 Content Length: 2547 chars
🕐 Timestamp: 2024-01-20 10:30:45.123456
--------------------------------------------------
✅ URL: https://example.com
📄 Content Length: 1256 chars
🕐 Timestamp: 2024-01-20 10:30:46.234567
--------------------------------------------------
```

## Common Use Cases

### 1. Simple Content Extraction
Perfect for gathering content from multiple pages quickly.

```python
async def extract_content():
    crawler = AdvancedWebCrawler()
    
    urls = [
        "https://news.ycombinator.com/",
        "https://github.com/trending",
        "https://stackoverflow.com/questions"
    ]
    
    results = await crawler.crawl_with_semaphore_dispatcher(urls)
    
    for result in results:
        if result.success:
            print(f"Extracted {len(result.content)} chars from {result.url}")
        else:
            print(f"Failed to crawl {result.url}")

asyncio.run(extract_content())
```

### 2. AI-Powered Analysis
Extract structured information using OpenAI GPT-4o.

```python
async def ai_analysis():
    crawler = AdvancedWebCrawler()
    
    # Analyze documentation pages
    urls = [
        "https://docs.crawl4ai.com/introduction/",
        "https://docs.crawl4ai.com/api/parameters/"
    ]
    
    results = await crawler.crawl_with_llm_analysis(urls)
    
    for result in results:
        if result.analysis:
            print(f"📖 Title: {result.analysis['title']}")
            print(f"📝 Summary: {result.analysis['summary']}")
            print("-" * 50)

asyncio.run(ai_analysis())
```

### 3. Complete Pipeline with Storage
Crawl, analyze, and store everything in Supabase.

```python
async def full_pipeline():
    crawler = AdvancedWebCrawler()
    
    urls = [
        "https://docs.crawl4ai.com/",
        "https://docs.crawl4ai.com/api/parameters/",
        "https://docs.crawl4ai.com/examples/"
    ]
    
    success = await crawler.crawl_and_store_in_supabase(urls)
    
    if success:
        print("✅ All URLs processed and stored successfully!")
        print("🔗 Check your Supabase dashboard for the results")
    else:
        print("❌ Some operations failed - check logs for details")

asyncio.run(full_pipeline())
```

## Testing Your Setup

Run the built-in test suite to verify everything is working:

```bash
python main.py
```

**Expected Output:**
```
🔧 AsyncWebCrawler Advanced Implementation Test

📊 Test Results:
Memory Adaptive: 2/2 ✅
Semaphore: 2/2 ✅
LLM Analysis: 2/2 ✅
Supabase Storage: 2/2 ✅

✅ AsyncWebCrawler implementation completed successfully!
All tests passed with 100% success rate.
```

## Configuration Options

### Browser Settings
Modify browser behavior in `src/config/environment.py`:

```python
# For debugging, you can disable headless mode
BrowserConfig(
    enable_stealth=True,
    headless=False,  # Shows browser window
    browser_type="chromium"
)
```

### Crawler Settings
Adjust crawling parameters:

```python
# For faster crawling (less polite)
CrawlerRunConfig(
    mean_delay=0.05,     # Reduced delay
    max_range=0.1,       # Less variation
    semaphore_count=10   # More concurrent operations
)
```

### LLM Analysis
Customize AI analysis instructions:

```python
llm_strategy = LLMExtractionStrategy(
    instruction="Extract the main topic, key points, and any technical specifications from this page."
)
```

## Troubleshooting

### Common Issues

#### 1. Environment Variables Not Found
```
Error: Supabase URL not configured
```
**Solution:** Check your `.env` file and ensure all required variables are set.

#### 2. Network Connectivity Issues
```
Error: Failed to connect to target website
```
**Solution:** Check your internet connection and try with different URLs.

#### 3. Supabase Connection Failed
```
Error: Could not authenticate with Supabase
```
**Solution:** Verify your Supabase URL and API key are correct.

#### 4. OpenAI API Issues
```
Error: OpenAI API key invalid
```
**Solution:** Check your OpenAI API key and account balance.

### Debug Mode
Enable detailed logging by setting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

- **Explore Advanced Features**: Check out the [Advanced Usage Guide](advanced-usage.md)
- **API Reference**: Read the [complete API documentation](../api/reference.md)
- **Architecture**: Understand the [system architecture](../architecture/overview.md)
- **Performance**: Learn about [optimization strategies](performance-tuning.md)

## Need Help?

- Check the [Troubleshooting Guide](troubleshooting.md)
- Review the [FAQ](faq.md)
- Look at example implementations in the repository

You're now ready to start crawling! 🕷️✨