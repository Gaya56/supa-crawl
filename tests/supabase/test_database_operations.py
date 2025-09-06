#!/usr/bin/env python3
"""
Supabase Integration Tests
Based on official Supabase documentation: https://supabase.com/docs/reference/python/

Tests the Supabase client functionality including:
- Database connection
- Table operations (pages table)
- Insert/Select operations
- Error handling
"""

import asyncio
import os
import sys
import unittest
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from supabase import create_client, Client
except ImportError:
    print("Supabase client not installed. Install with: pip install supabase")
    sys.exit(1)


class TestSupabaseIntegration(unittest.TestCase):
    """Test suite for Supabase database operations"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Supabase configuration
        # Source: https://supabase.com/docs/reference/python/initializing
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            self.skipTest("Supabase credentials not configured in environment variables")
        
        # Create Supabase client
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Test data
        self.test_page_data = {
            "url": f"https://test-{datetime.now().isoformat()}.example.com",
            "content": "Test content from Supabase integration test"
        }
    
    def test_client_connection(self):
        """Test Supabase client connection"""
        self.assertIsInstance(self.supabase, Client)
        self.assertIsNotNone(self.supabase.url)
        self.assertIsNotNone(self.supabase.auth)
    
    def test_pages_table_insert(self):
        """Test inserting data into pages table"""
        try:
            # Insert test data
            # Source: https://supabase.com/docs/reference/python/insert
            result = self.supabase.table('pages').insert(self.test_page_data).execute()
            
            self.assertIsNotNone(result.data)
            self.assertEqual(len(result.data), 1)
            
            inserted_page = result.data[0]
            self.assertEqual(inserted_page['url'], self.test_page_data['url'])
            self.assertEqual(inserted_page['content'], self.test_page_data['content'])
            self.assertIsNotNone(inserted_page['id'])
            self.assertIsNotNone(inserted_page['created_at'])
            
            # Store ID for cleanup
            self.inserted_id = inserted_page['id']
            
        except Exception as e:
            self.fail(f"Failed to insert into pages table: {str(e)}")
    
    def test_pages_table_select(self):
        """Test selecting data from pages table"""
        try:
            # First insert test data
            insert_result = self.supabase.table('pages').insert(self.test_page_data).execute()
            inserted_id = insert_result.data[0]['id']
            
            # Select the inserted data
            # Source: https://supabase.com/docs/reference/python/select
            select_result = self.supabase.table('pages').select("*").eq('id', inserted_id).execute()
            
            self.assertIsNotNone(select_result.data)
            self.assertEqual(len(select_result.data), 1)
            
            selected_page = select_result.data[0]
            self.assertEqual(selected_page['url'], self.test_page_data['url'])
            self.assertEqual(selected_page['content'], self.test_page_data['content'])
            
            # Cleanup
            self.supabase.table('pages').delete().eq('id', inserted_id).execute()
            
        except Exception as e:
            self.fail(f"Failed to select from pages table: {str(e)}")
    
    def test_pages_table_filter(self):
        """Test filtering data from pages table"""
        try:
            # Insert multiple test records
            test_data = [
                {"url": "https://filter-test-1.example.com", "content": "Filter test content 1"},
                {"url": "https://filter-test-2.example.com", "content": "Filter test content 2"}
            ]
            
            insert_result = self.supabase.table('pages').insert(test_data).execute()
            inserted_ids = [row['id'] for row in insert_result.data]
            
            # Filter by URL pattern
            # Source: https://supabase.com/docs/reference/python/filter
            filter_result = self.supabase.table('pages').select("*").like('url', '%filter-test%').execute()
            
            self.assertGreaterEqual(len(filter_result.data), 2)
            
            # Verify filtered results contain our test data
            urls = [row['url'] for row in filter_result.data]
            self.assertIn("https://filter-test-1.example.com", urls)
            self.assertIn("https://filter-test-2.example.com", urls)
            
            # Cleanup
            for record_id in inserted_ids:
                self.supabase.table('pages').delete().eq('id', record_id).execute()
                
        except Exception as e:
            self.fail(f"Failed to filter pages table: {str(e)}")
    
    def test_pages_table_update(self):
        """Test updating data in pages table"""
        try:
            # Insert test data
            insert_result = self.supabase.table('pages').insert(self.test_page_data).execute()
            inserted_id = insert_result.data[0]['id']
            
            # Update the record
            # Source: https://supabase.com/docs/reference/python/update
            updated_content = "Updated content from test"
            update_result = self.supabase.table('pages').update(
                {"content": updated_content}
            ).eq('id', inserted_id).execute()
            
            self.assertIsNotNone(update_result.data)
            self.assertEqual(len(update_result.data), 1)
            self.assertEqual(update_result.data[0]['content'], updated_content)
            
            # Cleanup
            self.supabase.table('pages').delete().eq('id', inserted_id).execute()
            
        except Exception as e:
            self.fail(f"Failed to update pages table: {str(e)}")
    
    def test_pages_table_delete(self):
        """Test deleting data from pages table"""
        try:
            # Insert test data
            insert_result = self.supabase.table('pages').insert(self.test_page_data).execute()
            inserted_id = insert_result.data[0]['id']
            
            # Delete the record
            # Source: https://supabase.com/docs/reference/python/delete
            delete_result = self.supabase.table('pages').delete().eq('id', inserted_id).execute()
            
            self.assertIsNotNone(delete_result.data)
            self.assertEqual(len(delete_result.data), 1)
            self.assertEqual(delete_result.data[0]['id'], inserted_id)
            
            # Verify deletion
            select_result = self.supabase.table('pages').select("*").eq('id', inserted_id).execute()
            self.assertEqual(len(select_result.data), 0)
            
        except Exception as e:
            self.fail(f"Failed to delete from pages table: {str(e)}")
    
    def tearDown(self):
        """Clean up any remaining test data"""
        try:
            # Clean up any test records that might be left behind
            self.supabase.table('pages').delete().like('url', '%test%').execute()
            self.supabase.table('pages').delete().like('url', '%filter-test%').execute()
        except:
            pass  # Ignore cleanup errors


def run_tests():
    """Run Supabase integration tests"""
    print("Running Supabase Integration Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSupabaseIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n" + "=" * 50)
        print("✓ All Supabase integration tests passed!")
        return True
    else:
        print(f"\n✗ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return False


if __name__ == "__main__":
    success = run_tests()
    
    if not success:
        sys.exit(1)
    
    print("\nSupabase integration functionality verified successfully!")