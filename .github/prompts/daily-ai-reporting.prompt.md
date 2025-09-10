---
mode: agent
---
context: |
  We are adding automated daily AI reporting to our existing prediction market crawler. 
  The crawler currently collects betting data from sites like Polymarket and stores it in 
  our Supabase Testing table. We'll implement a scheduled Edge Function that runs every 
  morning at 9 AM to analyze the last 24 hours of data and email insights.

overview: |
  Final System Architecture:
  1. Python Crawler (existing) → collects prediction market data → Testing table
  2. pg_cron (scheduler) → triggers at 9 AM daily → calls Edge Function
  3. Edge Function → queries last 24 hours from Testing table → sends to OpenAI
  4. OpenAI GPT-4 → analyzes market trends by category → returns HTML insights
  5. Resend API → emails formatted report → recipients receive daily analysis
  
  The report will include:
  - Market counts by category (Politics, Sports, etc.)
  - High-volume betting markets
  - Significant probability shifts
  - AI-generated trend analysis

task: Implement daily AI reporting for prediction market data

reference_documents:
  - /home/ali/Documents/Crawl4AI-Testing/supa-crawl/docs/daily-ai-reporting-corrected.md
  - /home/ali/Documents/Crawl4AI-Testing/supa-crawl/docs/daily-ai-reporting-complete-implementation.md

working_directory: /home/ali/Documents/Crawl4AI-Testing/supa-crawl/supabase

available_mcp_servers:
  - filesystem
  - supabase
  - sequential-thinking
  - mcp-omnisearch
  - memory

execution_rules:
  - ONE step at a time - never combine or skip steps
  - Before EACH step: Read both reference docs, check current state
  - After EACH step: Verify success, test results, confirm before proceeding
  - Use ONLY commands/code from official Supabase docs referenced in the guides
  - Terminal commands must be executed in the working directory

implementation_steps:
  1. Verify project state (Testing table structure, installed extensions)
  2. Enable pg_cron and pg_net extensions via migration
  3. Create Edge Function directory and index.ts file
  4. Set environment variables (OpenAI, Resend, email recipients)
  5. Store service role key in vault
  6. Create pg_cron schedule via migration
  7. Deploy edge function to production
  8. Test the function manually
  9. Monitor execution and verify cron job

step_format:
  - State: "Step X of 9: [current task]"
  - Review: Check reference docs for this step
  - Execute: Run command/create file
  - Verify: Test and confirm success
  - Summary: Brief result and next step

error_handling:
  - Check troubleshooting section in reference docs
  - Do NOT improvise fixes or workarounds
  - Stop and report if step fails

success_criteria:
  - All extensions enabled
  - Edge function deployed
  - Cron job scheduled for 9 AM daily
  - Test execution successful

BEGIN: Step 1 - Verify current project state
```