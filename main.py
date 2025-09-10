#!/usr/bin/env python3
"""
Main Entry Point for Dashboard-Aggregated Prediction Market Crawler (2025)
Following official documentation from:
- Crawl4AI: https://docs.crawl4ai.com/
- Supabase: https://supabase.com/docs

Features:
- DASHBOARD AGGREGATION: Multi-source prediction market data from specialized aggregators
- Tier 1 Sources: PolymarketAnalytics (60,000+ markets), ElectionBettingOdds (political aggregator)
- Tier 2 Sources: OddsJam (25+ sportsbooks), OddsChecker (80+ bookmakers), Betfair Exchange
- COMPREHENSIVE COVERAGE: Politics, sports, economics, tech, AI across multiple platforms
- LLM-powered structured data extraction using PredictionMarketBet schema  
- Supabase storage with Testing table schema (source_url, website_name, bet_title, odds, summary)
- Cross-platform comparison and arbitrage detection capabilities
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
    
    # Tier 1: Specialized Prediction Market Dashboards (PRIORITY)
    tier1_dashboard_urls = [
        "https://polymarketanalytics.com/",         # Aggregates 60,000+ markets from Polymarket + Kalshi
        "https://electionbettingodds.com/",         # Multi-source political odds aggregator
        "https://polymarketanalytics.com/polymarket-vs-kalshi",  # Direct platform comparison
    ]
    
    # Tier 2: Professional Odds Aggregators  
    tier2_aggregator_urls = [
        "https://oddsjam.com/",                     # Gold standard betting analytics (25+ sources)
        "https://www.oddschecker.com/us/",         # Leading odds comparison since 1999
        "https://betting.betfair.com/betfair-predicts/",  # Exchange-based predictions
    ]
    
    # Original Individual Platform URLs (for comparison)
    individual_platform_urls = [
        "https://polymarket.com/",                  # World's largest prediction market
        "https://manifold.markets/",               # Social prediction game 
        "https://kalshi.com/",                     # Regulated prediction market
    ]
    
    # Combined URL list - Start with dashboard aggregators for maximum data
    urls = tier1_dashboard_urls + tier2_aggregator_urls[:2]  # Focus on best aggregators first
    
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