from pydantic import BaseModel, Field


class PredictionMarketBet(BaseModel):
    """Schema for prediction market data extraction to match Testing table schema.
    Source: https://docs.crawl4ai.com/extraction/llm-strategies/
    Matches Testing table columns: source_url, website_name, bet_title, odds, summary
    """

    website_name: str = Field(
        description="Name of the prediction market site (e.g., Polymarket, Kalshi)"
    )
    bet_title: str = Field(description="Title of the prediction market or bet")
    odds: str = Field(description="Current odds or probability for this market")
    summary: str = Field(
        description="Brief description of what this market is predicting"
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
