# Supabase Chatbot Usage Guide

## Overview

The terminal chatbot provides an interactive interface to query and explore the crawled pages stored in your Supabase database. It offers a simple command-line interface with various search and data retrieval capabilities.

## Starting the Chatbot

```bash
# Navigate to the project directory
cd /home/ali/Documents/supa-crawl-LLM-playground

# Activate the virtual environment
source venv/bin/activate

# Run the chatbot
python -m chatbot.chatbot
```

## Available Commands

### 📋 Data Retrieval Commands

- **`latest`** - Show latest 5 pages
- **`latest N`** - Show latest N pages (e.g., `latest 10`)
- **`find <url>`** - Find page by exact URL match
- **`count`** - Show total number of pages in database
- **`summaries`** - Show pages with LLM-generated summaries
- **`content <id>`** - View full content of a specific page by ID

### 🔍 Search Commands

- **`search title <query>`** - Search pages by title (case-insensitive)
- **`search summary <query>`** - Search pages by summary content

### ℹ️ System Commands

- **`help`** - Show available commands and examples
- **`test`** - Test database connection
- **`quit`** / **`exit`** - Exit the chatbot

## Usage Examples

```bash
# Show help
query> help

# Get latest 3 pages
query> latest 3

# Find a specific page
query> find https://example.com

# Search for pages about Python
query> search title "python tutorial"

# Search summaries for machine learning content
query> search summary "machine learning"

# View full content of page with ID 5
query> content 5

# Count total pages
query> count

# Show pages that have summaries
query> summaries

# Test connection
query> test

# Exit the chatbot
query> quit
```

## Features

### Error Handling
- User-friendly error messages for invalid inputs
- Detailed logging for debugging (logged to console with timestamps)
- Graceful handling of database connection issues

### Content Display
- Truncated content display for readability
- Full content viewing via the `content` command
- Formatted output with emojis and clear structure
- Smart content truncation (2000 characters for full content view)

### Search Capabilities
- Case-insensitive search for titles and summaries
- Pattern matching using PostgreSQL's `ilike` operator
- Configurable result limits (default: 10 results)

### Performance
- Efficient queries using Supabase Python client
- Limited result sets to prevent overwhelming output
- Indexed database operations where applicable

## Database Schema

The chatbot works with the `pages` table schema:

```sql
CREATE TABLE pages (
  id bigint PRIMARY KEY GENERATED ALWAYS AS identity,
  url text NOT NULL,
  content text,
  summary text,
  title text
);
```

## Error Logging

All database errors are logged with full stack traces for debugging. Logs include:
- Timestamp
- Module name
- Log level
- Error message
- Exception details

## Requirements

- Python 3.13+
- Supabase Python client (`supabase>=2.18.1`)
- Active Supabase project with proper environment configuration
- Internet connection for database access

## Configuration

Ensure your `.env` file contains:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

## Troubleshooting

### Connection Issues
1. Verify your `.env` file has correct Supabase credentials
2. Test connection using the `test` command
3. Check network connectivity

### No Results Found
1. Verify data exists in your database using `count`
2. Try broader search terms
3. Check for typos in search queries

### Content Display Issues
1. Large content is automatically truncated for readability
2. Use the `content <id>` command for full content viewing
3. Content over 2000 characters will be truncated with a notice

### Logging Issues
1. Check console output for detailed error messages
2. Logging is configured automatically when the chatbot starts
3. Look for log entries with timestamps for debugging information