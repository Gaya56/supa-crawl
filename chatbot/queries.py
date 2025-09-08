#!/usr/bin/env python3
"""
Query helpers for the Supabase chatbot
Following official Supabase Python client documentation:
https://supabase.com/docs/reference/python/select
"""
import logging
from typing import List, Dict, Any, Optional
from supabase import Client

# Configure logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def latest_pages(supabase: Client, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch the latest pages from the database ordered by ID.
    
    Args:
        supabase: Supabase client instance
        limit: Number of results to return (default: 5)
        
    Returns:
        List of page dictionaries with url, title, summary
    """
    try:
        response = (
            supabase.table("pages")
            .select("id, url, title, summary")
            .order("id", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    except Exception as e:
        logger.error(f"Error fetching latest pages: {str(e)}", exc_info=True)
        print(f"❌ Error fetching latest pages: {str(e)}")
        return []


def find_page_by_url(supabase: Client, url: str) -> Optional[Dict[str, Any]]:
    """
    Find a page by its URL.
    
    Args:
        supabase: Supabase client instance
        url: URL to search for
        
    Returns:
        Page dictionary if found, None otherwise
    """
    try:
        response = (
            supabase.table("pages")
            .select("*")
            .eq("url", url)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error finding page by URL: {str(e)}", exc_info=True)
        print(f"❌ Error finding page by URL: {str(e)}")
        return None


def search_pages_by_title(supabase: Client, title_query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search pages by title using ilike (case-insensitive pattern matching).
    
    Args:
        supabase: Supabase client instance
        title_query: Title search query
        limit: Number of results to return (default: 10)
        
    Returns:
        List of page dictionaries matching the title query
    """
    try:
        response = (
            supabase.table("pages")
            .select("id, url, title, summary")
            .ilike("title", f"%{title_query}%")
            .order("id", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    except Exception as e:
        logger.error(f"Error searching pages by title: {str(e)}", exc_info=True)
        print(f"❌ Error searching pages by title: {str(e)}")
        return []


def search_pages_by_summary(supabase: Client, summary_query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search pages by summary content using ilike (case-insensitive pattern matching).
    
    Args:
        supabase: Supabase client instance
        summary_query: Summary search query
        limit: Number of results to return (default: 10)
        
    Returns:
        List of page dictionaries matching the summary query
    """
    try:
        response = (
            supabase.table("pages")
            .select("id, url, title, summary")
            .ilike("summary", f"%{summary_query}%")
            .order("id", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    except Exception as e:
        logger.error(f"Error searching pages by summary: {str(e)}", exc_info=True)
        print(f"❌ Error searching pages by summary: {str(e)}")
        return []


def count_total_pages(supabase: Client) -> int:
    """
    Get the total number of pages in the database.
    
    Args:
        supabase: Supabase client instance
        
    Returns:
        Total number of pages
    """
    try:
        response = (
            supabase.table("pages")
            .select("*", count="exact")
            .execute()
        )
        return response.count
    except Exception as e:
        logger.error(f"Error counting pages: {str(e)}", exc_info=True)
        print(f"❌ Error counting pages: {str(e)}")
        return 0


def get_pages_with_summaries(supabase: Client, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get pages that have both title and summary (non-null values).
    
    Args:
        supabase: Supabase client instance
        limit: Number of results to return (default: 10)
        
    Returns:
        List of page dictionaries with non-null title and summary
    """
    try:
        response = (
            supabase.table("pages")
            .select("id, url, title, summary")
            .not_.is_("title", "null")
            .not_.is_("summary", "null")
            .order("id", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    except Exception as e:
        logger.error(f"Error fetching pages with summaries: {str(e)}", exc_info=True)
        print(f"❌ Error fetching pages with summaries: {str(e)}")
        return []


def get_page_content(supabase: Client, page_id: int) -> Optional[Dict[str, Any]]:
    """
    Get the full content of a specific page by ID.
    
    Args:
        supabase: Supabase client instance
        page_id: The ID of the page to retrieve
        
    Returns:
        Page dictionary with full content if found, None otherwise
    """
    try:
        response = (
            supabase.table("pages")
            .select("*")
            .eq("id", page_id)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error fetching page content: {str(e)}", exc_info=True)
        print(f"❌ Error fetching page content: {str(e)}")
        return None


def format_page_result(page: Dict[str, Any], include_content: bool = False) -> str:
    """
    Format a page result for display in the terminal.
    
    Args:
        page: Page dictionary from database
        include_content: Whether to include the full content field
        
    Returns:
        Formatted string representation of the page
    """
    if not page:
        return "No page data"
    
    lines = []
    lines.append(f"📄 ID: {page.get('id', 'N/A')}")
    lines.append(f"🔗 URL: {page.get('url', 'N/A')}")
    
    title = page.get('title')
    if title:
        lines.append(f"📝 Title: {title}")
    
    summary = page.get('summary')
    if summary:
        lines.append(f"📖 Summary: {summary}")
    
    if include_content and page.get('content'):
        content = page.get('content', '')
        # For content command, show more content but still truncate very long content
        if len(content) > 2000:
            content = content[:2000] + "\n\n... [Content truncated. Use smaller queries or process content in chunks]"
        lines.append(f"📃 Content: {content}")
    
    return "\n".join(lines)


def format_pages_list(pages: List[Dict[str, Any]], include_content: bool = False) -> str:
    """
    Format a list of pages for display in the terminal.
    
    Args:
        pages: List of page dictionaries from database
        include_content: Whether to include the content field for each page
        
    Returns:
        Formatted string representation of all pages
    """
    if not pages:
        return "No pages found."
    
    formatted_pages = []
    for i, page in enumerate(pages, 1):
        formatted_pages.append(f"--- Page {i} ---")
        formatted_pages.append(format_page_result(page, include_content))
        formatted_pages.append("")  # Empty line for separation
    
    return "\n".join(formatted_pages)