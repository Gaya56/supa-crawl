# Prediction Market Implementation Guide

## Overview
This document details the implementation of live prediction market data extraction from current 2025 sources, replacing the previous general web crawler with a specialized prediction market scraper.

## Architecture Changes

### 1. Schema Implementation (`src/models/schemas.py`)

**Added PredictionMarketBet Schema:**
```python
class PredictionMarketBet(BaseModel):
    """
    Pydantic schema for prediction market bet extraction
    Matches Supabase Testing table structure for seamless storage
    """
    website_name: str = Field(..., description="Name of the prediction market website")
    bet_title: str = Field(..., description="Title/description of the betting market")
    odds: str = Field(..., description="Current odds or probability (e.g., '52% Yes', '1.85')")
    summary: str = Field(..., description="Brief summary of what the market is predicting")
```

**Key Features:**
- Perfect field mapping to Supabase Testing table
- Validation for required fields
- Descriptive field documentation
- Preserves existing PageSummary schema for compatibility

### 2. Database Handler (`src/storage/supabase_handler.py`)

**Added Prediction Market Storage Method:**
```python
async def store_prediction_market_data(self, prediction_market: 'PredictionMarketBet', source_url: str) -> bool:
    """
    Store prediction market data in Supabase Testing table
    
    Args:
        prediction_market: PredictionMarketBet object with market data
        source_url: Source URL where data was extracted from
        
    Returns:
        bool: True if storage successful, False otherwise
    """
    if TYPE_CHECKING:
        from ..models.schemas import PredictionMarketBet
        
    try:
        # Insert data into Testing table with perfect field mapping
        result = self.client.table("Testing").insert({
            "source_url": source_url,
            "website_name": prediction_market.website_name,
            "bet_title": prediction_market.bet_title,
            "odds": prediction_market.odds,
            "summary": prediction_market.summary
        }).execute()
        
        if result.data:
            print(f"✓ Stored prediction market: {prediction_market.bet_title} from {prediction_market.website_name}")
            return True
        else:
            print(f"✗ Failed to store prediction market data for {source_url}")
            return False
            
    except Exception as e:
        print(f"✗ Error storing prediction market data: {str(e)}")
        return False
```

**Key Features:**
- Official Supabase insert pattern
- Perfect field mapping to Testing table schema
- Comprehensive error handling
- Success/failure logging
- TYPE_CHECKING import for development

### 3. Crawler Enhancement (`src/crawlers/async_crawler.py`)

**Added Prediction Market Extraction Methods:**

```python
async def crawl_prediction_markets_with_llm(self, urls: List[str]) -> List[Dict]:
    """
    Crawl prediction market websites with LLM-powered data extraction
    
    Args:
        urls: List of prediction market URLs to crawl
        
    Returns:
        List of dictionaries containing extracted prediction market data
    """
    print(f"🎲 Starting prediction market LLM crawl for {len(urls)} URLs")
    
    # Configure LLM extraction strategy for prediction markets
    extraction_strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",
        api_token=self.openai_api_key,
        schema=PredictionMarketBet.model_json_schema(),
        extraction_type="schema",
        apply_chunking=False,
        instruction="Extract all available prediction market data from this page. Include market titles, current odds/probabilities, and brief descriptions of what each market is predicting. Focus on active betting markets with current odds."
    )
    
    crawler_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS,
        js_code="""
        // Wait for dynamic content to load
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Scroll to load more content
        window.scrollTo(0, document.body.scrollHeight);
        await new Promise(resolve => setTimeout(resolve, 2000));
        """
    )
    
    results = []
    
    async with AsyncWebCrawler(verbose=True, config=self.config) as crawler:
        for url in urls:
            try:
                result = await crawler.arun(url=url, config=crawler_config)
                
                if result.success and result.extracted_content:
                    # Debug output for development
                    print(f"🔍 Raw LLM Response for {url}:")
                    print(f"   Length: {len(result.extracted_content)} chars")
                    print(f"   Content: {result.extracted_content[:500]}...")
                    
                    # Parse LLM response (handle both single objects and arrays)
                    try:
                        parsed_data = json.loads(result.extracted_content)
                        
                        # Handle array responses (LLM may return multiple markets)
                        if isinstance(parsed_data, list):
                            print(f"📊 LLM returned {len(parsed_data)} prediction markets")
                            for market_data in parsed_data:
                                if isinstance(market_data, dict) and not market_data.get('error', False):
                                    results.append({
                                        'url': url,
                                        'data': market_data,
                                        'success': True
                                    })
                        else:
                            # Handle single object response
                            if isinstance(parsed_data, dict) and not parsed_data.get('error', False):
                                results.append({
                                    'url': url,
                                    'data': parsed_data,
                                    'success': True
                                })
                    except json.JSONDecodeError as e:
                        print(f"✗ Failed to parse LLM response for {url}: {e}")
                        continue
                    
                    print(f"🎲 Prediction market data extracted for: {url}")
                else:
                    print(f"✗ Failed to extract prediction market data from {url}: {result.error_message}")
                    
            except Exception as e:
                print(f"✗ Failed to extract prediction market data from {url}: {str(e)}")
                continue
    
    return results

async def crawl_and_store_prediction_markets(self, urls: List[str]) -> bool:
    """
    Complete pipeline: crawl prediction markets and store in Supabase
    
    Args:
        urls: List of prediction market URLs to crawl and store
        
    Returns:
        bool: True if at least one market was successfully stored
    """
    print(f"🎲 Starting prediction market crawl and store workflow for {len(urls)} URLs")
    
    # Extract prediction market data
    extraction_results = await self.crawl_prediction_markets_with_llm(urls)
    
    if not extraction_results:
        print("❌ No prediction market data extracted")
        return False
    
    # Store results in Supabase
    storage_success_count = 0
    total_markets = len(extraction_results)
    
    for i, result in enumerate(extraction_results, 1):
        try:
            # Create PredictionMarketBet object
            market = PredictionMarketBet(**result['data'])
            
            # Store in Supabase
            success = await self.supabase_handler.store_prediction_market_data(market, result['url'])
            if success:
                storage_success_count += 1
                print(f"✓ Stored prediction market {i}: {market.bet_title} from {market.website_name}")
            
        except Exception as e:
            print(f"✗ Failed to store prediction market {i}: {str(e)}")
            continue
    
    print(f"🎯 Prediction market storage complete: {storage_success_count}/{total_markets} results stored")
    return storage_success_count > 0
```

