# Daily AI Reporting Implementation - Corrected for Prediction Market Data

## Overview

Add daily AI reporting to analyze prediction market data collected by Crawl4AI. The `Testing` table stores structured prediction market data (website_name, bet_title, odds, summary, etc.). We'll create a Supabase Edge Function that runs daily at 9 AM via pg_cron, queries the last 24 hours of data, sends it to OpenAI/Anthropic for trend analysis, and emails insights via Resend.

## Current Table Structure

```sql
Testing table columns:
- id (bigint)
- timestamp (timestamptz)
- source_url (text)
- website_name (varchar) - e.g., "Polymarket", "Kalshi"
- bet_title (varchar) - e.g., "Republican Presidential Nominee 2028"
- odds (text) - e.g., "52% Yes"
- summary (text) - Market description
- market_category (varchar) - e.g., "Politics", "Sports"
- betting_options (text) - e.g., "Yes/No"
- probability_percentage (numeric)
- volume_info (varchar)
- closing_date (timestamp)
```

## Implementation Steps

### Step 1: Enable pg_cron
```sql
-- Migration: 20250111_enable_pgcron.sql
CREATE EXTENSION IF NOT EXISTS pg_cron;
GRANT USAGE ON SCHEMA cron TO postgres;
```

### Step 2: Create Edge Function
```bash
supabase functions new daily-report
```

File: `supabase/functions/daily-report/index.ts`
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  // Query last 24 hours of prediction market data
  const yesterday = new Date(Date.now() - 24*60*60*1000).toISOString()
  
  const { data, error } = await supabase
    .from('Testing')
    .select('website_name, bet_title, odds, market_category, volume_info, probability_percentage')
    .gte('timestamp', yesterday)

  if (error) throw error

  // Aggregate by category
  const marketsByCategory = data.reduce((acc, row) => {
    const category = row.market_category || 'Other'
    if (!acc[category]) acc[category] = []
    acc[category].push({
      site: row.website_name,
      title: row.bet_title,
      odds: row.odds,
      volume: row.volume_info
    })
    return acc
  }, {})

  // Send to AI for analysis
  const aiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'gpt-4',
      messages: [{
        role: 'system',
        content: 'Analyze prediction market trends and provide insights.'
      }, {
        role: 'user',
        content: `Analyze these prediction markets from the last 24 hours:\n${JSON.stringify(marketsByCategory, null, 2)}`
      }]
    })
  })

  const analysis = await aiResponse.json()
  
  // Send email via Resend
  const emailResponse = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${Deno.env.get('RESEND_API_KEY')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      from: 'reports@yourdomain.com',
      to: Deno.env.get('REPORT_EMAIL_TO'),
      subject: `Daily Prediction Market Report - ${new Date().toLocaleDateString()}`,
      html: `<h1>Daily Market Analysis</h1>${analysis.choices[0].message.content}`
    })
  })

  return new Response('Report sent', { status: 200 })
})
```

### Step 3: Store Secrets
```bash
supabase secrets set OPENAI_API_KEY=your_key
supabase secrets set RESEND_API_KEY=your_key
supabase secrets set REPORT_EMAIL_TO=recipient@email.com
```

### Step 4: Schedule with pg_cron
```sql
-- Migration: 20250111_schedule_daily_report.sql
SELECT cron.schedule(
  'daily-prediction-report',
  '0 9 * * *',
  $$
  SELECT net.http_post(
    url:='https://[PROJECT_REF].supabase.co/functions/v1/daily-report',
    headers:=jsonb_build_object(
      'Authorization', 'Bearer ' || current_setting('app.settings.service_role_key')
    ),
    body:=jsonb_build_object('trigger', 'scheduled')
  );
  $$
);
```

### Step 5: Deploy
```bash
supabase functions deploy daily-report
supabase db push
```

## Monitoring

Check job status:
```sql
SELECT * FROM cron.job_run_details 
WHERE jobname = 'daily-prediction-report' 
ORDER BY start_time DESC LIMIT 10;
```

## Key Differences from Original Plan

1. **No JSONB aggregation** - Query structured columns directly
2. **Prediction market focus** - Analyze odds, categories, and volumes
3. **Category grouping** - Markets grouped by market_category field
4. **Volume tracking** - Include volume_info for trend analysis

## Success Criteria

- ✓ Daily 9 AM execution
- ✓ Aggregates prediction market data by category
- ✓ AI identifies betting trends and anomalies
- ✓ Email contains formatted insights
- ✓ Zero impact on Python crawler