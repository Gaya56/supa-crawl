# 🔧 Advanced Usage Guide

## Advanced Crawling Strategies

This guide covers advanced usage patterns, optimization techniques, and enterprise-level features of the AsyncWebCrawler Advanced Implementation.

## Table of Contents
- [Advanced Dispatcher Strategies](#advanced-dispatcher-strategies)
- [Custom LLM Integration](#custom-llm-integration)
- [Performance Optimization](#performance-optimization)
- [Error Handling & Resilience](#error-handling--resilience)
- [Monitoring & Analytics](#monitoring--analytics)
- [Scaling Strategies](#scaling-strategies)

## Advanced Dispatcher Strategies

### Memory Adaptive Dispatcher

The Memory Adaptive Dispatcher dynamically adjusts concurrency based on system resources.

```python
async def adaptive_crawling_with_monitoring():
    crawler = AdvancedWebCrawler()
    
    # Large URL list for testing adaptive behavior
    urls = [
        "https://docs.crawl4ai.com/",
        "https://docs.crawl4ai.com/introduction/",
        "https://docs.crawl4ai.com/api/parameters/",
        "https://docs.crawl4ai.com/examples/",
        "https://docs.crawl4ai.com/advanced-usage/",
    ] * 5  # 25 URLs total
    
    start_time = time.time()
    results = await crawler.crawl_with_memory_adaptive_dispatcher(urls)
    end_time = time.time()
    
    # Analysis
    successful_crawls = sum(1 for r in results if r.success)
    total_content = sum(len(r.content) for r in results if r.success)
    
    print(f"📊 Adaptive Dispatcher Results:")
    print(f"   ✅ Success Rate: {successful_crawls}/{len(urls)} ({successful_crawls/len(urls)*100:.1f}%)")
    print(f"   📄 Total Content: {total_content:,} characters")
    print(f"   ⏱️ Total Time: {end_time - start_time:.2f} seconds")
    print(f"   🚀 Throughput: {len(urls)/(end_time - start_time):.2f} URLs/second")

asyncio.run(adaptive_crawling_with_monitoring())
```

**When to Use:**
- Variable content sizes (some pages are small, others are large)
- Unknown target website performance
- Dynamic resource availability
- Mixed content types (text, images, media)

### Semaphore Dispatcher with Custom Limits

```python
class CustomCrawler(AdvancedWebCrawler):
    async def crawl_with_custom_semaphore(self, urls: List[str], concurrency: int = 10):
        """Custom semaphore dispatcher with configurable concurrency."""
        async with AsyncWebCrawler(
            config=CrawlerConfig.create_browser_config()
        ) as crawler:
            # Custom semaphore
            semaphore = asyncio.Semaphore(concurrency)
            
            async def crawl_single_with_semaphore(url: str) -> CrawlResult:
                async with semaphore:
                    try:
                        result = await crawler.arun(
                            url=url,
                            config=CrawlerConfig.create_crawler_run_config()
                        )
                        return CrawlResult(
                            url=url,
                            content=result.markdown,
                            timestamp=datetime.now(),
                            success=True
                        )
                    except Exception as e:
                        return CrawlResult(
                            url=url,
                            content="",
                            timestamp=datetime.now(),
                            success=False,
                            error=str(e)
                        )
            
            # Execute with custom concurrency
            tasks = [crawl_single_with_semaphore(url) for url in urls]
            return await asyncio.gather(*tasks)

# Usage
async def high_concurrency_crawling():
    crawler = CustomCrawler()
    
    urls = ["https://example.com"] * 50  # 50 URLs
    
    # Test different concurrency levels
    for concurrency in [5, 10, 20]:
        start_time = time.time()
        results = await crawler.crawl_with_custom_semaphore(urls, concurrency)
        end_time = time.time()
        
        success_rate = sum(1 for r in results if r.success) / len(results)
        
        print(f"Concurrency {concurrency}: {end_time-start_time:.2f}s, Success: {success_rate:.1%}")

asyncio.run(high_concurrency_crawling())
```

## Custom LLM Integration

### Advanced LLM Strategies

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.config import LLMConfig

class AdvancedLLMAnalyzer:
    def __init__(self):
        self.strategies = {
            "summary": self._create_summary_strategy(),
            "technical": self._create_technical_strategy(),
            "sentiment": self._create_sentiment_strategy(),
            "entities": self._create_entity_strategy()
        }
    
    def _create_summary_strategy(self):
        return LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider="openai/gpt-4o",
                api_token=os.getenv("OPENAI_API_KEY")
            ),
            schema=PageSummary.model_json_schema(),
            instruction="""
            Analyze this webpage and provide:
            1. A concise title (max 100 chars)
            2. A comprehensive summary (200-500 words)
            3. Key topics covered
            4. Target audience
            5. Content quality assessment (1-10)
            """
        )
    
    def _create_technical_strategy(self):
        return LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider="openai/gpt-4o",
                api_token=os.getenv("OPENAI_API_KEY"),
                extra_args={"temperature": 0}  # Deterministic for technical content
            ),
            schema=TechnicalAnalysis.model_json_schema(),
            instruction="""
            Extract technical information:
            1. Programming languages mentioned
            2. Frameworks and libraries
            3. API endpoints and methods
            4. Code examples (if any)
            5. Technical difficulty level (beginner/intermediate/advanced)
            """
        )
    
    async def analyze_with_strategy(self, url: str, strategy_name: str):
        """Analyze URL with specific strategy."""
        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        strategy = self.strategies[strategy_name]
        
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
                config=CrawlerRunConfig(
                    extraction_strategy=strategy
                )
            )
            
            return {
                "url": url,
                "analysis": result.extracted_content,
                "raw_content": result.markdown
            }

# Usage Example
async def multi_strategy_analysis():
    analyzer = AdvancedLLMAnalyzer()
    
    url = "https://docs.crawl4ai.com/api/parameters/"
    
    # Analyze with different strategies
    for strategy in ["summary", "technical"]:
        result = await analyzer.analyze_with_strategy(url, strategy)
        print(f"\n{strategy.upper()} ANALYSIS:")
        print(f"Analysis: {result['analysis']}")
        print("-" * 50)

asyncio.run(multi_strategy_analysis())
```

### Custom Pydantic Schemas

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ContentType(str, Enum):
    ARTICLE = "article"
    DOCUMENTATION = "documentation"
    NEWS = "news"
    PRODUCT = "product"
    BLOG = "blog"
    FORUM = "forum"

class TechnicalAnalysis(BaseModel):
    programming_languages: List[str] = Field(default=[], description="Programming languages mentioned")
    frameworks: List[str] = Field(default=[], description="Frameworks and libraries mentioned")
    apis: List[str] = Field(default=[], description="API endpoints or methods mentioned")
    difficulty_level: str = Field(..., description="Technical difficulty: beginner, intermediate, or advanced")
    code_examples: bool = Field(..., description="Whether the page contains code examples")
    
class ContentAnalysis(BaseModel):
    title: str = Field(..., description="Page title")
    content_type: ContentType = Field(..., description="Type of content")
    word_count: int = Field(..., description="Estimated word count")
    reading_time: int = Field(..., description="Estimated reading time in minutes")
    key_topics: List[str] = Field(..., description="Main topics covered")
    target_audience: str = Field(..., description="Intended audience")
    quality_score: int = Field(..., ge=1, le=10, description="Content quality score (1-10)")
    
class SentimentAnalysis(BaseModel):
    overall_sentiment: str = Field(..., description="positive, negative, or neutral")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    emotional_tone: List[str] = Field(..., description="Emotional tones detected")
    
class EntityExtraction(BaseModel):
    organizations: List[str] = Field(default=[], description="Organizations mentioned")
    people: List[str] = Field(default=[], description="People mentioned")
    locations: List[str] = Field(default=[], description="Locations mentioned")
    technologies: List[str] = Field(default=[], description="Technologies mentioned")
    dates: List[str] = Field(default=[], description="Important dates mentioned")
```

## Performance Optimization

### Connection Pooling and Reuse

```python
class OptimizedCrawler:
    def __init__(self):
        self.browser_pool = None
        self.max_browsers = 3
        
    async def initialize_browser_pool(self):
        """Initialize a pool of browser instances."""
        self.browser_pool = []
        for _ in range(self.max_browsers):
            browser = AsyncWebCrawler(
                config=CrawlerConfig.create_browser_config()
            )
            await browser.astart()
            self.browser_pool.append(browser)
    
    async def get_browser(self):
        """Get available browser from pool."""
        while not self.browser_pool:
            await asyncio.sleep(0.1)  # Wait for available browser
        
        return self.browser_pool.pop()
    
    async def return_browser(self, browser):
        """Return browser to pool."""
        self.browser_pool.append(browser)
    
    async def optimized_crawl(self, urls: List[str]) -> List[CrawlResult]:
        """Crawl using browser pool for optimal performance."""
        if not self.browser_pool:
            await self.initialize_browser_pool()
        
        async def crawl_with_pooled_browser(url: str):
            browser = await self.get_browser()
            try:
                result = await browser.arun(
                    url=url,
                    config=CrawlerConfig.create_crawler_run_config()
                )
                return CrawlResult(
                    url=url,
                    content=result.markdown,
                    timestamp=datetime.now(),
                    success=True
                )
            finally:
                await self.return_browser(browser)
        
        tasks = [crawl_with_pooled_browser(url) for url in urls]
        return await asyncio.gather(*tasks)
    
    async def cleanup(self):
        """Clean up browser pool."""
        for browser in self.browser_pool:
            await browser.aclose()

# Usage
async def optimized_crawling():
    crawler = OptimizedCrawler()
    
    urls = ["https://example.com"] * 20
    
    try:
        results = await crawler.optimized_crawl(urls)
        print(f"Crawled {len(results)} URLs with browser pooling")
    finally:
        await crawler.cleanup()

asyncio.run(optimized_crawling())
```

### Caching Strategies

```python
import hashlib
import json
from typing import Dict, Any

class CacheManager:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache = {}
        self.max_memory_items = 1000
    
    def _get_cache_key(self, url: str, config: Dict[str, Any] = None) -> str:
        """Generate cache key from URL and configuration."""
        cache_data = {"url": url}
        if config:
            cache_data.update(config)
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    async def get_cached_result(self, url: str, config: Dict[str, Any] = None) -> Optional[CrawlResult]:
        """Get cached crawl result."""
        cache_key = self._get_cache_key(url, config)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                result = CrawlResult(**data)
                
                # Add to memory cache
                if len(self.memory_cache) < self.max_memory_items:
                    self.memory_cache[cache_key] = result
                
                return result
            except Exception:
                # Invalid cache file, remove it
                cache_file.unlink()
        
        return None
    
    async def cache_result(self, result: CrawlResult, config: Dict[str, Any] = None):
        """Cache crawl result."""
        cache_key = self._get_cache_key(result.url, config)
        
        # Memory cache
        if len(self.memory_cache) < self.max_memory_items:
            self.memory_cache[cache_key] = result
        
        # Disk cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump(result.dict(), f, default=str)

class CachedCrawler(AdvancedWebCrawler):
    def __init__(self):
        super().__init__()
        self.cache = CacheManager()
    
    async def crawl_with_cache(self, urls: List[str]) -> List[CrawlResult]:
        """Crawl with caching support."""
        results = []
        
        for url in urls:
            # Check cache first
            cached_result = await self.cache.get_cached_result(url)
            if cached_result:
                print(f"📁 Cache hit for {url}")
                results.append(cached_result)
                continue
            
            # Not in cache, crawl it
            print(f"🌐 Crawling {url}")
            try:
                async with AsyncWebCrawler() as crawler:
                    result_data = await crawler.arun(url=url)
                    
                    result = CrawlResult(
                        url=url,
                        content=result_data.markdown,
                        timestamp=datetime.now(),
                        success=True
                    )
                    
                    # Cache the result
                    await self.cache.cache_result(result)
                    results.append(result)
                    
            except Exception as e:
                result = CrawlResult(
                    url=url,
                    content="",
                    timestamp=datetime.now(),
                    success=False
                )
                results.append(result)
        
        return results

# Usage
async def cached_crawling():
    crawler = CachedCrawler()
    
    urls = [
        "https://docs.crawl4ai.com/",
        "https://example.com"
    ]
    
    # First run - will crawl and cache
    print("First run:")
    results1 = await crawler.crawl_with_cache(urls)
    
    # Second run - will use cache
    print("\nSecond run:")
    results2 = await crawler.crawl_with_cache(urls)

asyncio.run(cached_crawling())
```

## Error Handling & Resilience

### Comprehensive Error Handling

```python
import traceback
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Callable

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CrawlError:
    url: str
    error_type: str
    message: str
    severity: ErrorSeverity
    timestamp: datetime
    traceback: Optional[str] = None
    retry_count: int = 0

class ResilientCrawler:
    def __init__(self):
        self.max_retries = 3
        self.retry_delays = [1, 2, 4]  # Exponential backoff
        self.error_handlers = {
            "network": self._handle_network_error,
            "timeout": self._handle_timeout_error,
            "parsing": self._handle_parsing_error,
            "rate_limit": self._handle_rate_limit_error
        }
        self.error_log = []
    
    async def _classify_error(self, error: Exception, url: str) -> CrawlError:
        """Classify error type and severity."""
        error_type = type(error).__name__
        message = str(error)
        
        # Network-related errors
        if "connection" in message.lower() or "network" in message.lower():
            return CrawlError(
                url=url,
                error_type="network",
                message=message,
                severity=ErrorSeverity.MEDIUM,
                timestamp=datetime.now(),
                traceback=traceback.format_exc()
            )
        
        # Timeout errors
        elif "timeout" in message.lower():
            return CrawlError(
                url=url,
                error_type="timeout",
                message=message,
                severity=ErrorSeverity.LOW,
                timestamp=datetime.now()
            )
        
        # Rate limiting
        elif "rate limit" in message.lower() or "429" in message:
            return CrawlError(
                url=url,
                error_type="rate_limit",
                message=message,
                severity=ErrorSeverity.HIGH,
                timestamp=datetime.now()
            )
        
        # Generic error
        else:
            return CrawlError(
                url=url,
                error_type="generic",
                message=message,
                severity=ErrorSeverity.MEDIUM,
                timestamp=datetime.now(),
                traceback=traceback.format_exc()
            )
    
    async def _handle_network_error(self, error: CrawlError) -> bool:
        """Handle network-related errors."""
        if error.retry_count < self.max_retries:
            delay = self.retry_delays[min(error.retry_count, len(self.retry_delays) - 1)]
            print(f"🔄 Network error for {error.url}, retrying in {delay}s...")
            await asyncio.sleep(delay)
            return True  # Retry
        return False  # Give up
    
    async def _handle_timeout_error(self, error: CrawlError) -> bool:
        """Handle timeout errors."""
        if error.retry_count < self.max_retries:
            delay = self.retry_delays[min(error.retry_count, len(self.retry_delays) - 1)]
            print(f"⏱️ Timeout for {error.url}, retrying in {delay}s...")
            await asyncio.sleep(delay)
            return True
        return False
    
    async def _handle_rate_limit_error(self, error: CrawlError) -> bool:
        """Handle rate limiting."""
        # Longer delay for rate limiting
        delay = 60  # 1 minute
        print(f"🚦 Rate limited for {error.url}, waiting {delay}s...")
        await asyncio.sleep(delay)
        return True if error.retry_count < 2 else False
    
    async def _handle_parsing_error(self, error: CrawlError) -> bool:
        """Handle parsing errors."""
        # Parsing errors usually don't benefit from retries
        print(f"📝 Parsing error for {error.url}: {error.message}")
        return False
    
    async def resilient_crawl_single(self, url: str) -> CrawlResult:
        """Crawl single URL with error handling and retries."""
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(
                        url=url,
                        config=CrawlerConfig.create_crawler_run_config()
                    )
                    
                    return CrawlResult(
                        url=url,
                        content=result.markdown,
                        timestamp=datetime.now(),
                        success=True
                    )
                    
            except Exception as e:
                error = await self._classify_error(e, url)
                error.retry_count = retry_count
                self.error_log.append(error)
                
                # Try to handle the error
                if error.error_type in self.error_handlers:
                    should_retry = await self.error_handlers[error.error_type](error)
                    if should_retry:
                        retry_count += 1
                        continue
                
                # Error not handled or retry limit reached
                print(f"❌ Failed to crawl {url} after {retry_count} retries: {error.message}")
                return CrawlResult(
                    url=url,
                    content="",
                    timestamp=datetime.now(),
                    success=False
                )
        
        # Should not reach here
        return CrawlResult(
            url=url,
            content="",
            timestamp=datetime.now(),
            success=False
        )
    
    async def resilient_crawl(self, urls: List[str]) -> List[CrawlResult]:
        """Crawl multiple URLs with resilience."""
        tasks = [self.resilient_crawl_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Unexpected exception during task execution
                processed_results.append(CrawlResult(
                    url=urls[i],
                    content="",
                    timestamp=datetime.now(),
                    success=False
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered."""
        if not self.error_log:
            return {"total_errors": 0}
        
        error_types = {}
        severity_counts = {}
        
        for error in self.error_log:
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        
        return {
            "total_errors": len(self.error_log),
            "error_types": error_types,
            "severity_distribution": severity_counts,
            "most_recent_errors": [
                {"url": e.url, "type": e.error_type, "message": e.message}
                for e in self.error_log[-5:]  # Last 5 errors
            ]
        }

# Usage
async def resilient_crawling():
    crawler = ResilientCrawler()
    
    # Mix of good and problematic URLs
    urls = [
        "https://docs.crawl4ai.com/",
        "https://httpstat.us/500",  # Will return 500 error
        "https://httpstat.us/404",  # Will return 404 error
        "https://example.com",
        "https://nonexistent-domain-12345.com"  # DNS error
    ]
    
    results = await crawler.resilient_crawl(urls)
    
    # Show results
    successful = sum(1 for r in results if r.success)
    print(f"\n📊 Crawl Results: {successful}/{len(results)} successful")
    
    # Show error summary
    error_summary = crawler.get_error_summary()
    if error_summary["total_errors"] > 0:
        print(f"\n❌ Error Summary:")
        print(f"   Total Errors: {error_summary['total_errors']}")
        print(f"   Error Types: {error_summary['error_types']}")
        print(f"   Severity Distribution: {error_summary['severity_distribution']}")

asyncio.run(resilient_crawling())
```

## Monitoring & Analytics

### Performance Monitoring

```python
import psutil
import time
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class PerformanceMetrics:
    start_time: float
    end_time: float = 0
    urls_processed: int = 0
    successful_crawls: int = 0
    failed_crawls: int = 0
    total_content_size: int = 0
    memory_usage_mb: float = 0
    cpu_usage_percent: float = 0
    response_times: List[float] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def success_rate(self) -> float:
        if self.urls_processed == 0:
            return 0
        return self.successful_crawls / self.urls_processed
    
    @property
    def throughput(self) -> float:
        if self.duration == 0:
            return 0
        return self.urls_processed / self.duration
    
    @property
    def average_response_time(self) -> float:
        if not self.response_times:
            return 0
        return sum(self.response_times) / len(self.response_times)

class MonitoredCrawler:
    def __init__(self):
        self.metrics = None
        self.process = psutil.Process()
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Get current system resource usage."""
        return {
            "memory_mb": self.process.memory_info().rss / 1024 / 1024,
            "cpu_percent": self.process.cpu_percent()
        }
    
    async def monitored_crawl(self, urls: List[str]) -> Tuple[List[CrawlResult], PerformanceMetrics]:
        """Crawl URLs with comprehensive monitoring."""
        self.metrics = PerformanceMetrics(start_time=time.time())
        
        results = []
        
        for url in urls:
            url_start_time = time.time()
            
            try:
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(
                        url=url,
                        config=CrawlerConfig.create_crawler_run_config()
                    )
                    
                    crawl_result = CrawlResult(
                        url=url,
                        content=result.markdown,
                        timestamp=datetime.now(),
                        success=True
                    )
                    
                    self.metrics.successful_crawls += 1
                    self.metrics.total_content_size += len(result.markdown)
                    
            except Exception as e:
                crawl_result = CrawlResult(
                    url=url,
                    content="",
                    timestamp=datetime.now(),
                    success=False
                )
                self.metrics.failed_crawls += 1
            
            # Record response time
            response_time = time.time() - url_start_time
            self.metrics.response_times.append(response_time)
            
            results.append(crawl_result)
            self.metrics.urls_processed += 1
            
            # Update system metrics
            sys_metrics = self._get_system_metrics()
            self.metrics.memory_usage_mb = max(self.metrics.memory_usage_mb, sys_metrics["memory_mb"])
            self.metrics.cpu_usage_percent = max(self.metrics.cpu_usage_percent, sys_metrics["cpu_percent"])
        
        self.metrics.end_time = time.time()
        
        return results, self.metrics
    
    def print_performance_report(self, metrics: PerformanceMetrics):
        """Print detailed performance report."""
        print("\n📊 PERFORMANCE REPORT")
        print("=" * 50)
        print(f"⏱️  Duration: {metrics.duration:.2f} seconds")
        print(f"📈 Throughput: {metrics.throughput:.2f} URLs/second")
        print(f"✅ Success Rate: {metrics.success_rate:.1%} ({metrics.successful_crawls}/{metrics.urls_processed})")
        print(f"📄 Total Content: {metrics.total_content_size:,} characters")
        print(f"🧠 Peak Memory: {metrics.memory_usage_mb:.1f} MB")
        print(f"⚡ Peak CPU: {metrics.cpu_usage_percent:.1f}%")
        print(f"⏱️  Avg Response Time: {metrics.average_response_time:.2f} seconds")
        print(f"📊 Response Time Range: {min(metrics.response_times):.2f}s - {max(metrics.response_times):.2f}s")

# Usage
async def monitored_crawling():
    crawler = MonitoredCrawler()
    
    urls = [
        "https://docs.crawl4ai.com/",
        "https://docs.crawl4ai.com/introduction/",
        "https://docs.crawl4ai.com/api/parameters/",
        "https://example.com"
    ]
    
    results, metrics = await crawler.monitored_crawl(urls)
    crawler.print_performance_report(metrics)

asyncio.run(monitored_crawling())
```

## Scaling Strategies

### Distributed Crawling with Queue System

```python
import asyncio
import aioredis
from typing import Optional

class DistributedCrawler:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.worker_id = f"worker_{os.getpid()}_{int(time.time())}"
    
    async def connect_redis(self):
        """Connect to Redis for queue management."""
        self.redis = await aioredis.from_url(self.redis_url)
    
    async def add_urls_to_queue(self, urls: List[str], queue_name: str = "crawl_queue"):
        """Add URLs to the crawling queue."""
        if not self.redis:
            await self.connect_redis()
        
        for url in urls:
            await self.redis.lpush(queue_name, url)
        
        print(f"📤 Added {len(urls)} URLs to queue '{queue_name}'")
    
    async def get_url_from_queue(self, queue_name: str = "crawl_queue", timeout: int = 10) -> Optional[str]:
        """Get next URL from queue (blocking)."""
        if not self.redis:
            await self.connect_redis()
        
        result = await self.redis.brpop(queue_name, timeout=timeout)
        if result:
            return result[1].decode('utf-8')
        return None
    
    async def distributed_worker(self, queue_name: str = "crawl_queue", batch_size: int = 5):
        """Worker that processes URLs from queue."""
        print(f"🚀 Worker {self.worker_id} started")
        
        while True:
            # Get batch of URLs
            urls = []
            for _ in range(batch_size):
                url = await self.get_url_from_queue(queue_name, timeout=5)
                if url:
                    urls.append(url)
                else:
                    break  # No more URLs available
            
            if not urls:
                print(f"⏸️  Worker {self.worker_id} waiting for URLs...")
                await asyncio.sleep(5)
                continue
            
            print(f"🔄 Worker {self.worker_id} processing {len(urls)} URLs")
            
            # Process URLs
            crawler = AdvancedWebCrawler()
            results = await crawler.crawl_with_memory_adaptive_dispatcher(urls)
            
            # Store results
            if any(r.success for r in results):
                success = await crawler.crawl_and_store_in_supabase([r.url for r in results if r.success])
                if success:
                    print(f"✅ Worker {self.worker_id} stored {sum(1 for r in results if r.success)} results")
    
    async def start_distributed_crawl(self, urls: List[str], num_workers: int = 3):
        """Start distributed crawling with multiple workers."""
        # Add URLs to queue
        await self.add_urls_to_queue(urls)
        
        # Start workers
        tasks = []
        for i in range(num_workers):
            task = asyncio.create_task(self.distributed_worker())
            tasks.append(task)
        
        print(f"🌐 Started {num_workers} distributed workers")
        
        try:
            # Run workers
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n🛑 Stopping distributed crawl...")
            for task in tasks:
                task.cancel()

# Usage
async def distributed_crawling():
    crawler = DistributedCrawler()
    
    # Large URL list for distributed processing
    urls = [
        f"https://docs.crawl4ai.com/page-{i}/"
        for i in range(100)  # 100 URLs
    ]
    
    await crawler.start_distributed_crawl(urls, num_workers=5)

# Run in separate processes/containers
# asyncio.run(distributed_crawling())
```

### Auto-scaling Based on Queue Size

```python
class AutoScalingCrawler:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.workers = []
        self.max_workers = 10
        self.min_workers = 2
        self.scale_up_threshold = 50  # URLs in queue
        self.scale_down_threshold = 5
    
    async def get_queue_size(self, queue_name: str = "crawl_queue") -> int:
        """Get current queue size."""
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url)
        
        return await self.redis.llen(queue_name)
    
    async def scale_workers(self, queue_name: str = "crawl_queue"):
        """Auto-scale workers based on queue size."""
        queue_size = await self.get_queue_size(queue_name)
        current_workers = len(self.workers)
        
        if queue_size > self.scale_up_threshold and current_workers < self.max_workers:
            # Scale up
            new_workers = min(
                self.max_workers - current_workers,
                queue_size // 10  # One worker per 10 URLs
            )
            
            for _ in range(new_workers):
                worker = DistributedCrawler()
                worker_task = asyncio.create_task(worker.distributed_worker(queue_name))
                self.workers.append(worker_task)
            
            print(f"📈 Scaled up: +{new_workers} workers (total: {len(self.workers)})")
        
        elif queue_size < self.scale_down_threshold and current_workers > self.min_workers:
            # Scale down
            workers_to_remove = min(
                current_workers - self.min_workers,
                (self.min_workers - queue_size) if queue_size < self.min_workers else 1
            )
            
            for _ in range(workers_to_remove):
                if self.workers:
                    worker_task = self.workers.pop()
                    worker_task.cancel()
            
            print(f"📉 Scaled down: -{workers_to_remove} workers (total: {len(self.workers)})")
    
    async def auto_scaling_crawl(self, urls: List[str]):
        """Run auto-scaling distributed crawl."""
        # Initialize with minimum workers
        for _ in range(self.min_workers):
            worker = DistributedCrawler()
            worker_task = asyncio.create_task(worker.distributed_worker())
            self.workers.append(worker_task)
        
        # Add URLs to queue
        crawler = DistributedCrawler()
        await crawler.add_urls_to_queue(urls)
        
        print(f"🚀 Started auto-scaling crawl with {len(urls)} URLs")
        
        # Monitor and scale
        try:
            while True:
                await self.scale_workers()
                
                # Check if all URLs are processed
                queue_size = await self.get_queue_size()
                if queue_size == 0 and len(self.workers) <= self.min_workers:
                    print("✅ All URLs processed")
                    break
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping auto-scaling crawl...")
        finally:
            # Clean up workers
            for worker_task in self.workers:
                worker_task.cancel()

# Usage
async def auto_scaling_demo():
    crawler = AutoScalingCrawler()
    
    # Large dataset
    urls = [f"https://example.com/page-{i}/" for i in range(500)]
    
    await crawler.auto_scaling_crawl(urls)

# asyncio.run(auto_scaling_demo())
```

This advanced usage guide covers enterprise-level features, optimization strategies, and scaling patterns for the AsyncWebCrawler implementation. Use these patterns to build robust, high-performance web crawling systems.