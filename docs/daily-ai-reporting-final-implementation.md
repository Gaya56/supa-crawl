# Daily AI Reporting Implementation Prompt - Prediction Market Analysis

## Project Overview

We're adding daily AI reporting to our Crawl4AI prediction market scraper. The `Testing` table collects structured betting data (website_name, bet_title, odds, categories, volumes). We'll create a Supabase Edge Function that runs daily at 9 AM via pg_cron, queries the last 24 hours, analyzes trends with AI, and emails insights via Resend. This requires zero changes to the existing Python crawler.

## Verified Table Structure
```sql
-- Testing table columns (confirmed via MCP tools):
id                     bigint (auto)
timestamp              timestamptz (auto)
source_url             text
website_name           varchar(100)  -- "Polymarket", "Kalshi", etc.
bet_title              varchar(500)  -- "US Election 2028", etc.
odds                   text          -- "52% Yes", "$0.65", etc.
summary                text
market_category        varchar(100)  -- "Politics", "Sports", etc.
betting_options        text          -- "Yes/No", "Team A/B", etc.
probability_percentage numeric(5,2)  -- 0-100
volume_info            varchar(200)  -- "$1.2M volume", etc.
closing_date           timestamp
```

## MCP Tools Required

### File System Operations
- `filesystem:list_directory` - Map project structure
- `filesystem:read_text_file` - Read existing files
- `filesystem:create_directory` - Create function directories
- `filesystem:write_file` - Write new files

### Supabase Operations
- `supabase:list_tables` - Verify table structure
- `supabase:execute_sql` - Query data and test
- `supabase:apply_migration` - Apply migrations
- `supabase:deploy_edge_function` - Deploy function
- `supabase:get_logs` - Monitor execution

### Documentation
- `supabase:search_docs` - Find official patterns

## Step-by-Step Implementation

### Step 1: Verify Current State
**Tools**: `filesystem:list_directory`, `supabase:execute_sql`

Check table structure:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'Testing';
```

Check recent data:
```sql
SELECT website_name, bet_title, odds, market_category 
FROM Testing 
ORDER BY timestamp DESC 
LIMIT 5;
```

### Step 2: Enable pg_cron Extension
**Tools**: `filesystem:write_file`, `supabase:apply_migration`

Create: `supabase/migrations/20250111_enable_pgcron.sql`
```sql
-- Enable scheduled jobs
CREATE EXTENSION IF NOT EXISTS pg_cron;
GRANT USAGE ON SCHEMA cron TO postgres;

-- Enable HTTP for Edge Function calls
CREATE EXTENSION IF NOT EXISTS pg_net;
```

### Step 3: Create Edge Function
**Tools**: `filesystem:create_directory`, `filesystem:write_file`

Create directory:
```bash
supabase/functions/daily-report/
```

Create: `supabase/functions/daily-report/index.ts`
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  try {
    // Initialize Supabase admin client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Query last 24 hours of prediction markets
    const yesterday = new Date()
    yesterday.setHours(yesterday.getHours() - 24)
    
    const { data, error } = await supabase
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

    if (error) throw error

    // Group markets by category
    const categorizedMarkets = data.reduce((acc: any, market) => {
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
    }, {})

    // Prepare AI prompt
    const marketSummary = JSON.stringify(categorizedMarkets, null, 2)
    const totalMarkets = data.length

    // Call OpenAI for analysis
    const openAIResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: `You are a prediction market analyst. Analyze betting trends, identify high-volume markets, probability shifts, and emerging topics. Format your response as an HTML report with sections for: Executive Summary, Market Trends by Category, Notable Movements, and Investment Opportunities.`
          },
          {
            role: 'user',
            content: `Analyze these ${totalMarkets} prediction markets from the last 24 hours:\n\n${marketSummary}`
          }
        ],
        temperature: 0.7,
        max_tokens: 2000
      })
    })

    const aiData = await openAIResponse.json()
    const aiAnalysis = aiData.choices[0].message.content

    // Create HTML email
    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; }
            h1 { color: #333; }
            h2 { color: #666; }
            .stats { background: #f4f4f4; padding: 10px; border-radius: 5px; }
            .market { margin: 10px 0; padding: 10px; border-left: 3px solid #007bff; }
          </style>
        </head>
        <body>
          <h1>Daily Prediction Market Report</h1>
          <p>Report Date: ${new Date().toLocaleDateString()}</p>
          <div class="stats">
            <strong>Total Markets Analyzed:</strong> ${totalMarkets}<br>
            <strong>Data Sources:</strong> ${[...new Set(data.map(m => m.website_name))].join(', ')}
          </div>
          ${aiAnalysis}
        </body>
      </html>
    `

    // Send email via Resend
    const emailResponse = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${Deno.env.get('RESEND_API_KEY')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from: 'Prediction Market Reports <reports@yourdomain.com>',
        to: Deno.env.get('REPORT_EMAIL_TO')!.split(','),
        subject: `Daily Prediction Market Analysis - ${new Date().toLocaleDateString()}`,
        html: htmlContent
      })
    })

    if (!emailResponse.ok) {
      throw new Error(`Email failed: ${await emailResponse.text()}`)
    }

    return new Response(
      JSON.stringify({ 
        success: true, 
        markets_analyzed: totalMarkets,
        email_sent: true 
      }),
      { headers: { 'Content-Type': 'application/json' } }
    )
    
  } catch (error) {
    console.error('Error in daily report:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
})
```

### Step 4: Set Environment Variables
**Tool**: `supabase:secrets`

```bash
# In Supabase Dashboard > Settings > Edge Functions
OPENAI_API_KEY=sk-...
RESEND_API_KEY=re_...
REPORT_EMAIL_TO=recipient@example.com,another@example.com
```

### Step 5: Create pg_cron Schedule
**Tools**: `filesystem:write_file`, `supabase:apply_migration`

Create: `supabase/migrations/20250111_schedule_daily_report.sql`
```sql
-- Store credentials in vault
INSERT INTO vault.secrets (name, secret)
VALUES 
  ('DAILY_REPORT_URL', 'https://[PROJECT-REF].supabase.co/functions/v1/daily-report'),
  ('SERVICE_ROLE_KEY', '[YOUR-SERVICE-ROLE-KEY]')
