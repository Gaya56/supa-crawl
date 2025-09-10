-- Optimize Testing table data types for prediction market data
-- Add flexible JSONB columns while keeping existing TEXT fields for backward compatibility

-- Add structured odds column (JSONB for flexibility)
ALTER TABLE public."Testing" 
ADD COLUMN IF NOT EXISTS odds_structured JSONB;

-- Add raw scraped data storage (JSONB)
ALTER TABLE public."Testing" 
ADD COLUMN IF NOT EXISTS raw_data JSONB;

-- Add confidence score for data quality (0.00 to 1.00)
ALTER TABLE public."Testing" 
ADD COLUMN IF NOT EXISTS confidence_score NUMERIC(3,2) CHECK (confidence_score >= 0.00 AND confidence_score <= 1.00);

-- Add market status tracking
ALTER TABLE public."Testing" 
ADD COLUMN IF NOT EXISTS market_status VARCHAR(20) DEFAULT 'active' CHECK (market_status IN ('active', 'closed', 'suspended', 'cancelled'));

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_testing_website_name ON public."Testing"(website_name);
CREATE INDEX IF NOT EXISTS idx_testing_market_status ON public."Testing"(market_status);
CREATE INDEX IF NOT EXISTS idx_testing_confidence_score ON public."Testing"(confidence_score);

-- Add GIN index for JSONB columns (enables fast JSON queries)
CREATE INDEX IF NOT EXISTS idx_testing_odds_structured_gin ON public."Testing" USING GIN (odds_structured);
CREATE INDEX IF NOT EXISTS idx_testing_raw_data_gin ON public."Testing" USING GIN (raw_data);

-- Add comment explaining the optimization
COMMENT ON COLUMN public."Testing".odds_structured IS 'Structured odds data in JSON format for flexible storage of different prediction market formats';
COMMENT ON COLUMN public."Testing".raw_data IS 'Raw scraped data for debugging and backup purposes';
COMMENT ON COLUMN public."Testing".confidence_score IS 'Data quality confidence score from 0.00 to 1.00';
COMMENT ON COLUMN public."Testing".market_status IS 'Current status of the prediction market';
