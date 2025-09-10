-- Align Testing table with Table-Build.prompt.md specification (exactly 7 columns)
-- Reference: Table-Build.prompt.md - Keep the schema simple, 7 columns total

-- Drop extra columns not in specification
ALTER TABLE "Testing" 
DROP COLUMN IF EXISTS raw_data;

-- Rename created_at to timestamp (matches specification requirement)
ALTER TABLE "Testing" 
RENAME COLUMN created_at TO "timestamp";

-- Final table structure matches Table-Build.prompt.md exactly:
-- 1. id → unique identifier
-- 2. source_url → page URL where odds are listed  
-- 3. website_name → name of the site (e.g., Polymarket, Kalshi)
-- 4. bet_title → the actual bet or market name
-- 5. odds → raw odds values scraped from the page
-- 6. summary → short overview of the event/market  
-- 7. timestamp → when the odds were retrieved