**Key Features:**
- LLM-powered extraction using OpenAI GPT-4o-mini
- Schema-based validation with PredictionMarketBet
- Array response handling for multiple markets per page
- Dynamic content loading with JavaScript
- Comprehensive error handling and logging
- Debug output for development
- Complete storage pipeline integration

## Current Implementation Status

### ✅ Successfully Working
- **Polymarket.com** - World's largest prediction market
- **Live 2025 Data Extraction** - Current events and odds
- **Supabase Storage** - 13 markets stored successfully
- **LLM Processing** - GPT-4o-mini extraction working perfectly

### ⚠️ Partially Working
- **Manifold Markets** - Bot protection issues (`net::ERR_ABORTED`)

### 🔄 Ready to Test
- **ElectionBettingOdds.com** - Live odds aggregator
- **Kalshi.com** - Regulated prediction market
- **PredictIt.org** - Academic prediction market

## Current Live Data Examples

**Recent extraction from Polymarket (September 10, 2025):**

```json
{
    "website_name": "Polymarket",
    "bet_title": "Republican Presidential Nominee 2028",
    "odds": "52% Yes",
    "summary": "This market predicts whether J.D. Vance will win the 2028 Republican presidential nomination."
},
{
    "website_name": "Polymarket",
    "bet_title": "Will Trump release more Epstein files in 2025?",
    "odds": "52% chance Yes, 48% No",
    "summary": "This market predicts whether Trump will release more files related to Jeffrey Epstein in 2025."
},
{
    "website_name": "Polymarket",
    "bet_title": "US government shutdown in 2025?",
    "odds": "53% chance Yes, 47% No",
    "summary": "This market predicts the likelihood of a US government shutdown occurring in 2025."
}
```

## Technical Specifications

### Database Schema (Supabase Testing Table)
```sql
CREATE TABLE "Testing" (
    "id" SERIAL PRIMARY KEY,
    "timestamp" TIMESTAMPTZ DEFAULT NOW(),
    "source_url" TEXT NOT NULL,
    "website_name" TEXT NOT NULL,
    "bet_title" TEXT NOT NULL,
    "odds" TEXT NOT NULL,
    "summary" TEXT NOT NULL
);
```

### Dependencies
- **Crawl4AI v0.7.x** - Web crawling with LLM extraction
- **OpenAI GPT-4o-mini** - Structured data extraction
- **Supabase Python Client** - Database operations
- **Pydantic** - Data validation and schemas

### Configuration Requirements
```python
# Environment variables needed:
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Next Steps

1. **Dashboard Integration** - Find aggregator sites with comprehensive odds displays
2. **Enhanced Stealth** - Implement additional bot detection bypass measures
3. **Multi-source Aggregation** - Combine data from multiple prediction markets
4. **Real-time Monitoring** - Set up automated periodic data collection
5. **Category Expansion** - Add sports, crypto, tech, and other prediction categories

## Usage Examples

### Basic Prediction Market Crawl
```python
from src.crawlers.async_crawler import AdvancedWebCrawler

crawler = AdvancedWebCrawler()
urls = ["https://polymarket.com/", "https://manifold.markets/"]

# Extract and store prediction market data
success = await crawler.crawl_and_store_prediction_markets(urls)
print(f"Storage success: {success}")
```

### Test Current Implementation
```python
# Run the complete test suite
python main.py
```

This implementation successfully converts the general web crawler into a specialized prediction market scraper with live 2025 data extraction capabilities.
