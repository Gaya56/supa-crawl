#!/usr/bin/env python3
"""
Supabase Database Handler
Following official documentation from:
- Supabase: https://supabase.com/docs/reference/python/initializing
"""
import sys
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from ..config.environment import env_config

# Import check for Supabase client
try:
    from supabase import create_client, Client
except ImportError:
    print("Supabase client not installed. Install with: pip install supabase")
    sys.exit(1)


class SupabaseHandler:
    """
    Handler for Supabase database operations
    Source: https://supabase.com/docs/reference/python/initializing
    """
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """
        Initialize Supabase client using official pattern
        Source: https://supabase.com/docs/reference/python/initializing
        """
        if env_config.has_supabase_config:
            try:
                # Official Supabase client initialization pattern
                self.client = create_client(env_config.supabase_url, env_config.supabase_key)
                print(f"✓ Supabase client initialized: {env_config.supabase_url[:50]}...")
            except Exception as e:
                print(f"❌ Failed to initialize Supabase client: {str(e)}")
                self.client = None
        else:
            print("⚠ Supabase credentials not found in environment variables")
    
    @property
    def is_available(self) -> bool:
        """Check if Supabase client is available"""
        return self.client is not None
    
    def _extract_first_paragraph(self, markdown_content: str) -> str:
        """
        Extract the first meaningful paragraph from markdown content.
        Limits to ~500 characters for database storage efficiency.
        """
        if not markdown_content:
            return ""
        
        # Split by double newlines (paragraph breaks)
        paragraphs = markdown_content.split('\n\n')
        
        # Find first substantial paragraph (more than 50 characters)
        for paragraph in paragraphs:
            # Clean up the paragraph
            clean_paragraph = paragraph.strip().replace('\n', ' ')
            # Remove markdown headers and formatting
            clean_paragraph = clean_paragraph.lstrip('#').strip()
            
            if len(clean_paragraph) > 50:  # Meaningful content
                # Limit to ~500 characters for storage
                return clean_paragraph[:500] + "..." if len(clean_paragraph) > 500 else clean_paragraph
        
        # Fallback: return first 500 characters of entire content
        return markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content
    
    def store_crawl_results(self, results: List[Dict[str, Any]]) -> int:
        """
        Store crawl results in Supabase pages table
        Table schema: id, url, content, created_at
        Uses the working pattern from asyncwebcrawler_advanced.py
        
        Args:
            results: List of crawl result dictionaries to store
            
        Returns:
            Number of successfully stored records
        """
        if not self.is_available:
            print("❌ Supabase client not available")
            return 0
        
        stored_count = 0
        
        for result in results:
            try:
                # Handle both dict and object access patterns
                url = result.get('url') if isinstance(result, dict) else getattr(result, 'url', None)
                raw_markdown = result.get('raw_markdown') if isinstance(result, dict) else getattr(result, 'raw_markdown', None)
                analysis = result.get('analysis') if isinstance(result, dict) else getattr(result, 'analysis', None)
                
                if not url or not raw_markdown:
                    print(f"⚠ Skipping result with missing url or content: {result}")
                    continue
                
                # Prepare data for storage - only use fields that exist in pages table
                # Extract first paragraph from markdown for concise storage
                first_paragraph = self._extract_first_paragraph(raw_markdown)
                data = {
                    'url': url,
                    'content': first_paragraph  # Store only first paragraph
                }
                
                # If we have LLM analysis, add title as a comment in content
                if analysis:
                    title = analysis.get('title', 'No title') if isinstance(analysis, dict) else getattr(analysis, 'title', 'No title')
                    summary = analysis.get('summary', 'No summary') if isinstance(analysis, dict) else getattr(analysis, 'summary', 'No summary')
                    
                    # Prepend analysis to content for storage
                    analysis_header = f"TITLE: {title}\nSUMMARY: {summary}\n\n"
                    data['content'] = analysis_header + data['content']
                
                # Insert into Testing table using official Supabase pattern
                # Source: https://supabase.com/docs/reference/python/initializing
                response = self.client.table('Testing').insert(data).execute()
                
                if response.data:
                    stored_count += 1
                    print(f"✓ Stored in Supabase: {result['url']}")
                else:
                    print(f"⚠ No data returned for: {result['url']}")
                    
            except Exception as e:
                print(f"✗ Failed to store {result['url']}: {str(e)}")
        
        print(f"🎯 Storage complete: {stored_count}/{len(results)} results stored")
        return stored_count
    
    def store_page_summary(self, url: str, title: str, summary: str, raw_markdown: str = None, content_hash: str = None):
        """
        Store page summary using official Supabase upsert pattern.
        Source: https://supabase.com/docs/reference/python/upsert
        
        Args:
            url: Page URL (used as unique identifier)
            title: Extracted page title
            summary: Extracted page summary
            raw_markdown: Optional raw markdown content
            content_hash: Optional content hash for deduplication
            
        Returns:
            Supabase response data or None if failed
        """
        if not self.is_available:
            print("❌ Supabase client not available")
            return None
        
        try:
            # Prepare data for upsert - following official pattern
            # Now we can store title and summary in their own columns
            data = {
                "url": url,
                "title": title,
                "summary": summary
            }
            
            # Add content as first paragraph if provided
            if raw_markdown:
                first_paragraph = self._extract_first_paragraph(raw_markdown)
                data["content"] = first_paragraph
            
            # Official Supabase upsert pattern
            # Source: https://supabase.com/docs/reference/python/upsert
            response = self.client.table("Testing").upsert(data).execute()
            
            if response.data:
                print(f"✓ Stored page summary: {url}")
                return response.data
            else:
                print(f"⚠ No data returned for: {url}")
                return None
                
        except Exception as e:
            print(f"✗ Failed to store page summary for {url}: {str(e)}")
            return None
    
    def check_connection(self) -> bool:
        """
        Test Supabase connection by querying the Testing table
        """
        if not self.is_available:
            return False
            
        try:
            # Test connection with a simple query
            response = self.client.table('Testing').select('id').limit(1).execute()
            print("✓ Supabase connection verified")
            return True
        except Exception as e:
            print(f"❌ Supabase connection failed: {str(e)}")
            return False