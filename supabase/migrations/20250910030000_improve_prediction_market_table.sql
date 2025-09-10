-- Improve Testing table for better prediction market data structure
-- Remove mock data and enhance columns for clearer betting information
-- Date: September 10, 2025

-- First, clear all existing mock/test data
DELETE FROM "Testing";

-- Add new columns for better prediction market data structure (separate ALTER statements)
ALTER TABLE "Testing" ADD COLUMN IF NOT EXISTS market_category VARCHAR(100);
ALTER TABLE "Testing" ADD COLUMN IF NOT EXISTS betting_options TEXT;
ALTER TABLE "Testing" ADD COLUMN IF NOT EXISTS probability_percentage DECIMAL(5,2);
ALTER TABLE "Testing" ADD COLUMN IF NOT EXISTS volume_info VARCHAR(200);
ALTER TABLE "Testing" ADD COLUMN IF NOT EXISTS closing_date TIMESTAMP;

-- Modify existing columns for better data types and clarity
ALTER TABLE "Testing" 
ALTER COLUMN odds TYPE TEXT,
ALTER COLUMN summary TYPE TEXT,
ALTER COLUMN bet_title TYPE VARCHAR(500),
ALTER COLUMN website_name TYPE VARCHAR(100),
ALTER COLUMN source_url TYPE TEXT;

-- Add comments to clarify column purposes
COMMENT ON COLUMN "Testing".id IS 'Unique identifier for each prediction market entry';
COMMENT ON COLUMN "Testing".source_url IS 'Full URL where the prediction market data was scraped';
COMMENT ON COLUMN "Testing".website_name IS 'Name of prediction market platform (Polymarket, Kalshi, etc.)';
COMMENT ON COLUMN "Testing".bet_title IS 'Clear title of the prediction market or betting question';
COMMENT ON COLUMN "Testing".odds IS 'Raw odds/prices as displayed on the site (e.g., "Yes: 65% | No: 35%")';
COMMENT ON COLUMN "Testing".summary IS 'Brief description of what the market is predicting';
COMMENT ON COLUMN "Testing".market_category IS 'Category of prediction (Politics, Sports, Economics, etc.)';
COMMENT ON COLUMN "Testing".betting_options IS 'Available betting choices (Yes/No, Up/Down, Team names, etc.)';
COMMENT ON COLUMN "Testing".probability_percentage IS 'Implied probability as percentage (0-100)';
COMMENT ON COLUMN "Testing".volume_info IS 'Trading volume or liquidity information if available';
COMMENT ON COLUMN "Testing".closing_date IS 'When the market closes/resolves';
COMMENT ON COLUMN "Testing"."timestamp" IS 'When this data was scraped (UTC)';

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_testing_website_name ON "Testing"(website_name);
CREATE INDEX IF NOT EXISTS idx_testing_market_category ON "Testing"(market_category);
CREATE INDEX IF NOT EXISTS idx_testing_timestamp ON "Testing"("timestamp");

-- Reset the sequence to start fresh
ALTER SEQUENCE "Testing_id_seq" RESTART WITH 1;
