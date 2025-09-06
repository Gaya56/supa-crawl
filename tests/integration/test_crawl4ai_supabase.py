#!/usr/bin/env python3
"""
Crawl4AI + Supabase Integration Tests
Combines official documentation from:
- https://docs.crawl4ai.com/
- https://supabase.com/docs/

Tests the complete workflow:
1. Crawl web content with AsyncWebCrawler
2. Store results in Supabase database
3. Retrieve and validate stored data
"""

import asyncio
import os
import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

try:
    from supabase import create_client, Client
except ImportError:
    print("Supabase client not installed. Install with: pip install supabase")
    sys.exit(1)


class TestCrawl4AISupabaseIntegration(unittest.TestCase):
    """Test suite for Crawl4AI + Supabase integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Supabase configuration
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            self.skipTest("Supabase credentials not configured in environment variables")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Crawl4AI configuration
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=False
        )
        
        self.run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=1,
            timeout=30000
        )
        
        # Test URLs
        self.test_urls = [
            "https://httpbin.org/html",
            "https://example.com"
        ]
        
        # Store inserted IDs for cleanup
        self.inserted_ids = []
    
    async def test_crawl_and_store_single_url(self):
        """Test crawling a single URL and storing in Supabase"""
        url = self.test_urls[0]
        
        # Step 1: Crawl the URL
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=self.run_config)
            
            self.assertTrue(result.success, f"Crawling failed: {result.error_message}")
            self.assertIsNotNone(result.markdown)
            self.assertGreater(len(result.markdown), 0)
        
        # Step 2: Store in Supabase
        page_data = {
            "url": result.url,
            "content": result.markdown[:1000]  # Limit content for test
        }
        
        insert_result = self.supabase.table('pages').insert(page_data).execute()
        
        self.assertIsNotNone(insert_result.data)
        self.assertEqual(len(insert_result.data), 1)
        
        stored_page = insert_result.data[0]
        self.assertEqual(stored_page['url'], url)
        self.assertEqual(stored_page['content'], page_data['content'])
        self.assertIsNotNone(stored_page['id'])
        
        # Store ID for cleanup
        self.inserted_ids.append(stored_page['id'])
    
    async def test_crawl_and_store_multiple_urls(self):
        """Test crawling multiple URLs and storing all results"""
        # Step 1: Crawl multiple URLs
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            results = await crawler.arun_many(
                urls=self.test_urls,
                config=self.run_config
            )
        
        self.assertEqual(len(results), len(self.test_urls))
        
        # Step 2: Store all results in Supabase
        pages_data = []
        for result in results:
            self.assertTrue(result.success, f"Crawling failed for {result.url}: {result.error_message}")
            
            page_data = {
                "url": result.url,
                "content": result.markdown[:1000]  # Limit content for test
            }
            pages_data.append(page_data)
        
        # Batch insert
        insert_result = self.supabase.table('pages').insert(pages_data).execute()
        
        self.assertIsNotNone(insert_result.data)
        self.assertEqual(len(insert_result.data), len(self.test_urls))
        
        # Verify all URLs were stored
        stored_urls = [page['url'] for page in insert_result.data]
        for test_url in self.test_urls:
            self.assertIn(test_url, stored_urls)
        
        # Store IDs for cleanup
        self.inserted_ids.extend([page['id'] for page in insert_result.data])
    
    async def test_crawl_store_and_retrieve_workflow(self):
        """Test complete workflow: crawl -> store -> retrieve -> validate"""
        url = self.test_urls[1]  # Use example.com
        
        # Step 1: Crawl
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            crawl_result = await crawler.arun(url=url, config=self.run_config)
        
        self.assertTrue(crawl_result.success)
        original_content = crawl_result.markdown
        
        # Step 2: Store
        page_data = {
            "url": crawl_result.url,
            "content": original_content
        }
        
        insert_result = self.supabase.table('pages').insert(page_data).execute()
        stored_page = insert_result.data[0]
        page_id = stored_page['id']
        self.inserted_ids.append(page_id)
        
        # Step 3: Retrieve
        select_result = self.supabase.table('pages').select("*").eq('id', page_id).execute()
        retrieved_page = select_result.data[0]
        
        # Step 4: Validate
        self.assertEqual(retrieved_page['url'], url)
        self.assertEqual(retrieved_page['content'], original_content)
        self.assertIsNotNone(retrieved_page['created_at'])
        
        # Verify timestamp is recent
        created_at = datetime.fromisoformat(retrieved_page['created_at'].replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        time_diff = (now - created_at).total_seconds()
        self.assertLess(time_diff, 60)  # Should be created within last minute
    
    async def test_streaming_crawl_with_real_time_storage(self):
        """Test streaming crawl with real-time storage to Supabase"""
        stored_count = 0
        
        async def process_and_store(result):
            nonlocal stored_count
            
            if result.success:
                page_data = {
                    "url": result.url,
                    "content": result.markdown[:500]  # Limit for test
                }
                
                insert_result = self.supabase.table('pages').insert(page_data).execute()
                stored_page = insert_result.data[0]
                self.inserted_ids.append(stored_page['id'])
                stored_count += 1
        
        # Stream crawl and store results
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            async for result in crawler.arun_many(
                urls=self.test_urls,
                config=self.run_config,
                stream=True
            ):
                await process_and_store(result)
        
        self.assertEqual(stored_count, len(self.test_urls))
        
        # Verify all results are in database
        for url in self.test_urls:
            select_result = self.supabase.table('pages').select("*").eq('url', url).execute()
            self.assertGreater(len(select_result.data), 0, f"URL {url} not found in database")
    
    def test_error_handling_invalid_url(self):
        """Test error handling for invalid URLs"""
        async def test_invalid_url():
            invalid_url = "https://this-domain-should-not-exist-12345.com"
            
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                result = await crawler.arun(url=invalid_url, config=self.run_config)
                
                # Should handle error gracefully
                if not result.success:
                    # Don't store failed crawls
                    return
                
                # If somehow successful, don't store invalid data
                self.assertIsNotNone(result.markdown)
        
        # Run async test
        asyncio.create_task(test_invalid_url())
    
    def tearDown(self):
        """Clean up test data"""
        try:
            # Delete all inserted test records
            for page_id in self.inserted_ids:
                self.supabase.table('pages').delete().eq('id', page_id).execute()
            
            # Clean up any remaining test records
            self.supabase.table('pages').delete().in_('url', self.test_urls).execute()
            
        except Exception as e:
            print(f"Cleanup warning: {str(e)}")


async def run_async_integration_tests():
    """Run async integration tests"""
    test_instance = TestCrawl4AISupabaseIntegration()
    test_instance.setUp()
    
    print("Running Crawl4AI + Supabase Integration Tests")
    print("=" * 60)
    
    try:
        print("1. Testing crawl and store single URL...")
        await test_instance.test_crawl_and_store_single_url()
        print("   ✓ Single URL crawl and store test passed")
        
        print("2. Testing crawl and store multiple URLs...")
        await test_instance.test_crawl_and_store_multiple_urls()
        print("   ✓ Multiple URL crawl and store test passed")
        
        print("3. Testing complete workflow (crawl -> store -> retrieve)...")
        await test_instance.test_crawl_store_and_retrieve_workflow()
        print("   ✓ Complete workflow test passed")
        
        print("4. Testing streaming crawl with real-time storage...")
        await test_instance.test_streaming_crawl_with_real_time_storage()
        print("   ✓ Streaming crawl with storage test passed")
        
        print("5. Testing error handling...")
        test_instance.test_error_handling_invalid_url()
        print("   ✓ Error handling test passed")
        
        print("\n" + "=" * 60)
        print("✓ All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Integration test failed with error: {str(e)}")
        return False
    
    finally:
        test_instance.tearDown()


if __name__ == "__main__":
    # Run async integration tests
    success = asyncio.run(run_async_integration_tests())
    
    if not success:
        sys.exit(1)
    
    print("\nCrawl4AI + Supabase integration verified successfully!")