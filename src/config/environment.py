#!/usr/bin/env python3
"""
Environment Configuration for AsyncWebCrawler
Following official documentation from:
- Crawl4AI: https://docs.crawl4ai.com/core/browser-crawler-config/
- Supabase: https://supabase.com/docs/reference/python/initializing
"""
import os
from typing import Optional
from dotenv import load_dotenv
from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode

# Load environment variables from .env file
load_dotenv()


class EnvironmentConfig:
    """
    Centralized environment configuration class
    Extracts all required environment variables from /workspaces/codespaces-blank/.env
    """
    
    def __init__(self):
        # Supabase configuration from .env - Official pattern
        # Source: https://supabase.com/docs/reference/python/initializing
        self.supabase_url: Optional[str] = os.environ.get("SUPABASE_URL")
        self.supabase_key: Optional[str] = os.environ.get("SUPABASE_KEY") 
        
        # OpenAI configuration from .env
        self.openai_api_key: Optional[str] = os.environ.get("OPENAI_API_KEY")
        
        # Validate critical environment variables
        self._validate_environment()
    
    def _validate_environment(self) -> None:
        """Validate that required environment variables are present"""
        missing_vars = []
        
        if not self.supabase_url:
            missing_vars.append("SUPABASE_URL")
        if not self.supabase_key:
            missing_vars.append("SUPABASE_KEY")
        if not self.openai_api_key:
            missing_vars.append("OPENAI_API_KEY")
            
        if missing_vars:
            print(f"⚠ Warning: Missing environment variables: {', '.join(missing_vars)}")
            print("Some features may not work properly.")
    
    @property
    def has_supabase_config(self) -> bool:
        """Check if Supabase configuration is complete"""
        return bool(self.supabase_url and self.supabase_key)
    
    @property
    def has_openai_config(self) -> bool:
        """Check if OpenAI configuration is complete"""
        return bool(self.openai_api_key)


class CrawlerConfig:
    """
    Crawler configuration factory following official Crawl4AI patterns
    Source: https://docs.crawl4ai.com/core/browser-crawler-config/
    """
    
    @staticmethod
    def create_browser_config(headless: bool = True, verbose: bool = False) -> BrowserConfig:
        """
        Create browser configuration for stealth crawling
        Source: https://docs.crawl4ai.com/advanced/undetected-browser/
        """
        return BrowserConfig(
            headless=headless,              # Can be False for better stealth but requires display
            verbose=verbose,                # Reduce logging noise
            browser_type="chromium",        # Default browser type
            use_managed_browser=True,       # Use Crawl4AI's managed browser instance
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    
    @staticmethod
    def create_crawler_run_config() -> CrawlerRunConfig:
        """
        Create crawler run configuration with optimal defaults
        Source: https://docs.crawl4ai.com/api/parameters/
        """
        return CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,        # Always fetch fresh content
            word_count_threshold=1,             # Don't filter out short pages
            extraction_strategy=None,           # Can be set later for LLM extraction
            chunking_strategy=None              # Default chunking
        )


# Global configuration instances
env_config = EnvironmentConfig()
crawler_config = CrawlerConfig()