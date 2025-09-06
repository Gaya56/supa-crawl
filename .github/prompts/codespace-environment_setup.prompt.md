---
mode: agent
---

# Task: Set up the Crawl4AI and Supabase Environment

Your task is to set up the environment for a project that integrates Crawl4AI and Supabase in a GitHub Codespace. You must follow the instructions laid out in `/workspaces/codespaces-blank/.github/instructions/repo-build.instructions.md`.

**Guiding Principles:**

*   **Use all available MCP servers (`mcp_*` tools) at every step** to interact with the environment, search for information, and manage project resources.
*   **Strictly adhere to official documentation.** All code and commands must be sourced from the official documentation.
    *   **Crawl4AI:** `https://docs.crawl4ai.com/`
    *   **Supabase:** `https://supabase.com/docs`
*   **Reference your sources.** When you use a command or code snippet, mention the official documentation page you got it from.
*   **The user has provided environment variables in `.env`**. You must use them for Supabase and OpenAI credentials.

**Execution Steps:**

**Step 1: Initialize the Codespaces Environment**

1.  **Install Crawl4AI:**
    *   Install the `crawl4ai` python package using `pip`.
    *   Run `crawl4ai-setup` to install Playwright browsers.
    *   Verify the installation.

2.  **Install Supabase CLI:**
    *   Install the `supabase` npm package.
    *   Initialize a new Supabase project which will create a `supabase/` directory.
    *   Verify the installation.

**Step 2: Link to Supabase Project and Create Database Table**

1.  **Log in to Supabase:**
    *   Use the Supabase CLI to log in. You will need to provide the access token. Since this is an automated environment, you may need to find a way to handle the browser-based login or use a token if available. Let's assume for now you can get the token.

2.  **Link Supabase Project:**
    *   The user has provided the Supabase project URL in the `.env` file. You need to extract the project reference ID from the URL (`ygthtpoydaxupxxuflym`).
    *   Link the local Supabase configuration to the remote project using the project reference.

3.  **Create Database Table:**
    *   Create a new SQL migration file.
    *   Add the SQL command to create a `pages` table with `id`, `url`, and `content` columns.
    *   Apply the migration to the remote database.
    *   Verify that the table was created successfully.
