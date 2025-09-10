-- Cleanup Testing table: Remove unnecessary columns and optimize data types
-- Keep only essential columns for web scraping with proper data types

-- Drop redundant columns and over-engineered features
ALTER TABLE public."Testing" 
DROP COLUMN IF EXISTS timestamp,
DROP COLUMN IF EXISTS odds_structured,
DROP COLUMN IF EXISTS confidence_score,
DROP COLUMN IF EXISTS market_status;

-- Optimize data types for better performance and storage
-- Change TEXT columns to appropriate VARCHAR lengths with constraints
ALTER TABLE public."Testing" 
ALTER COLUMN source_url TYPE VARCHAR(500),
ALTER COLUMN website_name TYPE VARCHAR(50), 
ALTER COLUMN bet_title TYPE VARCHAR(300),
ALTER COLUMN summary TYPE VARCHAR(1000);

-- Keep odds as TEXT for flexibility (different formats: %, decimals, fractions)
-- Keep raw_data as JSONB for complete scraped data backup

-- Add NOT NULL constraints for critical fields
ALTER TABLE public."Testing" 
ALTER COLUMN source_url SET NOT NULL,
ALTER COLUMN website_name SET NOT NULL,
ALTER COLUMN bet_title SET NOT NULL,
ALTER COLUMN odds SET NOT NULL;

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_testing_website_name ON public."Testing"(website_name);
CREATE INDEX IF NOT EXISTS idx_testing_created_at ON public."Testing"(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_testing_raw_data_gin ON public."Testing" USING GIN(raw_data);

-- Final optimized table structure:
-- 1. id (bigint) - Primary key with auto-increment
-- 2. created_at (timestamptz) - Auto timestamp of record creation  
-- 3. source_url (varchar(500)) - The scraped page URL [NOT NULL]
-- 4. website_name (varchar(50)) - Platform identifier [NOT NULL]
-- 5. bet_title (varchar(300)) - Market question/title [NOT NULL]
-- 6. odds (text) - Raw odds in various formats [NOT NULL]
-- 7. summary (varchar(1000)) - Market description [NULLABLE]
-- 8. raw_data (jsonb) - Complete scraped data backup [NULLABLE]
