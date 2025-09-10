# Daily AI Reporting - Complete Implementation Guide

## Repository Structure
```
/home/ali/Documents/Crawl4AI-Testing/supa-crawl/
├── supabase/
│   ├── migrations/           # SQL migrations
│   ├── functions/           # Edge Functions (to be created)
│   └── config.toml          # Supabase config
├── src/                     # Python crawler (no changes needed)
├── docs/                    # Documentation
└── .env                     # Environment variables
```

## Prerequisites

### Check Supabase CLI Installation
```bash
cd /home/ali/Documents/Crawl4AI-Testing/supa-crawl
supabase --version
```

If not installed:
```bash
npm install -g supabase
```

## Implementation Steps

### Step 1: Verify Project State

**Terminal:**
```bash
cd /home/ali/Documents/Crawl4AI-Testing/supa-crawl
supabase projects list
```

**Verify Table Structure:**
```bash
supabase db execute --sql "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'Testing'"
```

**Check Sample Data:**
```bash
supabase db execute --sql "SELECT website_name, bet_title, odds, market_category FROM Testing ORDER BY timestamp DESC LIMIT 5"
```

### Step 2: Enable Required Extensions

**Create Migration File:**
```bash
supabase migration new enable_pgcron_and_pgnet
```

**Edit:** `supabase/migrations/[timestamp]_enable_pgcron_and_pgnet.sql`
```sql
-- Enable scheduled jobs
-- Docs: https://supabase.com/docs/guides/database/extensions/pg_cron
CREATE EXTENSION IF NOT EXISTS pg_cron;
GRANT USAGE ON SCHEMA cron TO postgres;

-- Enable HTTP requests
-- Docs: https://supabase.com/docs/guides/database/extensions/pg_net
CREATE EXTENSION IF NOT EXISTS pg_net;

-- Enable vault for secure storage
-- Docs: https://supabase.com/docs/guides/database/vault
CREATE EXTENSION IF NOT EXISTS vault;
```

**Apply Migration:**
```bash
supabase db push
```

### Step 3: Create Edge Function

**Terminal:**
```bash
supabase functions new daily-report
```

This creates:
- `/home/ali/Documents/Crawl4AI-Testing/supa-crawl/supabase/functions/daily-report/`
- `/home/ali/Documents/Crawl4AI-Testing/supa-crawl/supabase/functions/daily-report/index.ts`

