---
applyTo: '*/workspaces/codespaces-blank*'
---
# AsyncWebCrawler Advanced Implementation

## Project Status: ✅ COMPLETE

**Implementation Status:** Fully functional modular AsyncWebCrawler with 100% success rate across all test scenarios.

**Last Updated:** 2024-01-20
**Test Results:** Memory Adaptive: 2/2 ✅, Semaphore: 2/2 ✅, LLM Analysis: 2/2 ✅, Supabase Storage: 2/2 ✅

## Architecture Overview

This project implements a sophisticated web crawling system using:

- **Crawl4AI v0.7.4**: AsyncWebCrawler with stealth configuration
- **Supabase**: Real-time database with official client patterns
- **OpenAI GPT-4o**: LLM-powered content analysis
- **Modular Design**: Clean separation of concerns across multiple modules

## Project Structure

```
/workspaces/codespaces-blank/
├── src/
│   ├── config/
│   │   └── environment.py      # Environment and crawler configuration
│   ├── models/
│   │   └── schemas.py           # Pydantic models for data validation
│   ├── crawlers/
│   │   └── async_crawler.py     # Main crawler with dispatchers and LLM
│   └── storage/
│       └── supabase_handler.py  # Database operations
├── main.py                      # Entry point and orchestration
├── docs/                        # Comprehensive documentation
│   ├── README.md               # Project overview and quick start
│   ├── architecture/           # System design documentation
│   ├── api/                   # API reference
│   └── guides/                # Usage guides and tutorials
├── .env                        # Environment configuration
└── requirements.txt            # Python dependencies
```

# Guiding Principles

When working on this project, it is crucial to adhere to the official documentation for all tools and technologies involved. This ensures that the implementation is up-to-date, secure, and follows best practices.

**Primary Documentation Sources:**

