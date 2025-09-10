# Daily AI Reporting Implementation Prompt

## What We're Doing

We're adding an intelligent daily reporting layer to our existing Crawl4AI web scraping system that operates completely independently of the current Python crawler. Our `testing` table already collects web data with LLM-extracted insights throughout the day from various sources. Now, we'll create a Supabase Edge Function that runs automatically every morning at 9 AM using pg_cron scheduling, queries the last 24 hours of crawled data from the `testing` table, aggregates all the `extracted_data` JSONB fields, and sends this collective intelligence to an AI service (OpenAI/Anthropic) for meta-analysis to identify patterns, trends, anomalies, and generate actionable business insights. The AI will produce a comprehensive daily report that gets formatted and emailed using Resend to stakeholders. This approach requires zero modifications to our Python Crawl4AI codebase or database schema - it's a pure addition using Supabase's native scheduling and serverless functions, effectively transforming our raw crawl data into daily business intelligence reports without disrupting the existing workflow.

## MCP Tools Required

### File System Operations
- `mcp_filesystem_list_directory` - Map current codebase structure
- `mcp_filesystem_read_text_file` - Read migration files and config
- `mcp_filesystem_create_directory` - Create function directories
- `mcp_filesystem_write_file` - Write new files

### Supabase Operations
- `mcp_supabase2_list_tables` - Inspect current table structure
- `mcp_supabase2_execute_sql` - Query testing table schema
- `mcp_supabase2_apply_migration` - Apply pg_cron and scheduling migrations
- `mcp_supabase2_deploy_edge_function` - Deploy the daily report function
- `mcp_supabase2_list_migrations` - Review existing migrations
- `mcp_supabase2_get_logs` - Monitor function execution
- `mcp_supabase2_get_project_url` - Get project endpoints
- `mcp_supabase2_search_docs` - Find specific documentation

### Research & Documentation
- `mcp_mcp-omnisearc_perplexity_search` - Research AI integration patterns
- `mcp_mcp-omnisearc_brave_search` - Find official documentation
- `mcp_mcp-omnisearc_tavily_search` - Verify implementation approaches

### Analysis & Planning
- `mcp_sequential-th_sequentialthinking` - Break down complex implementation steps

## Step-by-Step Implementation Guide

### Step 1: Environment & Current State Analysis
**Objective**: Understand our current setup and table structure
**Tools**: `mcp_filesystem_list_directory`, `mcp_filesystem_read_text_file`, `mcp_supabase2_list_tables`, `mcp_supabase2_execute_sql`
**Actions**:
- Map the current supabase directory structure
- Read the latest migration file to understand testing table schema
- Query the testing table to see actual data structure
- Identify the extracted_data JSONB format

