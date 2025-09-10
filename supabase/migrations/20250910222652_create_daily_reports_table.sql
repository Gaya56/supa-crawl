-- Create daily reports table for storing AI analysis reports
CREATE TABLE daily_reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  report_date DATE NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  summary TEXT,
  documents_analyzed INTEGER DEFAULT 0,
  categories_found INTEGER DEFAULT 0,
  ai_insights TEXT,
  status TEXT DEFAULT 'completed'
);

-- Create indexes for faster queries
CREATE INDEX idx_daily_reports_date ON daily_reports(report_date DESC);
CREATE INDEX idx_daily_reports_created_at ON daily_reports(created_at DESC);

-- Enable RLS 
ALTER TABLE daily_reports ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (since this is internal reporting)
CREATE POLICY "Allow all operations on daily_reports" ON daily_reports FOR ALL USING (true);
