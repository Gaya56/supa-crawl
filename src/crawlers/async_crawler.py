#!/usr/bin/env python3
"""
AsyncWebCrawler Implementation with Advanced Features
Following official documentation from:
- Crawl4AI: https://docs.crawl4ai.com/core/quickstart/
- Multi-URL: https://docs.crawl4ai.com/advanced/multi-url-crawling/
- LLM Integration: https://docs.crawl4ai.com/core/quickstart/#llm-extraction
"""
import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any

# Official Crawl4AI imports - Source: https://docs.crawl4ai.com/
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai import LLMConfig, LLMExtractionStrategy
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher, SemaphoreDispatcher
from crawl4ai import CrawlerMonitor, RateLimiter

from ..config.environment import env_config, crawler_config
from ..models.schemas import PageSummary, PredictionMarketBet
from ..storage.supabase_handler import SupabaseHandler


class AdvancedWebCrawler:
    """
    Advanced AsyncWebCrawler with stealth, multi-URL support, and integrations
    Based on official Crawl4AI documentation: https://docs.crawl4ai.com/
    Extracted from working asyncwebcrawler_advanced.py
    """
    
    def __init__(self):
        # Configure browser for stealth mode using official pattern
        # Source: https://docs.crawl4ai.com/advanced/undetected-browser/
        self.browser_config = BrowserConfig(
            headless=True,              # Can be False for better stealth but requires display
            verbose=False,              # Reduce logging noise
            browser_type="chromium",    # Default browser type
            use_managed_browser=True,   # Use Crawl4AI's managed browser instance
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Configure crawler run parameters
        # Source: https://docs.crawl4ai.com/api/parameters/
        self.run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,        # Always fetch fresh content
            word_count_threshold=1,             # Don't filter out short pages
            extraction_strategy=None,           # Can be set later for LLM extraction
            chunking_strategy=None              # Default chunking
        )
        
        # Initialize Supabase handler
        self.storage_handler = SupabaseHandler()
    
    async def crawl_with_memory_adaptive_dispatcher(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Crawl multiple URLs using MemoryAdaptiveDispatcher for optimal resource management.
        Source: https://docs.crawl4ai.com/advanced/multi-url-crawling/#memoryadaptivedispatcher-default
        """
        print(f"🚀 Starting crawl with Memory Adaptive Dispatcher for {len(urls)} URLs")
        
        # Configure rate limiting
        rate_limiter = RateLimiter(
            base_delay=(1.0, 3.0),          # Random delay between 1-3 seconds
            max_delay=30.0,                 # Maximum backoff delay
            max_retries=3,                  # Retry attempts for rate-limited requests
            rate_limit_codes=[429, 503]     # HTTP codes that trigger rate limiting
        )
        
        # Configure monitoring for real-time progress tracking
        monitor = CrawlerMonitor()
        
        # Setup memory-adaptive dispatcher
        dispatcher = MemoryAdaptiveDispatcher(
            memory_threshold_percent=90.0,   # Pause if memory exceeds 90%
            check_interval=1.0,              # Check memory every second
            max_session_permit=10,           # Maximum concurrent tasks
            rate_limiter=rate_limiter,
            monitor=monitor
        )
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            print("📊 Crawling in progress...")
            
            # Batch processing mode - collect all results
            results = await crawler.arun_many(
                urls=urls,
                config=self.run_config,
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
                        'extracted_content': result.extracted_content,
                        'status_code': result.status_code,
                        'crawl_time': datetime.now().isoformat()
                    })
                    print(f"✓ Successfully crawled: {result.url}")
                else:
                    print(f"✗ Failed to crawl {result.url}: {result.error_message}")
            
            print(f"🎉 Crawling completed! {len(successful_results)}/{len(urls)} URLs successful")
            return successful_results
    
    async def crawl_with_semaphore_dispatcher(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Use SemaphoreDispatcher for simple concurrency control.
        Source: https://docs.crawl4ai.com/advanced/multi-url-crawling/#semaphoredispatcher
        """
        print(f"🔒 Starting crawl with Semaphore Dispatcher for {len(urls)} URLs")
        
        dispatcher = SemaphoreDispatcher(
            max_session_permit=20,           # Fixed number of concurrent tasks
            rate_limiter=RateLimiter(
                base_delay=(0.5, 1.0),
                max_delay=10.0
            )
        )
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            results = await crawler.arun_many(
                urls=urls,
                config=self.run_config,
                dispatcher=dispatcher
            )
            
            successful_results = []
            for result in results:
                if result.success:
                    successful_results.append({
                        'url': result.url,
                        'content': result.markdown,
                        'title': result.metadata.get('title', 'No title'),
                        'status_code': result.status_code
                    })
            
            return successful_results
    
    async def crawl_with_llm_analysis(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Crawl URLs with integrated LLM analysis for structured data extraction.
        Source: https://docs.crawl4ai.com/core/quickstart/#llm-extraction
        Following: Inject_OpenAI_Analysis_duringCrawl.prompt.md specifications
        """
        print(f"🧠 Starting LLM-powered crawl for {len(urls)} URLs")
        
        # Check for OpenAI API key
        if not env_config.has_openai_config:
            print("⚠ OpenAI API key not found, skipping LLM analysis")
            return await self.crawl_with_memory_adaptive_dispatcher(urls)
        
        # Configure LLM extraction strategy - Following official pattern
        # Source: https://docs.crawl4ai.com/extraction/llm-strategies/
        llm_strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider="openai/gpt-4o-mini",  # Official docs pattern
                api_token=env_config.openai_api_key
            ),
            schema=PageSummary.model_json_schema(),   # Official schema method
            extraction_type="schema",
            instruction="""Extract the main title and create a concise summary from this web page content. 
            For the title: Use the main page heading, document title, or prominent header text.
            For the summary: Write a 5-7 sentence description of what this page is about and its main purpose.
            If you cannot find a clear title, extract the most prominent heading or use the page's main topic.
            If you cannot determine the page content, describe what you can see. And how it works""",
            chunk_token_threshold=1000,
            apply_chunking=True,
            input_format="markdown",
            extra_args={"temperature": 0.2}  # Make output deterministic
        )
        
        # Update run config with LLM strategy - Following official pattern
        # Source: Inject_OpenAI_Analysis_duringCrawl.prompt.md
        crawler_config_llm = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=llm_strategy,
            word_count_threshold=1   # don't filter out short pages
        )
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            results = await crawler.arun_many(
                urls=urls,
                config=crawler_config_llm
            )
            
            analyzed_results = []
            for result in results:
                if result.success and result.extracted_content:
                    try:
                        # Following official pattern: data = json.loads(result.extracted_content)
                        data = json.loads(result.extracted_content)
                        analyzed_results.append({
                            'url': result.url,
                            'raw_markdown': result.markdown,
                            'analysis': data,  # data will be a dict with 'title' and 'summary'
                            'status_code': result.status_code,
                            'crawl_time': datetime.now().isoformat()
                        })
                        print(f"🧠 LLM analysis completed for: {result.url}")
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse LLM output for {result.url}: {str(e)}")
                        # Fallback to basic result
                        analyzed_results.append({
                            'url': result.url,
                            'raw_markdown': result.markdown,
                            'analysis': None,
                            'status_code': result.status_code
                        })
                else:
                    print(f"✗ Failed to analyze {result.url}: {result.error_message if result else 'Unknown error'}")
            
            return analyzed_results
    
    async def crawl_prediction_markets_with_llm(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Crawl prediction market URLs with LLM analysis for structured prediction market data extraction.
        Source: https://docs.crawl4ai.com/extraction/llm-strategies/
        Uses PredictionMarketBet schema to match Testing table structure.
        """
        print(f"🎲 Starting prediction market LLM crawl for {len(urls)} URLs")
        
        # Check for OpenAI API key
        if not env_config.has_openai_config:
            print("⚠ OpenAI API key not found, cannot extract prediction market data")
            return []
        
        # Configure LLM extraction strategy for prediction markets
        # Source: https://docs.crawl4ai.com/extraction/llm-strategies/
        llm_strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider="openai/gpt-4o-mini",  # Official docs pattern
                api_token=env_config.openai_api_key
            ),
            schema=PredictionMarketBet.model_json_schema(),   # Use prediction market schema
            extraction_type="schema",
            instruction="""Extract prediction market data from this page. Look for:
            - website_name: The name of the prediction market site (e.g., Polymarket, Kalshi, PredictIt, Manifold Markets)
            - bet_title: The title or name of the specific prediction market or betting event
            - odds: Current odds, probability percentage, or price for this market (e.g., "62%", "$0.38", "3:1")
            - summary: Brief description of what this market is predicting or betting on
            
            Focus on individual prediction markets or betting events. If multiple markets are shown, extract the most prominent one.
            Be precise with the odds format as displayed on the site.""",
            chunk_token_threshold=1000,
            apply_chunking=True,
            input_format="markdown",
            extra_args={"temperature": 0.2}  # Make output deterministic
        )
        
        # Update run config with prediction market LLM strategy
        crawler_config_prediction = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=llm_strategy,
            word_count_threshold=1   # don't filter out short pages
        )
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            results = await crawler.arun_many(
                urls=urls,
                config=crawler_config_prediction
            )
            
            analyzed_results = []
            for result in results:
                if result.success and result.extracted_content:
                    try:
                        # DEBUG: Show raw LLM response
                        print(f"🔍 Raw LLM Response for {result.url}:")
                        print(f"   Length: {len(result.extracted_content)} chars")
                        print(f"   Content: {result.extracted_content[:500]}...")
                        
                        # Following official pattern: data = json.loads(result.extracted_content)
                        data = json.loads(result.extracted_content)
                        analyzed_results.append({
                            'url': result.url,
                            'raw_markdown': result.markdown,
                            'prediction_data': data,  # data will match PredictionMarketBet schema
                            'status_code': result.status_code,
                            'crawl_time': datetime.now().isoformat()
                        })
                        print(f"🎲 Prediction market data extracted for: {result.url}")
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse prediction market LLM output for {result.url}: {str(e)}")
                        # Fallback to basic result
                        analyzed_results.append({
                            'url': result.url,
                            'raw_markdown': result.markdown,
                            'prediction_data': None,
                            'status_code': result.status_code
                        })
                else:
                    print(f"✗ Failed to extract prediction market data from {result.url}: {result.error_message if result else 'Unknown error'}")
            
            return analyzed_results
    
    async def crawl_and_store_in_supabase(self, urls: List[str]) -> bool:
        """
        Crawl URLs and store results in Supabase database with LLM analysis.
        Ensures .env file contains SUPABASE_URL and SUPABASE_KEY
        """
        if not self.storage_handler.is_available:
            print("❌ Supabase not configured. Check environment variables.")
            return False
        
        print(f"💾 Starting crawl and store workflow with LLM analysis for {len(urls)} URLs")
        
        # Crawl with LLM analysis
        results = await self.crawl_with_llm_analysis(urls)
        
        if not results:
            print("❌ No results from LLM analysis")
            return False
        
        # Store results using the new schema with separate title/summary columns
        stored_count = 0
        for result in results:
            try:
                url = result.get('url')
                if not url:
                    print("⚠ Skipping result with no URL")
                    continue
                    
                raw_markdown = result.get('raw_markdown', '')
                analysis_list = result.get('analysis', [])
                
                if analysis_list:
                    # Handle both list and direct dict formats
                    if isinstance(analysis_list, list) and len(analysis_list) > 0:
                        analysis = analysis_list[0]
                    else:
                        analysis = analysis_list
                    
                    # Ensure analysis is a dict
                    if isinstance(analysis, dict):
                        title = analysis.get('title', 'No title extracted')
                        summary = analysis.get('summary', 'No summary extracted')
                    else:
                        title = 'No title extracted'
                        summary = 'No summary extracted'
                    
                    # Store using new schema
                    response = self.storage_handler.store_page_summary(
                        url=url,
                        title=title,
                        summary=summary,
                        raw_markdown=raw_markdown
                    )
                    
                    if response:
                        stored_count += 1
                        print(f"✓ Stored with LLM analysis: {url}")
                    else:
                        print(f"❌ Failed to store: {url}")
                else:
                    print(f"⚠ No LLM analysis for: {url}")
                    
            except Exception as e:
                print(f"❌ Error storing {result.get('url', 'unknown')}: {str(e)}")
        
        print(f"🎯 Storage complete: {stored_count}/{len(results)} results stored with LLM analysis")
        return stored_count > 0
    
    async def crawl_and_store_prediction_markets(self, urls: List[str]) -> bool:
        """
        Crawl prediction market URLs and store results in Supabase with prediction market schema.
        Uses store_prediction_market_data() method to match Testing table structure.
        """
        if not self.storage_handler.is_available:
            print("❌ Supabase not configured. Check environment variables.")
            return False
        
        print(f"🎲 Starting prediction market crawl and store workflow for {len(urls)} URLs")
        
        # Crawl with prediction market LLM analysis
        results = await self.crawl_prediction_markets_with_llm(urls)
        
        if not results:
            print("❌ No results from prediction market LLM analysis")
            return False
        
        # Store results using the new prediction market schema
        stored_count = 0
        for result in results:
            try:
                url = result.get('url')
                if not url:
                    print("⚠ Skipping result with no URL")
                    continue
                    
                prediction_data_raw = result.get('prediction_data')
                
                # DEBUG: Print what the LLM actually returned
                print(f"🔍 DEBUG - Raw LLM output for {url}:")
                print(f"   Type: {type(prediction_data_raw)}")
                print(f"   Content: {prediction_data_raw}")
                
                # Handle both single object and array responses from LLM
                markets_to_store = []
                if prediction_data_raw:
                    if isinstance(prediction_data_raw, list):
                        # LLM returned array of markets - store all of them
                        markets_to_store = prediction_data_raw
                        print(f"📊 LLM returned {len(markets_to_store)} prediction markets")
                    elif isinstance(prediction_data_raw, dict):
                        # LLM returned single market
                        markets_to_store = [prediction_data_raw]
                        print(f"📊 LLM returned 1 prediction market")
                
                # Store each prediction market
                for i, market_data in enumerate(markets_to_store):
                    try:
                        # Remove any extra fields that aren't in our schema
                        clean_data = {
                            'website_name': market_data.get('website_name', ''),
                            'bet_title': market_data.get('bet_title', ''),
                            'odds': market_data.get('odds', ''),
                            'summary': market_data.get('summary', '')
                        }
                        
                        prediction_bet = PredictionMarketBet(**clean_data)
                        
                        # Store using prediction market schema
                        response = self.storage_handler.store_prediction_market_data(
                            source_url=url,
                            prediction_data=prediction_bet
                        )
                        
                        if response:
                            stored_count += 1
                            print(f"✓ Stored prediction market {i+1}: {prediction_bet.bet_title} from {prediction_bet.website_name}")
                        else:
                            print(f"❌ Failed to store prediction market {i+1} from: {url}")
                            
                    except Exception as validation_error:
                        print(f"❌ Failed to validate prediction market {i+1} from {url}: {str(validation_error)}")
                        print(f"   Market data: {market_data}")
                        
                if not markets_to_store:
                    print(f"⚠ No prediction market data extracted from: {url}")
                    
            except Exception as e:
                print(f"❌ Error storing prediction market from {result.get('url', 'unknown')}: {str(e)}")
        
        print(f"🎯 Prediction market storage complete: {stored_count}/{len(results)} results stored")
        return stored_count > 0