**Edit:** `supabase/functions/daily-report/index.ts`
```typescript
// Deno imports - https://supabase.com/docs/guides/functions/import-maps
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.7'

// Types
interface PredictionMarket {
  website_name: string
  bet_title: string
  odds: string
  summary: string
  market_category: string | null
  betting_options: string | null
  probability_percentage: number | null
  volume_info: string | null
}

interface MarketsByCategory {
  [key: string]: Array<{
    site: string
    title: string
    odds: string
    probability: number | null
    volume: string | null
  }>
}

serve(async (req: Request) => {
  try {
    console.log('Daily report function started')

    // Initialize Supabase admin client
    // Docs: https://supabase.com/docs/guides/functions/connect-to-postgres
    const supabaseUrl = Deno.env.get('SUPABASE_URL')
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if (!supabaseUrl || !supabaseServiceKey) {
      throw new Error('Missing Supabase credentials')
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey, {
      auth: {
        autoRefreshToken: false,
        persistSession: false
      }
    })

    // Query last 24 hours of prediction market data
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    
    console.log(`Querying data since: ${yesterday.toISOString()}`)
    
    const { data: markets, error } = await supabase
      .from('Testing')
      .select(`
        website_name,
        bet_title,
        odds,
        summary,
        market_category,
        betting_options,
        probability_percentage,
        volume_info
      `)
      .gte('timestamp', yesterday.toISOString())
      .order('volume_info', { ascending: false, nullsFirst: false })

    if (error) {
      console.error('Database query error:', error)
      throw error
    }

    console.log(`Found ${markets?.length || 0} markets`)

    if (!markets || markets.length === 0) {
      return new Response(
        JSON.stringify({ message: 'No markets found in last 24 hours' }),
        { headers: { 'Content-Type': 'application/json' } }
      )
    }

    // Group markets by category
    const categorizedMarkets: MarketsByCategory = markets.reduce((acc, market) => {
      const category = market.market_category || 'Uncategorized'
      if (!acc[category]) acc[category] = []
      acc[category].push({
        site: market.website_name,
        title: market.bet_title,
        odds: market.odds,
        probability: market.probability_percentage,
        volume: market.volume_info
      })
      return acc
    }, {} as MarketsByCategory)

    // Get unique websites
    const websites = [...new Set(markets.map((m: PredictionMarket) => m.website_name))]
    
    // Prepare market summary
    const marketSummary = Object.entries(categorizedMarkets)
      .map(([category, items]) => `${category}: ${items.length} markets`)
      .join(', ')

    console.log('Market summary:', marketSummary)

    // Call OpenAI for analysis
    // Docs: https://platform.openai.com/docs/api-reference/chat/create
    const openaiKey = Deno.env.get('OPENAI_API_KEY')
    if (!openaiKey) {
      throw new Error('Missing OpenAI API key')
    }

    console.log('Calling OpenAI for analysis...')
    
    const openAIResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openaiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: `You are a prediction market analyst. Analyze betting trends and provide insights in HTML format with these sections:
            1. Executive Summary (key findings in 3-4 bullets)
            2. Market Trends by Category (highlight high-volume and shifting markets)
            3. Notable Movements (significant probability changes or new markets)
            4. Investment Opportunities (markets with potential value)
            Format as clean HTML with <h2> headers and <ul>/<li> for lists.`
          },
          {
            role: 'user',
            content: `Analyze ${markets.length} prediction markets from the last 24 hours across ${websites.length} platforms:

Categories: ${marketSummary}

