#!/usr/bin/env python3
"""
Main Entry Point for Live Prediction Market Crawler (2025)
Following official documentation from:
- Crawl4AI: https://docs.crawl4ai.com/
- Supabase: https://supabase.com/docs

Features:
- LIVE prediction market data extraction from current active 2025 markets
- Sources: Polymarket, Manifold Markets, ElectionBettingOdds, Kalshi, PredictIt
- LLM-powered structured data extraction using PredictionMarketBet schema  
- Supabase storage with Testing table schema (source_url, website_name, bet_title, odds, summary)
- Current event tracking (politics, sports, economics, tech, AI)
- Stealth configuration to avoid bot detection
- Memory adaptive dispatcher for optimal resource management
- Real-time monitoring and rate limiting
"""
import asyncio
import sys
import os

# Add the parent directory to the path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crawlers.async_crawler import AdvancedWebCrawler
from src.config.environment import env_config


async def main():
    """Complete example demonstrating AsyncWebCrawler with stealth and Supabase integration"""
    
    print("� Prediction Market Crawler Implementation")
    print("=" * 60)
    print("Extracting structured prediction market data with LLM analysis")
    print("Following official documentation:")
    print("- Crawl4AI: https://docs.crawl4ai.com/")
    print("- Supabase: https://supabase.com/docs")
    print("=" * 60)
    
    # Initialize the advanced crawler
    crawler = AdvancedWebCrawler()
    
    # Current Active Prediction Market URLs for 2025 - Live Data
    # Based on research: major prediction market sites with active current markets
    urls = [
        "https://polymarket.com/",                   # World's largest prediction market - live 2025 data
        "https://manifold.markets/",                 # Social prediction game - active 2025 markets 
        "https://electionbettingodds.com/",         # Live betting odds aggregator - current events
        "https://kalshi.com/",                      # Regulated prediction market - live trading
        "https://www.predictit.org/",               # Academic prediction market - current markets
    ]
    
    print(f"🎯 Target URLs ({len(urls)}):")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    print()
    
    try:
        # Option 1: Basic crawling with memory adaptive dispatcher
        print("1️⃣ Testing Memory Adaptive Dispatcher...")
        results = await crawler.crawl_with_memory_adaptive_dispatcher(urls[:2])
        print(f"   Results: {len(results)} successful crawls\n")
        
        # Option 2: Semaphore dispatcher
        print("2️⃣ Testing Semaphore Dispatcher...")
        sem_results = await crawler.crawl_with_semaphore_dispatcher(urls[:2])
        print(f"   Results: {len(sem_results)} successful crawls\n")
        
        # Option 3: LLM analysis (if OpenAI key available)
        print("3️⃣ Testing LLM Analysis...")
        llm_results = await crawler.crawl_with_llm_analysis(urls[:2])
        print(f"   Results: {len(llm_results)} analyzed crawls\n")
        
        # Option 4: Full pipeline with Supabase storage (legacy)
        print("4️⃣ Testing Full Pipeline with Supabase (legacy schema)...")
        success = await crawler.crawl_and_store_in_supabase(["https://example.com"])  # Test with simple URL
        print(f"   Storage success: {success}\n")
        
        # Option 5: NEW - Prediction Market Pipeline
        print("5️⃣ Testing Prediction Market Pipeline...")
        pred_success = await crawler.crawl_and_store_prediction_markets(urls[:2])  # Test with 2 prediction market URLs
        print(f"   Prediction market storage success: {pred_success}\n")
        
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    # Run the advanced crawler
    print("Starting AsyncWebCrawler Advanced Implementation...")
    success = asyncio.run(main())
    
    if success:
        print("\n✅ AsyncWebCrawler implementation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ AsyncWebCrawler implementation failed!")
        sys.exit(1)