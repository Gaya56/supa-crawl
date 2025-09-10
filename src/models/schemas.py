from pydantic import BaseModel, Field
from typing import Optional


class PredictionMarketBet(BaseModel):
    """Enhanced schema for prediction market data extraction to match improved Testing table.
    Source: https://docs.crawl4ai.com/extraction/llm-strategies/
    
    Matches all Testing table columns including new descriptive fields:
    - Basic fields: website_name, bet_title, odds, summary
    - Enhanced fields: market_category, betting_options, probability_percentage, volume_info, closing_date
    """

    website_name: str = Field(
        description="Name of the prediction market site (e.g., Polymarket, Kalshi, OddsChecker)"
    )
    bet_title: str = Field(
        description="Clear title or question of the prediction market"
    )
    odds: str = Field(
        description="Raw odds/prices as displayed (e.g., 'Yes: 65% | No: 35%', '$1.20 / $0.80', '2.5 to 1')"
    )
    summary: str = Field(
        description="Brief description of what this market is predicting"
    )
    market_category: Optional[str] = Field(
        default=None,
        description="Category like Politics, Sports, Economics, Tech, Entertainment, etc."
    )
    betting_options: Optional[str] = Field(
        default=None,
        description="Available betting choices (e.g., 'Yes/No', 'Up/Down', 'Team A vs Team B', candidate names)"
    )
    probability_percentage: Optional[float] = Field(
        default=None,
        description="Implied probability as percentage (0-100) based on odds"
    )
    volume_info: Optional[str] = Field(
        default=None,
        description="Trading volume, liquidity, market size, or participation metrics"
    )
    closing_date: Optional[str] = Field(
        default=None,
        description="When the market closes, resolves, or event occurs (as readable text)"
    )


class PageSummary(BaseModel):
    """Legacy schema for general web crawling (kept for compatibility)
    Source: https://docs.crawl4ai.com/extraction/llm-strategies/
    Note: url is metadata from crawler, not extracted content
    """

    title: str = Field(description="The main title of the web page")
    summary: str = Field(description="A short paragraph summary of the page content")


class CrawlResult(BaseModel):
    page: PageSummary
    extracted_content: str


class Crawl4AIResponse(BaseModel):
    results: list[CrawlResult]


# Example usage:
# response = Crawl4AIResponse(results=[
#     CrawlResult(page=PageSummary(title="Example Title", summary="This is a short summary.", url="https://example.com"), extracted_content="Full content of the page")
# ])
