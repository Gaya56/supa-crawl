#!/usr/bin/env python3
"""
AsyncWebCrawler Basic Functionality Tests
Based on official Crawl4AI documentation: https://docs.crawl4ai.com/

Tests the core AsyncWebCrawler functionality including:
- Basic web crawling
- Browser configuration
- Multi-URL processing
- Error handling
"""

import asyncio
import os
import sys
import unittest
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


class TestAsyncWebCrawlerBasic(unittest.TestCase):
    """Test suite for basic AsyncWebCrawler functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_urls = [
            "https://httpbin.org/html",
            "https://example.com"
        ]
        
        # Configure browser for testing
        # Source: https://docs.crawl4ai.com/basic-usage/browser-config/
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=False
        )
        
        # Configure crawler run parameters
        # Source: https://docs.crawl4ai.com/basic-usage/crawler-config/
        self.run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=1,
            extraction_strategy=None,  # Use default extraction
            timeout=30000  # 30 seconds timeout
        )
    
    async def test_single_url_crawling(self):
        """Test crawling a single URL"""
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(
                url=self.test_urls[0],
                config=self.run_config
            )
            
            self.assertTrue(result.success, f"Crawling failed: {result.error_message}")
            self.assertIsNotNone(result.markdown)
            self.assertGreater(len(result.markdown), 0)
            self.assertEqual(result.url, self.test_urls[0])
    
    async def test_multi_url_crawling(self):
        """Test crawling multiple URLs with arun_many"""
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            results = await crawler.arun_many(
                urls=self.test_urls,
                config=self.run_config
            )
            
            self.assertEqual(len(results), len(self.test_urls))
            
            for result in results:
                self.assertTrue(result.success, f"Crawling failed for {result.url}: {result.error_message}")
                self.assertIsNotNone(result.markdown)
                self.assertGreater(len(result.markdown), 0)
    
    async def test_streaming_crawling(self):
        """Test streaming mode for real-time processing"""
        processed_count = 0
        
        async def process_result(result):
            nonlocal processed_count
            self.assertTrue(result.success)
            self.assertGreater(len(result.markdown), 0)
            processed_count += 1
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            async for result in crawler.arun_many(
                urls=self.test_urls,
                config=self.run_config,
                stream=True
            ):
                await process_result(result)
        
        self.assertEqual(processed_count, len(self.test_urls))
    
    def test_browser_config_validation(self):
        """Test browser configuration validation"""
        # Test valid configuration
        config = BrowserConfig(
            headless=True,
            verbose=False
        )
        self.assertIsInstance(config, BrowserConfig)
        
        # Test with additional parameters
        config_with_params = BrowserConfig(
            headless=True,
            verbose=False,
            extra_args=["--disable-dev-shm-usage"]
        )
        self.assertIsInstance(config_with_params, BrowserConfig)
    
    def test_crawler_run_config_validation(self):
        """Test crawler run configuration validation"""
        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=10,
            timeout=30000
        )
        self.assertIsInstance(config, CrawlerRunConfig)
        self.assertEqual(config.cache_mode, CacheMode.BYPASS)
        self.assertEqual(config.word_count_threshold, 10)


async def run_async_tests():
    """Run async test methods"""
    test_instance = TestAsyncWebCrawlerBasic()
    test_instance.setUp()
    
    print("Running AsyncWebCrawler Basic Tests")
    print("=" * 50)
    
    try:
        print("1. Testing single URL crawling...")
        await test_instance.test_single_url_crawling()
        print("   ✓ Single URL crawling test passed")
        
        print("2. Testing multi-URL crawling...")
        await test_instance.test_multi_url_crawling()
        print("   ✓ Multi-URL crawling test passed")
        
        print("3. Testing streaming crawling...")
        await test_instance.test_streaming_crawling()
        print("   ✓ Streaming crawling test passed")
        
        print("4. Testing browser config validation...")
        test_instance.test_browser_config_validation()
        print("   ✓ Browser config validation test passed")
        
        print("5. Testing crawler run config validation...")
        test_instance.test_crawler_run_config_validation()
        print("   ✓ Crawler run config validation test passed")
        
        print("\n" + "=" * 50)
        print("✓ All AsyncWebCrawler basic tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        return False


if __name__ == "__main__":
    # Run async tests
    success = asyncio.run(run_async_tests())
    
    if not success:
        sys.exit(1)
    
    print("\nAsyncWebCrawler basic functionality verified successfully!")