ON CONFLICT (name) DO UPDATE SET secret = EXCLUDED.secret;

-- Schedule daily execution at 9 AM
SELECT cron.schedule(
  'daily-prediction-report',
  '0 9 * * *',
  $$
  SELECT net.http_post(
    url := (SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'DAILY_REPORT_URL'),
    headers := jsonb_build_object(
      'Authorization', 'Bearer ' || (SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'SERVICE_ROLE_KEY'),
      'Content-Type', 'application/json'
    ),
    body := jsonb_build_object('scheduled', true)
  );
  $$
);
```

### Step 6: Deploy Everything
**Tools**: `supabase:deploy_edge_function`, `supabase:apply_migration`

```bash
# Deploy function
supabase functions deploy daily-report

# Apply migrations
supabase db push
```

### Step 7: Test Manually
**Tool**: `supabase:execute_sql`

```sql
-- Trigger function manually
SELECT net.http_post(
  url := 'https://[PROJECT-REF].supabase.co/functions/v1/daily-report',
  headers := jsonb_build_object(
    'Authorization', 'Bearer [SERVICE-ROLE-KEY]'
  ),
  body := jsonb_build_object('test', true)
);
```

### Step 8: Monitor Execution
**Tools**: `supabase:execute_sql`, `supabase:get_logs`

Check cron status:
```sql
-- View scheduled jobs
SELECT * FROM cron.job;

-- Check recent runs
SELECT * FROM cron.job_run_details 
WHERE jobname = 'daily-prediction-report' 
ORDER BY start_time DESC;

-- Check HTTP responses
SELECT * FROM net._http_response 
ORDER BY created DESC 
LIMIT 5;
```

## Expected Daily Report Format

```
DAILY PREDICTION MARKET ANALYSIS
================================

EXECUTIVE SUMMARY
- 127 active markets analyzed across 4 platforms
- Politics category showing highest volume ($2.3M)
- Notable shift in tech sector predictions

MARKET TRENDS BY CATEGORY

Politics (45 markets)
- "2028 Presidential Election" - 52% Trump Jr (Polymarket, $890K volume)
- "Senate Control 2026" - 48% Democrats (Kalshi, $340K volume)

Sports (32 markets)
- "Super Bowl Winner" - Chiefs 22% (multiple platforms)
- High volume on NBA championship markets

[Additional sections...]
```

## Monitoring & Maintenance

1. **Daily Health Check**
   ```sql
   SELECT COUNT(*) as markets_today 
   FROM Testing 
   WHERE timestamp > CURRENT_DATE;
   ```

2. **Failed Job Investigation**
   ```sql
   SELECT * FROM cron.job_run_details 
   WHERE status != 'succeeded' 
   AND start_time > CURRENT_DATE - INTERVAL '7 days';
   ```

3. **Function Logs**
   - Check Supabase Dashboard > Functions > Logs
   - Or use `supabase functions logs daily-report`

## Success Criteria
- ✓ Runs daily at 9 AM automatically
- ✓ Analyzes all markets from last 24 hours
- ✓ Groups by market_category
- ✓ AI identifies trends and opportunities
- ✓ Email sent to configured recipients
- ✓ Zero impact on Python crawler