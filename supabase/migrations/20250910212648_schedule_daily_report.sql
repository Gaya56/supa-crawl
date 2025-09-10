-- Schedule daily report at 9 AM
-- Docs: https://supabase.com/docs/guides/functions/schedule-functions

SELECT cron.schedule(
  'daily-prediction-report',    -- job name
  '0 9 * * *',                 -- 9 AM every day (UTC)
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