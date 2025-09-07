from pydantic import BaseModel, Field

class PageSummary(BaseModel):
    """Schema for LLM extraction following official Crawl4AI pattern.
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
