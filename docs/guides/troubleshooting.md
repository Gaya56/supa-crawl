# 🔧 Troubleshooting Guide

## Common Issues and Solutions

This guide helps you resolve common issues encountered while using the AsyncWebCrawler Advanced Implementation.

## Table of Contents
- [Environment Setup Issues](#environment-setup-issues)
- [Crawling Problems](#crawling-problems)
- [LLM Analysis Issues](#llm-analysis-issues)
- [Supabase Connection Problems](#supabase-connection-problems)
- [Performance Issues](#performance-issues)
- [Error Codes Reference](#error-codes-reference)

## Environment Setup Issues

### Issue: Environment Variables Not Found
```
Error: Supabase URL not configured
KeyError: 'SUPABASE_URL'
```

**Cause:** Missing or incorrectly named environment variables.

**Solution:**
1. Check your `.env` file exists in the project root:
```bash
ls -la .env
```

2. Verify the variable names are correct:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
OPENAI_API_KEY=sk-your_openai_key_here
```

3. Make sure no extra spaces around the `=` sign:
```env
# ❌ Wrong
SUPABASE_URL = https://...

# ✅ Correct  
SUPABASE_URL=https://...
```

4. Restart your application after changing `.env`:
```bash
python main.py
```

### Issue: Module Import Errors
```
ModuleNotFoundError: No module named 'crawl4ai'
ImportError: cannot import name 'AsyncWebCrawler'
```

**Cause:** Missing dependencies or incorrect installation.

**Solution:**
1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run Crawl4AI setup:
```bash
crawl4ai-setup
```

3. If using virtual environment, ensure it's activated:
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

4. Verify installation:
```python
import crawl4ai
print(crawl4ai.__version__)
```

### Issue: Permission Denied Errors
```
PermissionError: [Errno 13] Permission denied: '/path/to/playwright'
```

**Cause:** Insufficient permissions for Playwright browser installation.

**Solution:**
1. Run setup with proper permissions:
```bash
sudo crawl4ai-setup
```

2. Or install Playwright manually:
```bash
pip install playwright
playwright install chromium
```

3. For Docker/Codespaces:
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2
```

## Crawling Problems

### Issue: All Crawls Failing
```
❌ Failed to crawl https://example.com: net::ERR_NAME_NOT_RESOLVED
```

**Cause:** Network connectivity, DNS issues, or invalid URLs.

**Solution:**
1. Test network connectivity:
```bash
ping google.com
curl -I https://example.com
```

2. Verify URLs are valid and accessible:
```python
import requests
response = requests.head("https://example.com")
print(f"Status: {response.status_code}")
```

3. Check for proxy/firewall issues:
```python
# Add proxy configuration if needed
browser_config = BrowserConfig(
    enable_stealth=True,
    extra_args=["--proxy-server=http://proxy:port"]
)
```

4. Try with a simple, known-working URL:
```python
urls = ["https://httpbin.org/html"]  # Simple test page
```

### Issue: Bot Detection / 403 Forbidden
```
❌ Failed to crawl: 403 Forbidden
❌ Detected as bot, access denied
```

**Cause:** Website detecting automated access.

**Solution:**
1. Enable stealth mode:
```python
browser_config = BrowserConfig(
    enable_stealth=True,
    headless=False  # Less detectable
)
```

2. Add realistic delays:
```python
crawler_config = CrawlerRunConfig(
    mean_delay=2.0,      # Longer delays
    max_range=5.0,       # More variation
    simulate_user=True   # Simulate user behavior
)
```

3. Use realistic user agent:
```python
browser_config = BrowserConfig(
    enable_stealth=True,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
)
```

4. Implement session management:
```python
# Reuse browser sessions
async with AsyncWebCrawler(config=browser_config) as crawler:
    for url in urls:
        result = await crawler.arun(url=url)
        await asyncio.sleep(random.uniform(1, 3))  # Random delays
```

### Issue: Timeout Errors
```
TimeoutError: Navigation timeout of 30000ms exceeded
```

**Cause:** Slow-loading pages or network issues.

**Solution:**
1. Increase timeout:
```python
crawler_config = CrawlerRunConfig(
    page_timeout=60000,  # 60 seconds
    cache_mode=CacheMode.BYPASS
)
```

2. Wait for specific elements:
```python
crawler_config = CrawlerRunConfig(
    wait_for="networkidle",  # Wait for network to be idle
    delay_before_return_html=2000  # Wait 2 seconds before returning
)
```

3. Handle timeouts gracefully:
```python
async def safe_crawl(url: str):
    try:
        result = await crawler.arun(url=url, config=crawler_config)
        return result
    except TimeoutError:
        print(f"Timeout for {url}, skipping...")
        return None
```

### Issue: Empty Content Returned
```
✅ URL: https://example.com
📄 Content Length: 0 chars
```

**Cause:** JavaScript-heavy sites, dynamic content, or extraction issues.

**Solution:**
1. Wait for content to load:
```python
crawler_config = CrawlerRunConfig(
    wait_for="domcontentloaded",
    delay_before_return_html=3000,
    remove_overlay_elements=True
)
```

2. Use CSS selectors for specific content:
```python
crawler_config = CrawlerRunConfig(
    css_selector="main, article, .content",  # Target main content
    word_count_threshold=10  # Minimum words
)
```

3. Check if content is in iframe:
```python
crawler_config = CrawlerRunConfig(
    process_iframes=True
)
```

## LLM Analysis Issues

### Issue: OpenAI API Errors
```
❌ LLM Analysis failed: Invalid API key
❌ Rate limit exceeded
```

**Cause:** Invalid API key, insufficient credits, or rate limits.

**Solution:**
1. Verify API key:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

2. Check account balance:
   - Visit [OpenAI Usage Dashboard](https://platform.openai.com/usage)
   - Ensure sufficient credits

3. Implement rate limiting:
```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=50, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        now = datetime.now()
        # Remove old requests
        self.requests = [r for r in self.requests if now - r < timedelta(seconds=self.time_window)]
        
        if len(self.requests) >= self.max_requests:
            wait_time = self.time_window - (now - self.requests[0]).total_seconds()
            await asyncio.sleep(wait_time)
        
        self.requests.append(now)

# Usage
rate_limiter = RateLimiter(max_requests=20, time_window=60)

async def safe_llm_analysis(url: str):
    await rate_limiter.acquire()
    return await crawler.crawl_with_llm_analysis([url])
```

4. Use alternative models:
```python
# Use GPT-3.5 for cost efficiency
llm_config = LLMConfig(
    provider="openai/gpt-3.5-turbo",
    api_token=os.getenv("OPENAI_API_KEY")
)
```

### Issue: LLM Response Format Errors
```
❌ Failed to parse LLM response: Expecting ',' delimiter
❌ Schema validation failed
```

**Cause:** LLM returning invalid JSON or not following schema.

**Solution:**
1. Improve prompt instructions:
```python
llm_strategy = LLMExtractionStrategy(
    llm_config=llm_config,
    schema=PageSummary.model_json_schema(),
    instruction="""
    Extract information from this webpage and return ONLY valid JSON.
    Required format:
    {
        "title": "string - the page title",
        "summary": "string - brief content summary"
    }
    
    Do not include any explanatory text, only the JSON object.
    """,
    extra_args={"temperature": 0}  # Deterministic output
)
```

2. Add fallback handling:
```python
import json
from typing import Dict, Any

def parse_llm_response(response: str) -> Dict[str, Any]:
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != 0:
            try:
                return json.loads(response[start:end])
            except json.JSONDecodeError:
                pass
        
        # Return default structure
        return {
            "title": "Parse Error",
            "summary": "Failed to parse LLM response"
        }
```

3. Validate responses:
```python
def validate_llm_response(data: Dict[str, Any]) -> bool:
    required_fields = ["title", "summary"]
    return all(field in data and isinstance(data[field], str) for field in required_fields)

# Usage
response_data = parse_llm_response(result.extracted_content)
if not validate_llm_response(response_data):
    print("Invalid LLM response, using fallback")
    response_data = {"title": "Unknown", "summary": "Content analysis unavailable"}
```

## Supabase Connection Problems

### Issue: Authentication Failed
```
❌ Could not authenticate with Supabase
❌ Invalid API key
```

**Cause:** Incorrect Supabase URL or API key.

**Solution:**
1. Verify credentials in Supabase dashboard:
   - Go to Settings > API
   - Copy the correct URL and anon key

2. Test connection:
```python
from supabase import create_client

def test_supabase_connection():
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        # Simple test query
        result = supabase.table("pages").select("id").limit(1).execute()
        print("✅ Supabase connection successful")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False
```

3. Check URL format:
```env
# ✅ Correct format
SUPABASE_URL=https://abcdefghijklmnop.supabase.co

# ❌ Wrong - missing https://
SUPABASE_URL=abcdefghijklmnop.supabase.co

# ❌ Wrong - extra characters
SUPABASE_URL=https://abcdefghijklmnop.supabase.co/
```

### Issue: Table Does Not Exist
```
❌ relation "pages" does not exist
❌ Table 'pages' not found
```

**Cause:** Database table not created or wrong table name.

**Solution:**
1. Create the table in Supabase dashboard:
```sql
CREATE TABLE pages (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    content TEXT,
    analysis_header TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

2. Verify table exists:
```python
def check_table_exists():
    try:
        result = supabase.table("pages").select("*").limit(1).execute()
        print("✅ Table 'pages' exists")
        return True
    except Exception as e:
        print(f"❌ Table check failed: {e}")
        return False
```

3. Enable Row Level Security (optional):
```sql
-- Enable RLS
ALTER TABLE pages ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (for development)
CREATE POLICY "Allow all operations" ON pages
FOR ALL TO authenticated
USING (true)
WITH CHECK (true);
```

### Issue: Insert Failures
```
❌ Failed to insert record: duplicate key value violates unique constraint
❌ Permission denied for table pages
```

**Cause:** Duplicate URLs or insufficient permissions.

**Solution:**
1. Handle duplicates with upsert:
```python
def safe_insert_page(record: Dict[str, Any]):
    try:
        # Use upsert to handle duplicates
        result = supabase.table("pages").upsert(
            record,
            on_conflict="url"  # Update if URL already exists
        ).execute()
        return result
    except Exception as e:
        print(f"Insert failed: {e}")
        return None
```

2. Check permissions:
   - Verify your API key has write permissions
   - Check Row Level Security policies
   - Use service role key for admin operations (be careful!)

3. Validate data before insert:
```python
def validate_record(record: Dict[str, Any]) -> bool:
    required_fields = ["url", "content"]
    
    # Check required fields
    if not all(field in record for field in required_fields):
        return False
    
    # Check URL format
    if not record["url"].startswith(("http://", "https://")):
        return False
    
    # Check content length
    if len(record["content"]) == 0:
        return False
    
    return True
```

## Performance Issues

### Issue: Slow Crawling Speed
```
⏱️ Crawling 10 URLs took 120 seconds
🐌 Average: 12 seconds per URL
```

**Cause:** Inefficient configuration, high delays, or resource limitations.

**Solution:**
1. Optimize concurrency:
```python
# Increase semaphore count for more parallel operations
crawler_config = CrawlerRunConfig(
    semaphore_count=10,  # Default is 5
    mean_delay=0.1,      # Reduce delays
    max_range=0.2
)
```

2. Use browser pooling:
```python
class BrowserPool:
    def __init__(self, pool_size=3):
        self.pool = []
        self.pool_size = pool_size
    
    async def get_browser(self):
        if not self.pool:
            browser = AsyncWebCrawler(config=browser_config)
            await browser.astart()
            return browser
        return self.pool.pop()
    
    async def return_browser(self, browser):
        if len(self.pool) < self.pool_size:
            self.pool.append(browser)
        else:
            await browser.aclose()
```

3. Batch operations:
```python
# Process URLs in batches
async def batch_crawl(urls: List[str], batch_size=20):
    results = []
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        batch_results = await crawler.crawl_with_memory_adaptive_dispatcher(batch)
        results.extend(batch_results)
        
        # Small delay between batches
        await asyncio.sleep(1)
    
    return results
```

### Issue: High Memory Usage
```
🧠 Memory usage: 2.5 GB
⚠️ System running low on memory
```

**Cause:** Memory leaks, large content, or too many concurrent operations.

**Solution:**
1. Monitor memory usage:
```python
import psutil
import gc

def monitor_memory():
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.1f} MB")
    
    if memory_mb > 1000:  # 1GB threshold
        print("High memory usage, forcing garbage collection")
        gc.collect()
    
    return memory_mb
```

2. Implement content size limits:
```python
crawler_config = CrawlerRunConfig(
    word_count_threshold=10,
    excluded_tags=["script", "style", "nav", "footer"],
    remove_overlay_elements=True
)
```

3. Process in smaller batches:
```python
async def memory_efficient_crawl(urls: List[str]):
    results = []
    
    for url in urls:
        # Process one at a time to limit memory
        result = await crawler.crawl_single_url(url)
        results.append(result)
        
        # Clear memory periodically
        if len(results) % 10 == 0:
            gc.collect()
            monitor_memory()
    
    return results
```

## Error Codes Reference

### Crawl4AI Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| `net::ERR_NAME_NOT_RESOLVED` | DNS resolution failed | Check internet connection, verify URL |
| `net::ERR_INTERNET_DISCONNECTED` | No internet connection | Check network connectivity |
| `net::ERR_CONNECTION_TIMED_OUT` | Connection timeout | Increase timeout, check firewall |
| `net::ERR_SSL_PROTOCOL_ERROR` | SSL/TLS error | Check certificate, try HTTP instead |

### HTTP Status Codes

| Status | Description | Action |
|--------|-------------|--------|
| 200 | Success | ✅ Process normally |
| 403 | Forbidden | 🔄 Retry with stealth mode |
| 404 | Not Found | ❌ Skip URL |
| 429 | Rate Limited | ⏸️ Wait and retry |
| 500 | Server Error | 🔄 Retry later |
| 503 | Service Unavailable | 🔄 Retry with delay |

### Supabase Error Codes

| Error | Description | Solution |
|-------|-------------|----------|
| `PGRST116` | Schema cache error | Restart Supabase or clear cache |
| `PGRST301` | Row not found | Check query conditions |
| `23505` | Unique constraint violation | Use upsert or handle duplicates |
| `42P01` | Table does not exist | Create table in database |

## Getting Additional Help

### Enable Debug Logging
```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable Crawl4AI debug
os.environ["CRAWL4AI_DEBUG"] = "1"
```

### Collect System Information
```python
import platform
import sys
import crawl4ai

def system_info():
    print("=== SYSTEM INFORMATION ===")
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Crawl4AI: {crawl4ai.__version__}")
    print(f"Memory: {psutil.virtual_memory().total / 1024**3:.1f} GB")
    print(f"CPU: {psutil.cpu_count()} cores")
```

### Create Test Cases
```python
async def run_diagnostics():
    """Run comprehensive diagnostics."""
    print("🔍 Running AsyncWebCrawler Diagnostics...")
    
    # Test 1: Environment
    print("\n1. Environment Check:")
    env_vars = ["SUPABASE_URL", "SUPABASE_KEY", "OPENAI_API_KEY"]
    for var in env_vars:
        value = os.getenv(var)
        status = "✅" if value else "❌"
        print(f"   {status} {var}: {'Set' if value else 'Missing'}")
    
    # Test 2: Network
    print("\n2. Network Check:")
    test_urls = ["https://httpbin.org/get", "https://example.com"]
    for url in test_urls:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    status = "✅" if response.status == 200 else "❌"
                    print(f"   {status} {url}: {response.status}")
        except Exception as e:
            print(f"   ❌ {url}: {str(e)}")
    
    # Test 3: Crawler
    print("\n3. Crawler Check:")
    try:
        crawler = AdvancedWebCrawler()
        result = await crawler.crawl_with_memory_adaptive_dispatcher(["https://httpbin.org/html"])
        status = "✅" if result[0].success else "❌"
        print(f"   {status} Basic crawling: {'Working' if result[0].success else 'Failed'}")
    except Exception as e:
        print(f"   ❌ Basic crawling: {str(e)}")
    
    # Test 4: Database
    print("\n4. Database Check:")
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        result = supabase.table("pages").select("id").limit(1).execute()
        print("   ✅ Supabase connection: Working")
    except Exception as e:
        print(f"   ❌ Supabase connection: {str(e)}")

# Run diagnostics
asyncio.run(run_diagnostics())
```

If you're still experiencing issues after trying these solutions, consider:

1. **Check the project repository** for similar issues
2. **Review the logs** for detailed error messages
3. **Test with minimal configuration** to isolate the problem
4. **Update dependencies** to the latest versions
5. **Contact support** with system information and error logs

This troubleshooting guide covers the most common issues. For specific problems not covered here, enable debug logging and examine the detailed error messages for additional clues.