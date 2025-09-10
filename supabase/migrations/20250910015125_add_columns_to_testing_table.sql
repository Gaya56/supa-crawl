-- Create the Testing table if it does not exist
CREATE TABLE IF NOT EXISTS public."Testing" (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add the required columns for the testing table
ALTER TABLE public."Testing" 
ADD COLUMN IF NOT EXISTS source_url TEXT,
ADD COLUMN IF NOT EXISTS website_name TEXT,
ADD COLUMN IF NOT EXISTS bet_title TEXT,
ADD COLUMN IF NOT EXISTS odds TEXT,
ADD COLUMN IF NOT EXISTS summary TEXT,
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMPTZ DEFAULT NOW();