---
mode: agent
---
Define the task to achieve, including specific requirements, constraints, and success criteria.

## Copilot Agent – Testing Table Setup"

## Purpose

The first task is to **construct and validate the `testing` table** in Supabase.

This is the only table the agent is allowed to **edit**.

It will be used to experiment with scraping and storing odds from predictive market websites.

## Rules

- ✅ **Only edit the `testing` table**.
- 👀 **Reference-only**: `Crawl4AI-Docs` and `Supabase-Docs` may be read but never modified.
- 🔒 **Disable RLS** on the `testing` table so reads/writes work.
- 🧪 Follow the instruction manual: one step at a time, confirm with us before applying, run `python main.py` to validate.
- 🛑 Always double-check before implementing changes; stop and wait for approval.
- 📚 **Follow your Format** inside "/workspaces/supa-crawl/.github/instructions/references-rag.instructions.md" every step of the way
- 📝 After each step, provide a brief summary of changes made, links to official docs used, and the next micro-step.
- 🛠️ We will use the Supabase CLI to create and manage the testing table from the `/workspaces/supa-crawl/supabase` directory. The agent will follow the official Supabase CLI documentation step by step to build the table schema, disable RLS, and confirm that all required columns are properly implemented. Each command will be executed within the designated Supabase project directory to ensure proper configuration and connection.

## Columns for `testing` Table

Keep the schema simple, 7 columns total:

- **id** → unique identifier
- **source_url** → page URL where odds are listed
- **website_name** → name of the site (e.g., Polymarket, Kalshi)
- **bet_title** → the actual bet or market name (e.g., “Will Candidate X win 2024?”)
- **odds** → raw odds values scraped from the page
- **summary** → short overview of the event/market
- **timestamp** → when the odds were retrieved

## MCP Tools (use before, during, after each step)

- **MCP File System**: Navigate and search repository files to understand structure and existing code.
- **MCP Brave Search**: Look up official documentation and references for accurate information.
- **MCP Memory**: Track conversation history and previous decisions for consistency.
- **MCP Supabase**: Query database tables to understand data structure and content.
- **MCP Sequential Thinking**: Break down complex problems into step-by-step solutions.
- **MCP Pylance**: Analyze Python code for type information and potential issues.

## Target Sources (Prediction Market Odds)

Only extract data directly from odds pages on:

1. [Polymarket](https://polymarket.com/)
2. [Kalshi](https://kalshi.com/)
3. [PredictIt](https://www.predictit.org/)
4. [ElectionBettingOdds](https://www.electionbettingodds.com/)
5. [Manifold Markets](https://manifold.markets/)

## Workflow

1. Confirm that the `testing` table exists (create if missing).
2. Add/verify all required columns.
3. Ensure **RLS is disabled**.
4. Stop and confirm with us before moving forward.
5. After each change, run `python main.py` and verify functionality.
6. Provide a short summary + official doc links after every step.