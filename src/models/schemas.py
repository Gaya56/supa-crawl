#!/usr/bin/env python3
"""
Pydantic Models for Data Validation
Following official documentation from:
- Crawl4AI: https://docs.crawl4ai.com/core/quickstart/#llm-extraction
- Inject_OpenAI_Analysis_duringCrawl.prompt.md specifications
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PageSummary(BaseModel):
    """
    Schema for LLM-powered content analysis - Official Crawl4AI pattern
    Source: Inject_OpenAI_Analysis_duringCrawl.prompt.md
    """
    title: str = Field(..., description="Page title")
    summary: str = Field(..., description="Brief summary of the page content")


class CrawlResult(BaseModel):
    """
    Standardized crawl result structure for consistent data handling
    Based on the working patterns from asyncwebcrawler_advanced.py
    """
    url: str = Field(..., description="The URL that was crawled")
    success: bool = Field(..., description="Whether the crawl was successful")
    raw_markdown: Optional[str] = Field(None, description="Raw markdown content")
    analysis: Optional[Dict[str, Any]] = Field(None, description="LLM analysis results")
    error_message: Optional[str] = Field(None, description="Error message if crawl failed")
    crawl_time: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp of crawl")
    status_code: Optional[int] = Field(None, description="HTTP status code")


class SupabaseRecord(BaseModel):
    """
    Model for Supabase database records
    Matches the pages table schema: id, url, content, created_at
    """
    url: str = Field(..., description="The crawled URL")
    content: str = Field(..., description="Page content including analysis")
    
    def to_supabase_dict(self) -> dict:
        """Convert to dictionary suitable for Supabase insertion"""
        return {
            "url": self.url,
            "content": self.content
        }