# 🏗️ Architecture Overview

## System Design Philosophy

The AsyncWebCrawler Advanced Implementation follows a modular, event-driven architecture designed for scalability, maintainability, and performance. The system is built on three core principles:

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Official Documentation Compliance**: All implementations follow Crawl4AI and Supabase best practices
3. **Async-First Design**: Non-blocking operations throughout the entire pipeline

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AsyncWebCrawler System                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │    Entry    │    │   Config    │    │   Models    │    │   Storage   │  │
│  │   Point     │    │   Layer     │    │   Layer     │    │   Layer     │  │
│  │             │    │             │    │             │    │             │  │
│  │  main.py    │───▶│ environment │───▶│  schemas    │───▶│  supabase   │  │
│  │             │    │   .py       │    │    .py      │    │ _handler.py │  │
│  │ • CLI       │    │             │    │             │    │             │  │
│  │ • Orchestr. │    │ • Env Vars  │    │ • Pydantic │    │ • CRUD Ops  │  │
│  │ • Error     │    │ • Browser   │    │ • Validation│    │ • Real-time │  │
│  │   Handling  │    │   Config    │    │ • Schemas   │    │ • Webhooks  │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                   │                   │                   │       │
│         │                   │                   │                   │       │
│         ▼                   │                   │                   │       │
│  ┌─────────────┐            │                   │                   │       │
│  │   Crawler   │◀───────────┘                   │                   │       │
│  │   Engine    │◀───────────────────────────────┘                   │       │
│  │             │◀───────────────────────────────────────────────────┘       │
│  │async_crawler│                                                            │
│  │    .py      │                                                            │
│  │             │                                                            │
│  │ • Memory    │    ┌─────────────┐    ┌─────────────┐                     │
│  │   Adaptive  │    │   AI/LLM    │    │ Monitoring  │                     │
│  │ • Semaphore │    │    Layer    │    │  & Logging  │                     │
│  │ • LLM       │───▶│             │    │             │                     │
│  │ • Storage   │    │  OpenAI     │    │ • Metrics   │                     │
│  │ • Rate      │    │  GPT-4o     │    │ • Errors    │                     │
│  │   Limiting  │    │             │    │ • Analytics │                     │
│  └─────────────┘    └─────────────┘    └─────────────┘                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Entry Point Layer (`main.py`)

**Purpose**: Orchestrates the entire crawling workflow and provides the user interface.

**Responsibilities**:
- Command-line interface and argument parsing
- Environment validation and setup
- Workflow orchestration
- Error handling and reporting
- Performance monitoring

**Key Features**:
```python
async def main():
    # Complete workflow demonstration
    crawler = AdvancedWebCrawler()
    
    # 1. Memory Adaptive Dispatcher
    results = await crawler.crawl_with_memory_adaptive_dispatcher(urls)
    
    # 2. Semaphore Dispatcher  
    sem_results = await crawler.crawl_with_semaphore_dispatcher(urls)
    
    # 3. LLM Analysis
    llm_results = await crawler.crawl_with_llm_analysis(urls)
    
    # 4. Full Pipeline with Storage
    success = await crawler.crawl_and_store_in_supabase(urls)
```

### 2. Configuration Layer (`src/config/environment.py`)

**Purpose**: Centralizes all configuration management following official patterns.

**Official Documentation Compliance**:
- Crawl4AI `BrowserConfig` and `CrawlerRunConfig` patterns
- Supabase client initialization standards
- Environment variable best practices

**Key Classes**:

```python
class EnvironmentConfig:
    """Environment variable management with validation"""
    
class CrawlerConfig:
    """Factory for official Crawl4AI configurations"""
    
    @staticmethod
    def create_browser_config() -> BrowserConfig:
        """Official BrowserConfig with stealth settings"""
        
    @staticmethod  
    def create_crawler_run_config() -> CrawlerRunConfig:
        """Official CrawlerRunConfig with rate limiting"""
```

### 3. Models Layer (`src/models/schemas.py`)

**Purpose**: Defines data structures and validation schemas using Pydantic.

**Schema Definitions**:
```python
class PageSummary(BaseModel):
    """LLM extraction schema for structured analysis"""
    title: str = Field(..., description="Page title")
    summary: str = Field(..., description="Brief summary")

class CrawlResult(BaseModel):
    """Standardized crawler output structure"""
    url: str
    content: str
    analysis: Optional[Dict[str, Any]] = None
    timestamp: datetime
    success: bool

class SupabaseRecord(BaseModel):
    """Database record format for storage"""
    url: str
    content: str
    analysis_header: Optional[str] = None
```