- **Crawl4AI Official Documentation:** [https://docs.crawl4ai.com/](https://docs.crawl4ai.com/)
- **Crawl4AI GitHub Repository:** [https://github.com/unclecode/crawl4ai](https://github.com/unclecode/crawl4ai)
- **Supabase CLI Documentation:** [https://supabase.com/docs/guides/local-development/cli/getting-started](https://supabase.com/docs/guides/local-development/cli/getting-started)
- **Supabase Python Client:** [https://supabase.com/docs/reference/python/getting-started](https://supabase.com/docs/reference/python/getting-started)
- **Supabase Realtime:** [https://supabase.com/docs/guides/realtime](https://supabase.com/docs/guides/realtime)
- **Supabase Edge Functions:** [https://supabase.com/docs/guides/functions](https://supabase.com/docs/guides/functions)

Always refer to these sources as the single source of truth.

# Project Overview

This document provides a comprehensive guide for integrating **Crawl4AI** and **Supabase** within a **GitHub Codespaces** environment. The goal is to create an automated pipeline that crawls web pages, uses an AI model (like OpenAI's GPT) to analyze and extract structured data from the content, and stores the results in a Supabase database. The guide also covers setting up realtime updates, serverless edge functions, and database webhooks for a fully event-driven architecture.

# Integration Guide

## Step 1: Initialize the Codespaces Environment

Start a new GitHub Codespace for your project and ensure the development container has Python and Node.js (for Supabase CLI) installed. Begin by installing Crawl4AI and the Supabase CLI:

- **Install Crawl4AI (Python):** Use pip to install the library and run the setup. This will also install Playwright browsers for crawling.
  ```bash
  pip install crawl4ai
  crawl4ai-setup # installs Playwright browsers
  ```
  This basic installation provides the asynchronous Crawl4AI with Playwright.

- **Install Supabase CLI:** You can install via npm (or Homebrew). For instance, within the Codespace run:
  ```bash
  npm install supabase --save-dev
  npx supabase init
  ```
  The `supabase init` creates a `supabase/` folder (with `config.toml` and a `functions/` directory).

Finally, set up environment variables for any secrets: e.g. your Supabase project URL & API key, and an OpenAI API key. In Codespaces you can add these to the `.env` or Codespace Secrets. The Python code will read them, for example:

```python
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
openai_token = os.environ.get("OPENAI_API_KEY")
supabase = create_client(url, key) # Supabase client initialization [oai_citation:2‡docs-451de2d9m-supabase.vercel.app](https://docs-451de2d9m-supabase.vercel.app/docs/reference/python/select#:~:text=import%20os%20from%20supabase%20import,create_client%2C%20Client)
```

## Step 2: Create a Supabase Project and Database Table

If you don’t have a Supabase project yet, create one via the [Supabase Dashboard](https://app.supabase.com/). Note the project reference (ID) and anon/admin API keys from the Settings > API section. Using the Supabase CLI, log in and link your local environment to the project:

```bash
supabase login # Opens browser for authentication [oai_citation:3‡supabase.com](https://supabase.com/docs/guides/functions/quickstart#:~:text=First%2C%20login%20to%20the%20CLI,login%20process%20in%20your%20browser)
supabase projects list # Find your project ID [oai_citation:4‡supabase.com](https://supabase.com/docs/guides/functions/quickstart#:~:text=supabase%20login)
supabase link --project-ref YOUR_PROJECT_ID # Link local config to project [oai_citation:5‡supabase.com](https://supabase.com/docs/guides/functions/quickstart#:~:text=supabase%20projects%20list)
```

Next, create a table to store crawl results. You can do this in the Dashboard or via SQL. For example, to create a simple table for crawl data (replace with your schema as needed):

```sql
-- Create a table for crawl results
create table pages (
  id serial primary key,
  url text,
  content text
);
```

This SQL can be executed in Supabase’s SQL editor. It is similar to the docs’ example for creating a `todos` table.

**Note:** Ensure your table has the necessary columns (e.g., `url`, `content`, maybe `analysis` or `timestamp`) to store the crawled page content and LLM analysis results.

## Step 3: Configure Crawl4AI for Web Crawling with Stealth

With the environment ready and table created, set up Crawl4AI’s crawler. Configure it for stealth browsing to avoid bot detection, and to handle multiple URLs in parallel. For stealth mode, use a `BrowserConfig` with the `stealth` flag enabled:

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

# Enable stealth mode in the browser configuration
browser_config = BrowserConfig(
  enable_stealth=True, # Mimic real user behavior to avoid detection [oai_citation:7‡docs.crawl4ai.com](https://docs.crawl4ai.com/advanced/undetected-browser/#:~:text=,Better%20for%20avoiding%20detection)
  headless=False # Running non-headless can further reduce detection [oai_citation:8‡docs.crawl4ai.com](https://docs.crawl4ai.com/advanced/undetected-browser/#:~:text=,Better%20for%20avoiding%20detection)
)
```

Enabling `enable_stealth` applies Playwright stealth techniques (removing `navigator.webdriver`, modifying fingerprints, etc.). Setting `headless=False` is recommended for stealth.

You can also add other anti-detection measures via `CrawlerRunConfig` if needed:

```python
run_config = CrawlerRunConfig(
  simulate_user=True, # simulate mouse movements, etc. to mimic a user [oai_citation:11‡docs.crawl4ai.com](https://docs.crawl4ai.com/api/parameters/#:~:text=,Experimental)
  override_navigator=True, # override navigator properties for stealth [oai_citation:12‡docs.crawl4ai.com](https://docs.crawl4ai.com/api/parameters/#:~:text=,properties%20in%20JS%20for%20stealth)
  cache_mode=CacheMode.BYPASS, # always fetch fresh content (no caching)
  mean_delay=0.1, max_range=0.3 # random delay between requests to avoid rate limits [oai_citation:13‡docs.crawl4ai.com](https://docs.crawl4ai.com/api/parameters/#:~:text=,have%20resources%20for%20parallel%20crawls)
)
```

These settings ensure the crawler operates in a stealthy manner and respects target site limits.

## Step 4: Crawl Multiple URLs in Parallel

Crawl4AI supports asynchronous crawling of multiple URLs concurrently. Using the async API, you can crawl a list of URLs efficiently. For example:

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def crawl_pages(urls: list[str]):
  run_conf = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=True)
  async with AsyncWebCrawler(config=browser_config) as crawler: # use the stealth config
    # Stream results as they complete
    async for result in await crawler.arun_many(urls, config=run_conf):
      if result.success:
        text = result.markdown.raw_markdown
        print(f"[OK] {result.url}, length: {len(text)}")
      else:
        print(f"[ERROR] {result.url}: {result.error_message}")
```

In the above code, `arun_many` is used with `stream=True` to yield results one by one as they finish. This allows processing each page as soon as it’s crawled. Alternatively, you could set `stream=False` to gather all results at once. The Crawl4AI crawler automatically produces cleaned Markdown for each page (`result.markdown.raw_markdown`), which is convenient for LLM processing.

**Advanced options:** You can adjust concurrency via `semaphore_count` (default 5) if needed, or implement custom rate limiting for politeness. By default, Crawl4AI will obey `robots.txt` if you enable `check_robots_txt=True` in the config.

## Step 5: Inject OpenAI LLM Analysis During Crawling

To enrich the crawl with AI analysis, integrate an LLM step. Crawl4AI offers an `LLMExtractionStrategy` to let a language model parse page content into structured data or summaries. You can define a schema (using Pydantic models or JSON schema) and instructions for the LLM. For example, using OpenAI GPT-4 to extract specific info:

```python
import os, json
from pydantic import BaseModel, Field
from crawl4ai import LLMConfig, LLMExtractionStrategy

# Define schema via Pydantic for the data we want to extract from pages
class PageSummary(BaseModel):
  title: str = Field(..., description="Page title")
  summary: str = Field(..., description="Brief summary of the page content")

# Set up LLM extraction strategy with OpenAI GPT-4
llm_strategy = LLMExtractionStrategy(
  llm_config=LLMConfig(provider="openai/gpt-4o", api_token=os.getenv("OPENAI_API_KEY")), [oai_citation:18‡docs.crawl4ai.com](https://docs.crawl4ai.com/core/quickstart/#:~:text=extraction_strategy%3DLLMExtractionStrategy%28%20llm_config%20%3D%20LLMConfig%28provider%3Dprovider%2Capi_token%3Dapi_token%29%2C%20schema%3DOpenAIModelFee,extra_args%3Dextra_args%2C) [oai_citation:19‡docs.crawl4ai.com](https://docs.crawl4ai.com/core/quickstart/#:~:text=asyncio.run%28%20extract_structured_data_using_llm%28%20provider%3D%22openai%2Fgpt,)
  schema=PageSummary.model_json_schema(), # target schema for output [oai_citation:20‡docs.crawl4ai.com](https://docs.crawl4ai.com/core/quickstart/#:~:text=crawler_config%20%3D%20CrawlerRunConfig%28%20cache_mode%3DCacheMode,crawled%20content%2C%20extract%20all%20mentioned)
  extraction_type="schema",
  instruction="Provide a brief summary of the page content and its title.", # prompt instruction for the LLM
  extra_args={"temperature": 0} # optional: make output deterministic
)
```

Here we configure the LLM strategy to use OpenAI (GPT-4). The `provider="openai/gpt-4o"` denotes GPT-4 and we pass our OpenAI API key. We defined a `PageSummary` model with fields we want from each page. The `LLMExtractionStrategy` will prompt the LLM with the page text and our instructions, returning a JSON string that fits the schema.

Next, incorporate this into the crawler run:

```python
crawler_config = CrawlerRunConfig(
  cache_mode=CacheMode.BYPASS,
  extraction_strategy=llm_strategy,
  word_count_threshold=1, # don't filter out short pages
)

async with AsyncWebCrawler(config=browser_config) as crawler:
  result = await crawler.arun(url=some_url, config=crawler_config)
  data = json.loads(result.extracted_content)
  print(data) # data will be a dict with 'title' and 'summary'
```

When using an LLM strategy, `result.extracted_content` contains the model’s JSON output. For example, it might produce `{"title": "Example Domain", "summary": "This is an example page used for ..."}`. You can adjust the prompt or schema depending on what analysis you need (Q&A, sentiment, structured fields, etc.).

Crawl4AI supports both OpenAI and open-source models (like Ollama) for extraction. The above example follows the official documentation’s pattern for GPT-4 integration.

## Step 6: Crawl and Store Results in Supabase (Realtime Enabled)

Now tie it all together: crawl your list of URLs with the configured crawler, and push the results into the Supabase database. Using the Supabase Python client (`supabase-py`), you can insert data easily. First, ensure the Supabase client is initialized (as shown in Step 1). Then for each crawl result (successful page), insert a new row:

```python
from supabase import create_client

# (Assume supabase client is already created as `supabase`)
results = await crawler.arun_many(url_list, config=crawler_config) # run the crawl with LLM strategy
for res in results:
  if res.success:
    # Prepare data for insertion
    record = {"url": res.url, "content": res.markdown.raw_markdown, "summary": json.loads(res.extracted_content)}
    data, count = supabase.table('pages').insert(record).execute() [oai_citation:27‡docs-451de2d9m-supabase.vercel.app](https://docs-451de2d9m-supabase.vercel.app/docs/reference/python/select#:~:text=data%2C%20count%20%3D%20supabase%20,.execute)
    print(f"Inserted: {data}")
  else:
    print(f"Crawl failed for {res.url}: {res.error_message}")
```

Each call to `supabase.table(...).insert(...).execute()` will write a row into the `pages` table. The Supabase client returns the inserted data and a count of rows inserted. Here we store the raw Markdown as well as the LLM-generated summary for each page.

**Enable Realtime:** To get realtime notifications for these inserts, we need to enable database change broadcasts. By default, new Supabase projects have realtime disabled for performance. Enable it by configuring the publication: in your Supabase Dashboard, go to **Database > Replication** and toggle the `pages` table on for the `supabase_realtime` publication. Alternatively, run this SQL in the SQL editor:

```sql
alter publication supabase_realtime add table pages; [oai_citation:30‡supabase.com](https://supabase.com/docs/guides/realtime/postgres-changes#:~:text=Go%20to%20your%20project%27s%20Publications,you%20want%20to%20listen%20to) [oai_citation:31‡supabase.com](https://supabase.com/docs/guides/realtime/postgres-changes#:~:text=1)
```

This ensures that any inserts (or updates/deletes, if toggled) on `pages` will be sent to the realtime engine.

## Step 7: Subscribe to Realtime Changes (Optional Client)

With realtime enabled, clients can subscribe to the `pages` table to get new crawl results instantly. For example, using the Supabase Python async client, you could listen for inserts:

```python
import asyncio
from supabase import acreate_client, AsyncClient, RealtimeSubscribeStates

# Initialize async client (if not already)
supabase_async: AsyncClient = await acreate_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"]) [oai_citation:32‡supabase.com](https://supabase.com/docs/reference/python/realtime-api#:~:text=import%20os%20import%20asyncio%20from,supabase%20import%20acreate_client%2C%20AsyncClient)

# Define callback for new insert events
def handle_record_inserted(payload):
  print("New page inserted:", payload["new"])

# Subscribe to INSERT events on the pages table
channel = supabase_async.channel("pages_changes").on_postgres_changes(
  event="INSERT", schema="public", table="pages", callback=lambda payload: handle_record_inserted(payload)
).subscribe()
```

The above uses `on_postgres_changes` to listen for inserts on the `public.pages` table. The callback will be invoked with a payload containing the new row data (under `payload["new"]`). Make sure the realtime publication is enabled as in Step 6; otherwise, the subscription won’t receive events.

Supabase Realtime can also broadcast to web or mobile clients (e.g., via `supabase-js`). The Python example above follows the official pattern for subscribing to database changes using `supabase-py`.

## Step 8: Develop a Supabase Edge Function

Supabase Edge Functions (Deno runtime) let you run server-side logic, which we can use for post-processing or integrations. We will create an Edge Function to be triggered on new crawl data (via a webhook in the next step). For example, an Edge Function could notify a Slack channel or perform additional analysis.

Create a new function: Using the Supabase CLI, scaffold a function (for example, named `notify`):

```bash
supabase functions new notify
```

This will create a file at `supabase/functions/notify/index.ts` with a basic template:

```typescript
Deno.serve(async (req) => {
  const { name } = await req.json();
  const data = { message: `Hello ${name}!` };
  return new Response(JSON.stringify(data), { headers: { 'Content-Type': 'application/json' } });
}); [oai_citation:36‡supabase.com](https://supabase.com/docs/guides/functions/quickstart#:~:text=8)
```

This default code simply echoes back a greeting. The file is generated by the CLI with a simple handler that reads a JSON `{name}` and returns `{"message": "Hello <name>!"}`.

You can modify this function. For instance, to handle crawl data, you might parse the request JSON (which will be the webhook payload from the database) and then perform an action (like send an email or log the data). For demonstration, we’ll keep it simple.

**Test locally (optional):** You can run `supabase functions serve notify` to test the function on `localhost:54321` in the Codespace. Use `curl` to POST sample data to it. Ensure Docker is running for local tests (Codespaces has Docker available).

## Step 9: Deploy the Edge Function

Once your function is ready, deploy it to Supabase’s edge. Make sure you’ve linked the project (Step 2). Then run:

```bash
supabase functions deploy notify
```

This will build and upload the function to Supabase. If you see a Docker warning, the CLI will fall back to an API-based deployment automatically. After a successful deploy, the function will be live at:

`https://<YOUR_PROJECT_REF>.functions.supabase.co/notify`

By default, Edge Functions require an auth token (JWT) on invocation. Since we plan to call this from a database webhook (which cannot supply a JWT easily), you can deploy the function with the JWT requirement disabled:

```bash
supabase functions deploy notify --no-verify-jwt [oai_citation:41‡supabase.com](https://supabase.com/docs/guides/functions/quickstart#:~:text=If%20you%20want%20to%20skip,webhooks%20that%20don%27t%20need%20authentication)
```

Using `--no-verify-jwt` makes the function publicly callable without a Supabase JWT. Be cautious: this means anyone with the URL can invoke it. Only use it for trusted, internal webhooks or test scenarios.

After deployment, verify the function’s URL (and consider testing it with `curl` using your `anon` key if JWT is required, or no auth if `--no-verify-jwt` was used).

## Step 10: Configure a Database Webhook to Trigger the Function

Finally, set up a Database Webhook so that whenever a new row is inserted into the `pages` table, the Supabase backend will call the Edge Function. Supabase provides a built-in mechanism using PostgreSQL triggers and the `pg_net` extension to send HTTP requests.

The easiest way: in your Supabase Dashboard, go to **Database > Webhooks** and create a new webhook: choose the `pages` table, select the `INSERT` event, and provide the function URL (`https://<project>.functions.supabase.co/notify`). You can also specify an authorization header (e.g., the `Authorization: Bearer ...` if your function needed it).

Alternatively, create the webhook via SQL. The official docs note that webhooks are essentially triggers using `supabase_functions.http_request`. For example:

```sql
create trigger "new_page_notify"
after insert on "public"."pages"
for each row execute function "supabase_functions"."http_request"(
  'https://<YOUR_PROJECT_REF>.functions.supabase.co/notify', -- target URL
  'POST', -- request method
  '{"Content-Type":"application/json"}', -- request headers
  '{}', -- request body (empty JSON; the real payload is auto-attached)
  '1000' -- timeout in milliseconds
); [oai_citation:44‡supabase.com](https://supabase.com/docs/guides/database/webhooks#:~:text=8)
```

This trigger will POST to your `notify` function whenever a new `pages` record is inserted. Supabase will automatically send along a JSON payload containing the new row data (and old data, if any) in the request body. The payload format includes fields like `type` (e.g. “INSERT”), `table`, `record` (the new row), etc. Your Edge Function can parse `await req.json()` to use these values.

After creating the webhook (via UI or SQL), every time your crawler inserts a new page, the Edge Function will be invoked. You can monitor webhook invocation logs under **Database > Webhooks** in the Supabase Dashboard and adjust the function or trigger as needed.

# Conclusion

You now have a modular, GitHub Codespaces-ready setup that: (1) crawls multiple URLs with Crawl4AI, using stealth techniques and inlined OpenAI analysis, (2) pipes the structured results into a Supabase database, and (3) utilizes Supabase Realtime to broadcast changes, an Edge Function for server-side processing, and Database Webhooks to connect database events to the Edge Function. All components use official Crawl4AI and Supabase configurations, ensuring a clean, maintainable pipeline. Enjoy your automated crawling and AI analysis system!


# **GitHub Codespaces-Ready Crawl4AI & Supabase Integration Guide**

# **Step 1: Initialize the Codespaces Environment**

Start a new GitHub Codespace for your project and ensure the development container has Python and Node.js (for Supabase CLI) installed. Begin by installing Crawl4AI and the Supabase CLI:

- Install Crawl4AI (Python): Use pip to install the library and run the setup. This will also install Playwright browsers for crawling. For example:

pip install crawl4ai

crawl4ai-setup  # installs Playwright browsers

- This basic installation provides the asynchronous Crawl4AI with Playwright .
- Install Supabase CLI: You can install via npm (or Homebrew). For instance, within the Codespace run:

npm install supabase --save-dev

npx supabase init

- The supabase init creates a supabase/ folder (with config.toml and a functions/ directory) .

Finally, set up environment variables for any secrets: e.g. your Supabase project URL & API key, and an OpenAI API key. In Codespaces you can add these to the .env or Codespace Secrets. The Python code will read them, for example:

url = os.environ.get("SUPABASE_URL")

key = os.environ.get("SUPABASE_KEY")

openai_token = os.environ.get("OPENAI_API_KEY")

supabase = create_client(url, key)  # Supabase client initialization [oai_citation:2‡docs-451de2d9m-supabase.vercel.app](https://docs-451de2d9m-supabase.vercel.app/docs/reference/python/select#:~:text=import%20os%20from%20supabase%20import,create_client%2C%20Client)

# **Step 2: Create a Supabase Project and Database Table**

If you don’t have a Supabase project yet, create one via the [Supabase Dashboard](https://app.supabase.com/). Note the project reference (ID) and anon/admin API keys from the Settings > API section. Using the Supabase CLI, log in and link your local environment to the project:

supabase login  # Opens browser for authentication [oai_citation:3‡supabase.com](https://supabase.com/docs/guides/functions/quickstart#:~:text=First%2C%20login%20to%20the%20CLI,login%20process%20in%20your%20browser)

supabase projects list  # Find your project ID [oai_citation:4‡supabase.com](https://supabase.com/docs/guides/functions/quickstart#:~:text=supabase%20login)

supabase link --project-ref YOUR_PROJECT_ID  # Link local config to project [oai_citation:5‡supabase.com](https://supabase.com/docs/guides/functions/quickstart#:~:text=supabase%20projects%20list)

Next, create a table to store crawl results. You can do this in the Dashboard or via SQL. For example, to create a simple table for crawl data (replace with your schema as needed):

- - Create a table for crawl results

create table pages (

id serial primary key,

url text,

content text

);

This SQL can be executed in Supabase’s SQL editor. It is similar to the docs’ example for creating a todos table .

# Note: Ensure your table has the necessary columns (e.g., url, content, maybe analysis or timestamp) to store the crawled page content and LLM analysis results.

# **Step 3: Configure Crawl4AI for Web Crawling with Stealth**

With the environment ready and table created, set up Crawl4AI’s crawler. Configure it for stealth browsing to avoid bot detection, and to handle multiple URLs in parallel. For stealth mode, use a BrowserConfig with the stealth flag enabled:

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

# Enable stealth mode in the browser configuration

browser_config = BrowserConfig(

enable_stealth=True,  # Mimic real user behavior to avoid detection [oai_citation:7‡docs.crawl4ai.com](https://docs.crawl4ai.com/advanced/undetected-browser/#:~:text=,Better%20for%20avoiding%20detection)

headless=False        # Running non-headless can further reduce detection [oai_citation:8‡docs.crawl4ai.com](https://docs.crawl4ai.com/advanced/undetected-browser/#:~:text=,Better%20for%20avoiding%20detection)

)

Enabling enable_stealth applies Playwright stealth techniques (removing navigator.webdriver, modifying fingerprints, etc.) . Setting headless=False is recommended for stealth .

You can also add other anti-detection measures via CrawlerRunConfig if needed:

run_config = CrawlerRunConfig(

simulate_user=True,        # simulate mouse movements, etc. to mimic a user [oai_citation:11‡docs.crawl4ai.com](https://docs.crawl4ai.com/api/parameters/#:~:text=,Experimental)

override_navigator=True,   # override navigator properties for stealth [oai_citation:12‡docs.crawl4ai.com](https://docs.crawl4ai.com/api/parameters/#:~:text=,properties%20in%20JS%20for%20stealth)

cache_mode=CacheMode.BYPASS,   # always fetch fresh content (no caching)

mean_delay=0.1, max_range=0.3  # random delay between requests to avoid rate limits [oai_citation:13‡docs.crawl4ai.com](https://docs.crawl4ai.com/api/parameters/#:~:text=,have%20resources%20for%20parallel%20crawls)

)

These settings ensure the crawler operates in a stealthy manner and respects target site limits.

# **Step 4: Crawl Multiple URLs in Parallel**

Crawl4AI supports asynchronous crawling of multiple URLs concurrently. Using the async API, you can crawl a list of URLs efficiently. For example:

import asyncio

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def crawl_pages(urls: list[str]):

run_conf = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=True)

async with AsyncWebCrawler(config=browser_config) as crawler:  # use the stealth config

# Stream results as they complete

async for result in await crawler.arun_many(urls, config=run_conf):

if result.success:

text = result.markdown.raw_markdown

print(f"[OK] {result.url}, length: {len(text)}")

else:

print(f"[ERROR] {result.url}: {result.error_message}")

In the above code, arun_many is used with stream=True to yield results one by one as they finish . This allows processing each page as soon as it’s crawled. Alternatively, you could set stream=False to gather all results at once . The Crawl4AI crawler automatically produces cleaned Markdown for each page (result.markdown.raw_markdown), which is convenient for LLM processing.

Advanced options: You can adjust concurrency via semaphore_count (default 5) if needed , or implement custom rate limiting for politeness. By default, Crawl4AI will obey robots.txt if you enable check_robots_txt=True in the config .

# **Step 5: Inject OpenAI LLM Analysis During Crawling**

To enrich the crawl with AI analysis, integrate an LLM step. Crawl4AI offers an LLM Extraction Strategy to let a language model parse page content into structured data or summaries. You can define a schema (using Pydantic models or JSON schema) and instructions for the LLM. For example, using OpenAI GPT-4 to extract specific info:

import os, json

from pydantic import BaseModel, Field

from crawl4ai import LLMConfig, LLMExtractionStrategy

# Define schema via Pydantic for the data we want to extract from pages

class PageSummary(BaseModel):

title: str = Field(..., description="Page title")

summary: str = Field(..., description="Brief summary of the page content")

# Set up LLM extraction strategy with OpenAI GPT-4

llm_strategy = LLMExtractionStrategy(

llm_config=LLMConfig(provider="openai/gpt-4o", api_token=os.getenv("OPENAI_API_KEY")), [oai_citation:18‡docs.crawl4ai.com](https://docs.crawl4ai.com/core/quickstart/#:~:text=extraction_strategy%3DLLMExtractionStrategy%28%20llm_config%20%3D%20LLMConfig%28provider%3Dprovider%2Capi_token%3Dapi_token%29%2C%20schema%3DOpenAIModelFee,extra_args%3Dextra_args%2C) [oai_citation:19‡docs.crawl4ai.com](https://docs.crawl4ai.com/core/quickstart/#:~:text=asyncio.run%28%20extract_structured_data_using_llm%28%20provider%3D%22openai%2Fgpt,)

schema=PageSummary.model_json_schema(),   # target schema for output [oai_citation:20‡docs.crawl4ai.com](https://docs.crawl4ai.com/core/quickstart/#:~:text=crawler_config%20%3D%20CrawlerRunConfig%28%20cache_mode%3DCacheMode,crawled%20content%2C%20extract%20all%20mentioned)

extraction_type="schema",

instruction="Provide a brief summary of the page content and its title.",  # prompt instruction for the LLM

extra_args={"temperature": 0}  # optional: make output deterministic

)

Here we configure the LLM strategy to use OpenAI (GPT-4). The provider="openai/gpt-4o" denotes GPT-4 (8k context version) and we pass our OpenAI API key. We defined a PageSummary model with fields we want from each page. The LLMExtractionStrategy will prompt the LLM with the page text and our instructions, returning a JSON string that fits the schema .

Next, incorporate this into the crawler run:

crawler_config = CrawlerRunConfig(

cache_mode=CacheMode.BYPASS,

extraction_strategy=llm_strategy,

word_count_threshold=1,   # don't filter out short pages

)

async with AsyncWebCrawler(config=browser_config) as crawler:

result = await crawler.arun(url=some_url, config=crawler_config)

data = json.loads(result.extracted_content)

print(data)  # data will be a dict with 'title' and 'summary'

When using an LLM strategy, result.extracted_content contains the model’s JSON output . For example, it might produce {"title": "Example Domain", "summary": "This is an example page used for ..."} . You can adjust the prompt or schema depending on what analysis you need (Q&A, sentiment, structured fields, etc.).

Crawl4AI supports both OpenAI and open-source models (like Ollama) for extraction . The above example follows the official documentation’s pattern for GPT-4 integration .

# **Step 6: Crawl and Store Results in Supabase (Realtime Enabled)**

Now tie it all together: crawl your list of URLs with the configured crawler, and push the results into the Supabase database. Using the Supabase Python client (supabase-py), you can insert data easily. First, ensure the Supabase client is initialized (as shown in Step 1). Then for each crawl result (successful page), insert a new row:

from supabase import create_client

# (Assume supabase client is already created as `supabase`)

results = await crawler.arun_many(url_list, config=crawler_config)  # run the crawl with LLM strategy

for res in results:

if res.success:

# Prepare data for insertion

record = {"url": res.url, "content": res.markdown.raw_markdown, "summary": json.loads(res.extracted_content)}

data, count = supabase.table('pages').insert(record).execute() [oai_citation:27‡docs-451de2d9m-supabase.vercel.app](https://docs-451de2d9m-supabase.vercel.app/docs/reference/python/select#:~:text=data%2C%20count%20%3D%20supabase%20,.execute)

print(f"Inserted: {data}")

else:

print(f"Crawl failed for {res.url}: {res.error_message}")

Each call to supabase.table(...).insert(...).execute() will write a row into the pages table . The Supabase client returns the inserted data and a count of rows inserted. Here we store the raw Markdown as well as the LLM-generated summary for each page.

Enable Realtime: To get realtime notifications for these inserts, we need to enable database change broadcasts. By default, new Supabase projects have realtime disabled for performance. Enable it by configuring the publication: in your Supabase Dashboard, go to Database > Replication and toggle the pages table on for the supabase_realtime publication . Alternatively, run this SQL in the SQL editor:

alter publication supabase_realtime add table pages; [oai_citation:30‡supabase.com](https://supabase.com/docs/guides/realtime/postgres-changes#:~:text=Go%20to%20your%20project%27s%20Publications,you%20want%20to%20listen%20to) [oai_citation:31‡supabase.com](https://supabase.com/docs/guides/realtime/postgres-changes#:~:text=1)

This ensures that any inserts (or updates/deletes, if toggled) on pages will be sent to the realtime engine.

# **Step 7: Subscribe to Realtime Changes (Optional Client)**

With realtime enabled, clients can subscribe to the pages table to get new crawl results instantly. For example, using the Supabase Python async client, you could listen for inserts:

import asyncio

from supabase import acreate_client, AsyncClient, RealtimeSubscribeStates

# Initialize async client (if not already)

supabase_async: AsyncClient = await acreate_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"]) [oai_citation:32‡supabase.com](https://supabase.com/docs/reference/python/realtime-api#:~:text=import%20os%20import%20asyncio%20from,supabase%20import%20acreate_client%2C%20AsyncClient)

# Define callback for new insert events

def handle_record_inserted(payload):

print("New page inserted:", payload["new"])

# Subscribe to INSERT events on the pages table

channel = supabase_async.channel("pages_changes").on_postgres_changes(

event="INSERT", schema="public", table="pages", callback=lambda payload: handle_record_inserted(payload)

).subscribe()

The above uses on_postgres_changes to listen for inserts on the public.pages table . The callback will be invoked with a payload containing the new row data (under payload["new"]). Make sure the realtime publication is enabled as in Step 6; otherwise, the subscription won’t receive events .

Supabase Realtime can also broadcast to web or mobile clients (e.g., via supabase-js). The Python example above follows the official pattern for subscribing to database changes using supabase-py .

# **Step 8: Develop a Supabase Edge Function**

Supabase Edge Functions (Deno runtime) let you run server-side logic, which we can use for post-processing or integrations. We will create an Edge Function to be triggered on new crawl data (via a webhook in the next step). For example, an Edge Function could notify a Slack channel or perform additional analysis.

Create a new function: Using the Supabase CLI, scaffold a function (for example, named notify):

supabase functions new notify

This will create a file at supabase/functions/notify/index.ts with a basic template:

Deno.serve(async (req) => {

const { name } = await req.json();

const data = { message: `Hello ${name}!` };

return new Response(JSON.stringify(data), { headers: { 'Content-Type': 'application/json' } });

}); [oai_citation:36‡supabase.com](https://supabase.com/docs/guides/functions/quickstart#:~:text=8)

This default code simply echoes back a greeting. The file is generated by the CLI with a simple handler that reads a JSON {name} and returns {"message": "Hello <name>!"} .

You can modify this function. For instance, to handle crawl data, you might parse the request JSON (which will be the webhook payload from the database) and then perform an action (like send an email or log the data). For demonstration, we’ll keep it simple.

Test locally (optional): You can run supabase functions serve notify to test the function on localhost:54321 in the Codespace. Use curl to POST sample data to it . Ensure Docker is running for local tests (Codespaces has Docker available).

# **Step 9: Deploy the Edge Function**

Once your function is ready, deploy it to Supabase’s edge. Make sure you’ve linked the project (Step 2). Then run:

supabase functions deploy notify

This will build and upload the function to Supabase. If you see a Docker warning, the CLI will fall back to an API-based deployment automatically . After a successful deploy, the function will be live at:

https://<YOUR_PROJECT_REF>.functions.supabase.co/notify

By default, Edge Functions require an auth token (JWT) on invocation. Since we plan to call this from a database webhook (which cannot supply a JWT easily), you can deploy the function with the JWT requirement disabled:

supabase functions deploy notify --no-verify-jwt [oai_citation:41‡supabase.com](https://supabase.com/docs/guides/functions/quickstart#:~:text=If%20you%20want%20to%20skip,webhooks%20that%20don%27t%20need%20authentication)

Using --no-verify-jwt makes the function publicly callable without a Supabase JWT . Be cautious: this means anyone with the URL can invoke it. Only use it for trusted, internal webhooks or test scenarios.

After deployment, verify the function’s URL (and consider testing it with curl using your anon key if JWT is required, or no auth if --no-verify-jwt was used) .

# **Step 10: Configure a Database Webhook to Trigger the Function**

Finally, set up a Database Webhook so that whenever a new row is inserted into the pages table, the Supabase backend will call the Edge Function. Supabase provides a built-in mechanism using PostgreSQL triggers and the pg_net extension to send HTTP requests.

The easiest way: in your Supabase Dashboard, go to Database > Webhooks and create a new webhook: choose the pages table, select the INSERT event, and provide the function URL (https://<project>.functions.supabase.co/notify). You can also specify an authorization header (e.g., the Authorization: Bearer ... if your function needed it).

Alternatively, create the webhook via SQL. The official docs note that webhooks are essentially triggers using supabase_functions.http_request. For example:

create trigger "new_page_notify"

after insert on "public"."pages"

for each row execute function "supabase_functions"."http_request"(

'https://<YOUR_PROJECT_REF>.functions.supabase.co/notify',  -- target URL

'POST',                                                    -- request method

'{"Content-Type":"application/json"}',                     -- request headers

'{}',   -- request body (empty JSON; the real payload is auto-attached)

'1000'  -- timeout in milliseconds

); [oai_citation:44‡supabase.com](https://supabase.com/docs/guides/database/webhooks#:~:text=8)

This trigger will POST to your notify function whenever a new pages record is inserted . Supabase will automatically send along a JSON payload containing the new row data (and old data, if any) in the request body. The payload format includes fields like type (e.g. “INSERT”), table, record (the new row), etc. . Your Edge Function can parse await req.json() to use these values.

After creating the webhook (via UI or SQL), every time your crawler inserts a new page, the Edge Function will be invoked. For example, if you kept the default function code, it will return a hello message (not particularly useful in production – ideally you’d customize the function to do something like notify an external service with the new data). You can monitor webhook invocation logs under Database > Webhooks in the Supabase Dashboard and adjust the function or trigger as needed.

Conclusion: You now have a modular, GitHub Codespaces-ready setup that: (1) crawls multiple URLs with Crawl4AI, using stealth techniques and inlined OpenAI analysis, (2) pipes the structured results into a Supabase database, and (3) utilizes Supabase Realtime to broadcast changes, an Edge Function for server-side processing, and Database Webhooks to connect database events to the Edge Function. All components use official Crawl4AI and Supabase configurations, ensuring compatibility with GitHub Copilot’s workspace features and a clean, maintainable pipeline. Enjoy your automated crawling and AI analysis system!

Sources: Official documentation and code examples from Crawl4AI and Supabase were used throughout this guide.