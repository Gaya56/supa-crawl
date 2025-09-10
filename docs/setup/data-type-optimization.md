# Testing Table Data Type Optimization Guide

## 📊 Current vs Recommended Schema

### Current (All TEXT)
```sql
CREATE TABLE public."Testing" (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  source_url TEXT,        -- ⚠️ Too generic
  website_name TEXT,      -- ✅ Good as TEXT
  bet_title TEXT,         -- ✅ Good as TEXT  
  odds TEXT,              -- ⚠️ Should be numeric
  summary TEXT,           -- ✅ Good as TEXT
  timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

### Recommended (Flexible + Typed)
```sql
CREATE TABLE public."Testing" (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  source_url TEXT NOT NULL,                    -- URLs can vary greatly
  website_name VARCHAR(50) NOT NULL,           -- Limited site names
  bet_title TEXT NOT NULL,                     -- Market titles vary
  odds JSONB,                                  -- 🔥 FLEXIBLE for all formats
  summary TEXT,                                -- Optional descriptions
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  
  -- 🚀 NEW: Additional flexible fields
  raw_data JSONB,                             -- Store original scraped data
  confidence_score NUMERIC(3,2),              -- 0.00 to 1.00
  market_status VARCHAR(20) DEFAULT 'active'   -- active/closed/suspended
);
```

## 🎯 **Why JSONB for Odds? (Most Flexible)**

Different prediction markets use different formats:

### Polymarket (Probability %)
```json
{"yes": 0.67, "no": 0.33, "format": "probability"}
```

### Kalshi (Yes/No Cents)  
```json
{"yes": 67, "no": 33, "format": "cents", "currency": "USD"}
```

### Traditional Betting (Decimal/Fractional)
```json
{"decimal": 2.5, "fractional": "3/2", "american": "+150"}
```

## 🛠️ **Implementation Options**

### Option 1: Add Migration (Recommended)
```bash
# Create new migration
supabase migration new optimize_testing_table_types

# SQL for migration:
ALTER TABLE public."Testing" 
ALTER COLUMN odds TYPE JSONB USING odds::JSONB,
ADD COLUMN IF NOT EXISTS raw_data JSONB,
ADD COLUMN IF NOT EXISTS confidence_score NUMERIC(3,2),
ADD COLUMN IF NOT EXISTS market_status VARCHAR(20) DEFAULT 'active';
```

### Option 2: Keep Current + Add New Columns
```bash
# Less disruptive - add alongside existing
ALTER TABLE public."Testing" 
ADD COLUMN IF NOT EXISTS odds_structured JSONB,
ADD COLUMN IF NOT EXISTS raw_data JSONB,
ADD COLUMN IF NOT EXISTS confidence_score NUMERIC(3,2);
```

### Option 3: Create New Optimized Table
```bash
# Fresh start with better schema
supabase migration new create_optimized_testing_table
```

## 📝 **Python Integration Examples**

### Storing Different Odds Formats
```python
# Polymarket data
odds_data = {
    "yes": 0.67,
    "no": 0.33, 
    "format": "probability",
    "source": "polymarket",
    "last_updated": "2025-09-10T01:00:00Z"
}

# Insert to database
supabase.table("Testing").insert({
    "source_url": "https://polymarket.com/market/...",
    "website_name": "Polymarket",
    "bet_title": "Will candidate X win 2024?",
    "odds": odds_data,  # JSONB handles this automatically
    "raw_data": original_scraped_html,
    "confidence_score": 0.95
}).execute()
```

### Querying Flexible Data
```python
# Find markets with high confidence
results = supabase.table("Testing")
    .select("*")
    .gt("confidence_score", 0.90)
    .execute()

# Query specific odds format
results = supabase.table("Testing")
    .select("*") 
    .eq("odds->format", "probability")
    .execute()
```

## 🚀 **Recommendation: Start with Option 2**

1. **Keep existing TEXT columns** (no breaking changes)
2. **Add JSONB columns** for structured data
3. **Gradually migrate** as you build scrapers
4. **Test thoroughly** before removing old columns

Would you like me to create the migration for this optimization?
