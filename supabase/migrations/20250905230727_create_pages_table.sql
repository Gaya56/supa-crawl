-- Create a table for storing crawled web pages
create table pages (
  id bigint primary key generated always as identity,
  url text not null unique,
  content text,
  created_at timestamptz default now()
);

-- Enable Row Level Security (RLS)
alter table pages enable row level security;

-- Create a policy that allows all operations for authenticated users
create policy "Enable all operations for authenticated users" on pages
  for all using (auth.role() = 'authenticated');

-- Create an index on the url column for faster lookups
create index idx_pages_url on pages(url);