# Quick Start Guide

Get up and running with Supa-Crawl in under 10 minutes. This guide walks you through the complete setup process from installation to your first successful crawl with LLM analysis.

## Prerequisites

Before starting, ensure you have:

- **Python 3.12+** installed
- **Git** for repository management
- **OpenAI API key** ([Get one here](https://platform.openai.com/api-keys))
- **Supabase account** ([Sign up here](https://supabase.com))

## Step 1: Repository Setup

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/Gaya56/supa-crawl.git
cd supa-crawl

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install browser dependencies for Playwright
playwright install
sudo playwright install-deps  # Linux/macOS only
```

### Verify Installation

```bash
# Test basic imports
python -c "
import crawl4ai
import openai
import supabase
print('✅ All dependencies installed successfully!')
"
```

## Step 2: Environment Configuration

### Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit the .env file with your credentials
nano .env  # or use your preferred editor
```

### Configure API Keys

Add your credentials to `.env`:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# Optional: Advanced settings
CRAWL4AI_VERBOSE=false
CRAWL4AI_CACHE_MODE=bypass
```

### Get Your Supabase Credentials

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project or select existing one
3. Go to **Settings** → **API**
4. Copy your **Project URL** and **anon/public key**

## Step 3: Database Setup

### Create the Pages Table

In your Supabase SQL Editor, run:

```sql
-- Create the main pages table
CREATE TABLE pages (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url TEXT NOT NULL,
    title TEXT,           -- AI-generated title
    summary TEXT,         -- AI-generated summary
    content TEXT          -- Raw markdown content
);

-- Create performance indexes
CREATE INDEX idx_pages_url ON pages(url);
CREATE INDEX idx_pages_title ON pages(title);

-- Optional: Add Row Level Security (RLS)
ALTER TABLE pages ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users
CREATE POLICY "Users can insert pages" ON pages
FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can select pages" ON pages
FOR SELECT USING (true);
```

### Verify Database Connection

```bash
# Test database connectivity
python -c "
from src.storage.supabase_handler import SupabaseHandler
handler = SupabaseHandler()
if handler.is_available:
    print('✅ Database connection successful!')
else:
    print('❌ Database connection failed. Check your credentials.')
"
```

## Step 4: First Crawl Test

### Basic Crawling Test

Create a test file `test_crawl.py`:

```python
import asyncio
from src.crawlers.async_crawler import AdvancedWebCrawler

async def test_basic_crawl():
    """Test basic crawling functionality"""
    print("🧪 Testing basic crawling...")
    
    crawler = AdvancedWebCrawler()
    urls = ["https://example.com"]
    
    # Test simple crawling
    results = await crawler.crawl_with_memory_adaptive_dispatcher(urls)
    
    if results:
        print(f"✅ Basic crawl successful! Retrieved {len(results)} pages")
        print(f"📄 Content preview: {results[0]['raw_markdown'][:100]}...")
    else:
        print("❌ Basic crawl failed")

# Run the test
asyncio.run(test_basic_crawl())
```

```bash
# Run the test
python test_crawl.py
```

### LLM Analysis Test

Create `test_llm.py`:

```python
import asyncio
from src.crawlers.async_crawler import AdvancedWebCrawler

async def test_llm_analysis():
    """Test LLM-powered content analysis"""
    print("🧠 Testing LLM analysis...")
    
    crawler = AdvancedWebCrawler()
    urls = ["https://example.com"]
    
    # Test LLM extraction
    results = await crawler.crawl_with_llm_analysis(urls)
    
    if results and results[0].get('analysis'):
        analysis = results[0]['analysis'][0]
        print("✅ LLM analysis successful!")
        print(f"📝 Title: {analysis['title']}")
        print(f"📄 Summary: {analysis['summary']}")
    else:
        print("❌ LLM analysis failed")

# Run the test
asyncio.run(test_llm_analysis())
```

```bash
# Run the test
python test_llm.py
```

## Step 5: Complete Pipeline Test

### Full Integration Test

```python
import asyncio
from src.crawlers.async_crawler import AdvancedWebCrawler

async def test_full_pipeline():
    """Test complete crawl → analyze → store pipeline"""
    print("🚀 Testing complete pipeline...")
    
    crawler = AdvancedWebCrawler()
    urls = [
        "https://example.com",
        "https://docs.crawl4ai.com/"
    ]
    
    # Run complete pipeline
    success = await crawler.crawl_and_store_in_supabase(urls)
    
    if success:
        print("✅ Complete pipeline successful!")
        print("📊 Check your Supabase dashboard to see the stored data")
    else:
        print("❌ Pipeline failed - check logs for details")

# Run the test
asyncio.run(test_full_pipeline())
```

### Verify Stored Data

Check your Supabase dashboard or run:

```python
from src.storage.supabase_handler import SupabaseHandler

handler = SupabaseHandler()
response = handler.client.table('pages').select('url, title, summary').limit(5).execute()

print("📊 Recent crawl results:")
for row in response.data:
    print(f"🔗 {row['url']}")
    print(f"   📝 {row['title']}")
    print(f"   📄 {row['summary'][:100]}...")
    print()
```

## Step 6: Run the Main Demo

### Execute Complete Demo

```bash
# Run the comprehensive demo
python main.py
```

Expected output:
```
🌐 AsyncWebCrawler Advanced Implementation
============================================================
Following official documentation:
- Crawl4AI: https://docs.crawl4ai.com/
- Supabase: https://supabase.com/docs
============================================================

🎯 Target URLs (3):
  1. https://docs.crawl4ai.com/api/parameters/
  2. https://docs.crawl4ai.com/
  3. https://example.com

1️⃣ Testing Memory Adaptive Dispatcher...
   Results: 2 successful crawls

2️⃣ Testing Semaphore Dispatcher...
   Results: 2 successful crawls

3️⃣ Testing LLM Analysis...
   Results: 2 analyzed crawls

4️⃣ Testing Full Pipeline with Supabase...
   Storage success: True

🎉 All tests completed successfully!
```

## Common Issues & Solutions

### Issue 1: Import Errors

```bash
# Error: ModuleNotFoundError
# Solution: Ensure virtual environment is activated
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### Issue 2: Browser Dependencies

```bash
# Error: Browser executable not found
# Solution: Install Playwright browsers
playwright install
sudo playwright install-deps  # Linux/macOS
```

### Issue 3: OpenAI API Errors

```bash
# Error: Invalid API key
# Solution: Verify your OpenAI API key
python -c "
import openai
import os
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('✅ OpenAI API key valid')
"
```

### Issue 4: Supabase Connection

```bash
# Error: Failed to connect to Supabase
# Solution: Check URL and key format
# URL should be: https://project-id.supabase.co
# Key should be: eyJ... (starts with eyJ)
```

## Next Steps

Now that you have Supa-Crawl running:

1. **Explore Advanced Features**: Check out [Advanced Usage Guide](advanced-usage.md)
2. **Customize Extraction**: Modify the LLM prompts in `src/models/schemas.py`
3. **Scale Your Operations**: Learn about batch processing and optimization
4. **Monitor Performance**: Set up logging and monitoring
5. **Build Applications**: Use the API to build custom crawling solutions

## Quick Reference

### Essential Commands

```bash
# Start crawling
python main.py

# Run tests
python -m pytest tests/ -v

# Check system status
python -c "from src.config.environment import env_config; env_config.validate()"

# View recent results
python -c "
from src.storage.supabase_handler import SupabaseHandler
h = SupabaseHandler()
data = h.client.table('pages').select('*').limit(3).execute()
print(data.data)
"
```

### Key Files

- `main.py` - Complete demo and testing
- `src/crawlers/async_crawler.py` - Core crawling logic
- `src/models/schemas.py` - Data models and LLM schemas
- `src/storage/supabase_handler.py` - Database operations
- `.env` - Environment configuration

### Documentation

- [API Reference](../api/reference.md) - Complete method documentation
- [Architecture Overview](../architecture/overview.md) - System design
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

**🎉 Congratulations! You now have a fully functional AI-powered web crawling pipeline.**