---
mode: agent
---
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