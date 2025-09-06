drop extension if exists "pg_net";

drop policy "Enable all operations for authenticated users" on "public"."pages";

alter table "public"."pages" drop constraint "pages_url_key";

drop index if exists "public"."idx_pages_url";

drop index if exists "public"."pages_url_key";

alter table "public"."pages" drop column "created_at";

alter table "public"."pages" add column "summary" text;

alter table "public"."pages" add column "title" text;

alter table "public"."pages" disable row level security;


