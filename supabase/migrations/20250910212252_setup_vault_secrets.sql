-- Store secrets securely for pg_cron access
-- Docs: https://supabase.com/docs/guides/database/vault

-- Store the Edge Function URL for pg_cron to call
SELECT vault.create_secret('https://ygthtpoydaxupxxuflym.supabase.co/functions/v1/daily-report', 'daily_report_url');

-- Store the service role key for authentication
SELECT vault.create_secret('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlndGh0cG95ZGF4dXB4eHVmbHltIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzEwOTk2OSwiZXhwIjoyMDcyNjg1OTY5fQ.AWnjcsd4SSKRwPVU-uL1E6gC73mSRBVizf7sdkLOsBE', 'service_role_key');