### 4. Crawler Engine (`src/crawlers/async_crawler.py`)

**Purpose**: Core crawling logic implementing multiple dispatch strategies.

**Dispatcher Strategies**:

#### Memory Adaptive Dispatcher
- **Dynamic Resource Allocation**: Adjusts based on available memory
- **Optimal Performance**: Automatically scales concurrent operations
- **Official Implementation**: Uses Crawl4AI's `MemoryAdaptiveDispatcher`

#### Semaphore Dispatcher  
- **Controlled Concurrency**: Fixed number of concurrent operations
- **Rate Limiting**: Respects target site limits
- **Reliable Performance**: Predictable resource usage

#### LLM Integration
- **OpenAI GPT-4o**: Structured content extraction
- **Schema-Based**: Uses Pydantic models for validation
- **Real-time Processing**: Concurrent analysis during crawling

**Code Example**:
```python
class AdvancedWebCrawler:
    async def crawl_with_memory_adaptive_dispatcher(self, urls: List[str]):
        """Memory adaptive crawling with dynamic resource allocation"""
        
    async def crawl_with_semaphore_dispatcher(self, urls: List[str]):
        """Semaphore-based crawling with controlled concurrency"""
        
    async def crawl_with_llm_analysis(self, urls: List[str]):
        """AI-powered content analysis with OpenAI GPT-4o"""
        
    async def crawl_and_store_in_supabase(self, urls: List[str]):
        """Complete pipeline with real-time storage"""
```

### 5. Storage Layer (`src/storage/supabase_handler.py`)

**Purpose**: Handles all database operations and real-time data management.

**Official Supabase Patterns**:
- `create_client()` initialization
- Real-time subscriptions
- Error handling and retry logic
- Transaction management

**Key Features**:
```python
class SupabaseHandler:
    async def store_crawl_results(self, results: List[CrawlResult]):
        """Store results with analysis headers"""
        
    async def setup_realtime_subscription(self):
        """Real-time change notifications"""
        
    async def get_crawl_history(self):
        """Retrieve historical data"""
```

## Data Flow

### 1. Initialization Flow
```
main.py → EnvironmentConfig → CrawlerConfig → AdvancedWebCrawler
```

### 2. Crawling Flow
```
URLs → Dispatcher → Crawl4AI → Content Extraction → Validation → Results
```

### 3. LLM Analysis Flow
```
Content → OpenAI GPT-4o → Schema Validation → Structured Data → Storage
```

### 4. Storage Flow
```
Results → SupabaseHandler → Database → Real-time Updates → Webhooks
```

## Performance Characteristics

### Memory Usage
- **Memory Adaptive**: 50-200MB depending on content size
- **Semaphore**: 100-150MB consistent usage
- **LLM Analysis**: +50MB for AI processing

### Concurrency
- **Memory Adaptive**: 3-8 concurrent operations (dynamic)
- **Semaphore**: 5 concurrent operations (fixed)
- **Rate Limiting**: 0.1-0.3s delays between requests

### Scalability
- **Horizontal**: Multiple crawler instances supported
- **Vertical**: Scales with available system resources
- **Database**: Supabase handles thousands of concurrent connections

## Error Handling Strategy

### 1. Graceful Degradation
- Network failures → Retry with exponential backoff
- LLM failures → Continue with basic extraction
- Database failures → Local caching with delayed sync

### 2. Monitoring & Alerting
- Real-time error tracking
- Performance metrics collection
- Automated health checks

### 3. Recovery Mechanisms
- Automatic retry logic
- Circuit breaker patterns
- Fallback strategies

## Security Considerations

### 1. Stealth Operations
- Browser fingerprint masking
- User agent rotation
- Request timing randomization

### 2. API Security
- Environment variable management
- API key rotation support
- Rate limiting compliance

### 3. Data Protection
- Secure storage patterns
- Encrypted connections
- Access control lists

## Testing Architecture

### 1. Unit Tests
- Individual component testing
- Mock external dependencies
- Schema validation testing

### 2. Integration Tests
- End-to-end workflow testing
- Database integration
- LLM integration testing

### 3. Performance Tests
- Load testing
- Memory usage profiling
- Concurrency testing

This architecture ensures a robust, scalable, and maintainable web crawling solution that follows industry best practices and official documentation standards.