Full data:
${JSON.stringify(categorizedMarkets, null, 2)}`
          }
        ],
        temperature: 0.7,
        max_tokens: 2000
      })
    })

    if (!openAIResponse.ok) {
      const errorText = await openAIResponse.text()
      console.error('OpenAI error:', errorText)
      throw new Error(`OpenAI API failed: ${openAIResponse.status}`)
    }

    const aiData = await openAIResponse.json()
    const aiAnalysis = aiData.choices[0].message.content

    // Create HTML email
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }
    h1 {
      color: #1a1a1a;
      border-bottom: 3px solid #007bff;
      padding-bottom: 10px;
    }
    h2 {
      color: #444;
      margin-top: 25px;
    }
    .header-info {
      background: #f8f9fa;
      padding: 15px;
      border-radius: 8px;
      margin: 20px 0;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 10px;
      margin: 15px 0;
    }
    .stat-box {
      background: #007bff;
      color: white;
      padding: 10px;
      border-radius: 5px;
      text-align: center;
    }
    .stat-box .number {
      font-size: 24px;
      font-weight: bold;
    }
    .stat-box .label {
      font-size: 14px;
      opacity: 0.9;
    }
    ul {
      padding-left: 20px;
    }
    li {
      margin: 8px 0;
    }
  </style>
</head>
<body>
  <h1>📊 Daily Prediction Market Report</h1>
  
  <div class="header-info">
    <strong>Report Date:</strong> ${new Date().toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })}<br>
    <strong>Analysis Period:</strong> Last 24 hours<br>
    <strong>Data Sources:</strong> ${websites.join(', ')}
  </div>
  
  <div class="stats">
    <div class="stat-box">
      <div class="number">${markets.length}</div>
      <div class="label">Total Markets</div>
    </div>
    <div class="stat-box">
      <div class="number">${Object.keys(categorizedMarkets).length}</div>
      <div class="label">Categories</div>
    </div>
    <div class="stat-box">
      <div class="number">${websites.length}</div>
      <div class="label">Platforms</div>
    </div>
  </div>
  
  ${aiAnalysis}
  
  <hr style="margin-top: 40px; border: 1px solid #eee;">
  <p style="font-size: 12px; color: #666; text-align: center;">
    This report was automatically generated by Crawl4AI Daily Reporter. 
    Data sourced from ${websites.join(', ')}.
  </p>
</body>
</html>`

    console.log('HTML email created, sending via Resend...')

    // Send email via Resend
    // Docs: https://resend.com/docs/api-reference/emails/send-email
    const resendKey = Deno.env.get('RESEND_API_KEY')
    const emailTo = Deno.env.get('REPORT_EMAIL_TO')
    
    if (!resendKey || !emailTo) {
      throw new Error('Missing Resend configuration')
    }

    const emailResponse = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${resendKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from: 'Prediction Markets <reports@yourdomain.com>',
        to: emailTo.split(',').map(email => email.trim()),
        subject: `📈 Daily Prediction Market Analysis - ${new Date().toLocaleDateString()}`,
        html: htmlContent
      })
    })

    if (!emailResponse.ok) {
      const errorText = await emailResponse.text()
      console.error('Resend error:', errorText)
      throw new Error(`Email sending failed: ${emailResponse.status}`)
    }

    const emailResult = await emailResponse.json()
    console.log('Email sent successfully:', emailResult.id)

    // Return success response
    return new Response(
      JSON.stringify({ 
        success: true, 
        markets_analyzed: markets.length,
        categories: Object.keys(categorizedMarkets).length,
        email_id: emailResult.id,
        timestamp: new Date().toISOString()
      }),
      { 
        status: 200,
        headers: { 'Content-Type': 'application/json' } 
      }
    )
    
  } catch (error) {
    console.error('Function error:', error)
    return new Response(
      JSON.stringify({ 
        error: error.message,
        timestamp: new Date().toISOString()
      }),
      { 
        status: 500, 
        headers: { 'Content-Type': 'application/json' } 
      }
    )
  }
})
```

### Step 4: Set Environment Variables

**In Supabase Dashboard:**
1. Go to: https://supabase.com/dashboard/project/[YOUR-PROJECT]/settings/functions
2. Add these secrets:

```bash
OPENAI_API_KEY=sk-...your-key...
RESEND_API_KEY=re_...your-key...
REPORT_EMAIL_TO=email1@example.com,email2@example.com
```

**Or via CLI:**
```bash
supabase secrets set OPENAI_API_KEY="sk-..."
supabase secrets set RESEND_API_KEY="re_..."
supabase secrets set REPORT_EMAIL_TO="email@example.com"
```

### Step 5: Store Service Role Key in Vault

**Create Migration:**
```bash
supabase migration new setup_vault_secrets
```

**Edit:** `supabase/migrations/[timestamp]_setup_vault_secrets.sql`
```sql
-- Store secrets securely
-- Docs: https://supabase.com/docs/guides/database/vault

-- Get your project URL and service role key from:
-- https://supabase.com/dashboard/project/[PROJECT-ID]/settings/api

SELECT vault.create_secret('https://[PROJECT-REF].supabase.co/functions/v1/daily-report', 'daily_report_url');
SELECT vault.create_secret('[YOUR-SERVICE-ROLE-KEY]', 'service_role_key');
```

**Apply Migration:**
```bash
supabase db push
```

### Step 6: Create pg_cron Schedule

**Create Migration:**
```bash
supabase migration new schedule_daily_report
```

**Edit:** `supabase/migrations/[timestamp]_schedule_daily_report.sql`
```sql
-- Schedule daily report at 9 AM
-- Docs: https://supabase.com/docs/guides/functions/schedule-functions

SELECT cron.schedule(
  'daily-prediction-report',    -- job name
  '0 9 * * *',                 -- 9 AM every day
  $$
  SELECT net.http_post(
    url := (SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'daily_report_url'),
    headers := jsonb_build_object(
      'Authorization', 'Bearer ' || (SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'service_role_key'),
      'Content-Type', 'application/json'
    ),
    body := jsonb_build_object(
      'scheduled', true,
      'timestamp', now()
    )
  ) AS request_id;
  $$
);