**Official References**:
- [Supabase Table Management](https://supabase.com/docs/guides/database/tables)
- [JSONB Data Types](https://supabase.com/docs/guides/database/json)

### Step 2: Enable pg_cron Extension
**Objective**: Enable scheduled jobs capability in Supabase
**Tools**: `mcp_supabase2_apply_migration`, `mcp_supabase2_search_docs`
**Actions**:
- Research pg_cron extension in Supabase docs
- Create migration to enable pg_cron
- Verify extension is available and working

**Official References**:
- [pg_cron Extension Guide](https://supabase.com/docs/guides/database/extensions/pg_cron)
- [Database Extensions](https://supabase.com/docs/guides/database/extensions)

### Step 3: Create Edge Function Structure
**Objective**: Set up the TypeScript Edge Function for daily reporting
**Tools**: `mcp_filesystem_create_directory`, `mcp_filesystem_write_file`, `mcp_supabase2_search_docs`
**Actions**:
- Create supabase/functions/daily-report directory
- Write index.ts with proper Deno imports
- Set up basic function structure for querying and AI integration
- Configure environment variables handling

**Official References**:
- [Edge Functions Quickstart](https://supabase.com/docs/guides/functions/quickstart)
- [Local Development](https://supabase.com/docs/guides/functions/local-development)
- [Environment Variables](https://supabase.com/docs/guides/functions/secrets)

### Step 4: Implement Data Query Logic
**Objective**: Query testing table for last 24 hours of data
**Tools**: `mcp_filesystem_write_file`, `mcp_supabase2_search_docs`
**Actions**:
- Add Supabase client initialization in Edge Function
- Implement query to select last 24 hours from testing table
- Extract and aggregate extracted_data JSONB fields
- Add error handling and logging

**Official References**:
- [Supabase Client in Edge Functions](https://supabase.com/docs/guides/functions/connect-to-postgres)
- [Querying JSONB](https://supabase.com/docs/guides/database/json#querying-json-data)

### Step 5: AI Integration Setup
**Objective**: Send aggregated data to AI service for analysis
**Tools**: `mcp_mcp-omnisearc_perplexity_search`, `mcp_filesystem_write_file`
**Actions**:
- Research OpenAI/Anthropic API integration patterns
- Add AI service API calls to Edge Function
- Design prompt for daily report generation
- Handle API responses and error cases

**Official References**:
- [Calling External APIs](https://supabase.com/docs/guides/functions/examples/call-external-api)
- [HTTP Requests in Edge Functions](https://supabase.com/docs/guides/functions/examples/stripe-webhooks)

### Step 6: Email Integration with Resend
**Objective**: Send formatted AI reports via email
**Tools**: `mcp_filesystem_write_file`, `mcp_supabase2_search_docs`
**Actions**:
- Set up Resend API integration
- Create HTML email template for reports
- Add email sending logic to Edge Function
- Configure recipient lists and error handling

**Official References**:
- [Sending Emails with Resend](https://supabase.com/docs/guides/functions/examples/send-emails)
- [Email Templates](https://resend.com/docs/send-with-nodejs)

### Step 7: Schedule Daily Execution
**Objective**: Create pg_cron job to run function daily at 9 AM
**Tools**: `mcp_supabase2_apply_migration`, `mcp_supabase2_execute_sql`
**Actions**:
- Create migration with pg_cron schedule
- Set up HTTP POST to Edge Function endpoint
- Configure proper authentication for scheduled calls
- Test scheduling configuration

**Official References**:
- [Scheduled Functions](https://supabase.com/docs/guides/functions/schedule-functions)
- [Database Webhooks](https://supabase.com/docs/guides/database/webhooks)

### Step 8: Deploy and Test
**Objective**: Deploy function and verify end-to-end workflow
**Tools**: `mcp_supabase2_deploy_edge_function`, `mcp_supabase2_get_logs`
**Actions**:
- Deploy Edge Function to Supabase
- Apply all migrations
- Test manual function execution
- Verify scheduled execution
- Monitor logs and debug issues

**Official References**:
- [Deploying Functions](https://supabase.com/docs/guides/functions/deploy)
- [Function Logs](https://supabase.com/docs/guides/functions/logging)
- [Debugging](https://supabase.com/docs/guides/functions/debugging)

### Step 9: Monitoring and Maintenance
**Objective**: Set up ongoing monitoring of the reporting system
**Tools**: `mcp_supabase2_get_logs`, `mcp_supabase2_execute_sql`
**Actions**:
- Create queries to monitor pg_cron job status
- Set up function execution monitoring
- Document troubleshooting procedures
- Plan for scaling and optimization

**Official References**:
- [Monitoring pg_cron](https://supabase.com/docs/guides/database/extensions/pg_cron#monitoring-cron-jobs)
- [Function Observability](https://supabase.com/docs/guides/functions/observability)

## Key Design Principles

1. **Zero Python Changes**: The reporting system operates entirely within Supabase infrastructure
2. **Non-Intrusive**: No modifications to existing testing table or crawler workflow
3. **Scalable**: Built on Supabase's serverless architecture
4. **Maintainable**: Uses official Supabase patterns and best practices
5. **Reliable**: Includes proper error handling, logging, and monitoring

## Expected Deliverables

1. **New Migration Files**:
   - `enable_pgcron_extension.sql`
   - `schedule_daily_report.sql`

2. **New Edge Function**:
   - `supabase/functions/daily-report/index.ts`
   - Supporting configuration and environment setup

3. **Documentation**:
   - Deployment instructions
   - Monitoring and troubleshooting guide
   - Sample report formats

## Success Criteria

- Daily reports are generated automatically at 9 AM
- Reports contain meaningful AI analysis of crawled data
- Email delivery is reliable and formatted properly
- System operates without affecting existing Crawl4AI workflow
- Proper logging and monitoring are in place for maintenance

---

*This prompt ensures a systematic, well-documented approach to adding AI reporting capabilities using only official Supabase tools and patterns.*