-- Optional: Add comment for documentation
COMMENT ON CRON JOB 'daily-prediction-report' IS 'Sends daily prediction market analysis report via email at 9 AM';
```

**Apply Migration:**
```bash
supabase db push
```

### Step 7: Deploy Edge Function

**Deploy to Production:**
```bash
cd /home/ali/Documents/Crawl4AI-Testing/supa-crawl
supabase functions deploy daily-report
```

**Verify Deployment:**
```bash
supabase functions list
```

### Step 8: Test the Function

**Manual Test via Terminal:**
```bash
# Get your anon key
ANON_KEY=$(supabase status | grep "anon key" | cut -d'"' -f2)
PROJECT_URL=$(supabase status | grep "API URL" | cut -d'"' -f2)

# Test the function
curl -X POST "$PROJECT_URL/functions/v1/daily-report" \
  -H "Authorization: Bearer $ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

**Test via SQL:**
```bash
supabase db execute --sql "
SELECT net.http_post(
  url := 'https://[PROJECT-REF].supabase.co/functions/v1/daily-report',
  headers := jsonb_build_object(
    'Authorization', 'Bearer [SERVICE-ROLE-KEY]'
  ),
  body := jsonb_build_object('manual_test', true)
);"
```

### Step 9: Monitor Execution

**Check Cron Jobs:**
```bash
supabase db execute --sql "SELECT * FROM cron.job WHERE jobname = 'daily-prediction-report';"
```

**Check Recent Runs:**
```bash
supabase db execute --sql "
SELECT jobid, jobname, status, start_time, end_time, duration 
FROM cron.job_run_details 
WHERE jobname = 'daily-prediction-report' 
ORDER BY start_time DESC 
LIMIT 10;"
```

**Check Function Logs:**
```bash
supabase functions logs daily-report --tail
```

**Check HTTP Responses:**
```bash
supabase db execute --sql "
SELECT id, status_code, content, created 
FROM net._http_response 
WHERE content LIKE '%daily-report%' 
ORDER BY created DESC 
LIMIT 5;"
```

## Troubleshooting

### Debug Cron Execution
```sql
-- Check if pg_cron is running
SELECT * FROM pg_stat_activity WHERE application_name = 'pg_cron scheduler';

-- View all cron jobs
SELECT * FROM cron.job;

-- Check failed jobs
SELECT * FROM cron.job_run_details 
WHERE status != 'succeeded' 
ORDER BY start_time DESC;
```

### Test Data Query
```sql
-- Verify you have recent data
SELECT COUNT(*), MAX(timestamp) as latest 
FROM "Testing" 
WHERE timestamp > NOW() - INTERVAL '24 hours';
```

### Restart pg_cron (if needed)
```sql
-- As superuser
SELECT cron.unschedule('daily-prediction-report');
-- Then re-run the schedule migration
```

## Official Documentation Links

- **pg_cron Extension**: https://supabase.com/docs/guides/database/extensions/pg_cron
- **Edge Functions**: https://supabase.com/docs/guides/functions/quickstart
- **Scheduled Functions**: https://supabase.com/docs/guides/functions/schedule-functions
- **Environment Variables**: https://supabase.com/docs/guides/functions/secrets
- **Function Deployment**: https://supabase.com/docs/guides/functions/deploy
- **Vault Extension**: https://supabase.com/docs/guides/database/vault
- **pg_net Extension**: https://supabase.com/docs/guides/database/extensions/pg_net
- **Function Logs**: https://supabase.com/docs/guides/functions/logging

## File Structure After Implementation
```
/home/ali/Documents/Crawl4AI-Testing/supa-crawl/
├── supabase/
│   ├── migrations/
│   │   ├── [timestamp]_enable_pgcron_and_pgnet.sql
│   │   ├── [timestamp]_setup_vault_secrets.sql
│   │   └── [timestamp]_schedule_daily_report.sql
│   ├── functions/
│   │   └── daily-report/
│   │       └── index.ts
│   └── config.toml
├── src/               # Python crawler (unchanged)
├── docs/
│   └── daily-ai-reporting-complete-implementation.md
└── .env              # Local environment variables
```