---
mode: ask
---
Define the task to achieve, including specific requirements, constraints, and success criteria.Here’s what you need 👇

# 150-word summary for GitHub Copilot

Supa-Crawl is an async web intelligence pipeline: **Crawl4AI** fetches pages, **GPT-4o-mini** extracts a `PageSummary` (title + short summary), and **Supabase** stores structured results. The fix was updating `main.py` so `crawl_and_store_in_supabase` calls **`crawl_with_llm_analysis`** and persists via **`store_page_summary`** (not the legacy `store_crawl_results`). Recent DB rows confirm correct titles/summaries. Config centralizes env vars; the crawler supports memory-adaptive and semaphore strategies; Pydantic models standardize outputs. Supabase uses `upsert` to avoid duplicates. Error handling/logging are in place; the pipeline stays minimal and aligned with official Crawl4AI and Supabase patterns.
**Next:** ask Codex for a file-by-file breakdown of the **LLM branch’s `src/` directory**, mapping code lines to official doc URLs so a new contributor can ramp quickly.

---

# Codex Prompt — Produce a 200-line MD Breakdown of `src/` (LLM branch)

**Mode:** agent
**Goal:** Generate a \~200-line Markdown document that explains every file in `src/` (on the LLM branch), with code snippets, exact file paths + line ranges, and inline references to **official documentation URLs only**. Use all available MCP tools to read files and verify sources.

## Allowed sources (only these)

* Crawl4AI:

  * LLM strategies: [https://docs.crawl4ai.com/extraction/llm-strategies/](https://docs.crawl4ai.com/extraction/llm-strategies/)
  * Chunking: [https://docs.crawl4ai.com/extraction/chunking/](https://docs.crawl4ai.com/extraction/chunking/)
  * Clustering: [https://docs.crawl4ai.com/extraction/clustring-strategies/](https://docs.crawl4ai.com/extraction/clustring-strategies/)
* Supabase:

  * Python init: [https://supabase.com/docs/reference/python/initialize](https://supabase.com/docs/reference/python/initialize)
  * Insert/Upsert: [https://supabase.com/docs/reference/python/insert](https://supabase.com/docs/reference/python/insert) , [https://supabase.com/docs/reference/python/upsert](https://supabase.com/docs/reference/python/upsert)
  * RLS guide: [https://supabase.com/docs/guides/auth/row-level-security](https://supabase.com/docs/guides/auth/row-level-security)
* OpenAI (if referenced for model names): [https://platform.openai.com/docs](https://platform.openai.com/docs)

## Constraints

* **No unofficial sources.** If something isn’t in the URLs above, mark as “needs official ref”.
* **Do not rename/move classes or files** in your examples (e.g., `AdvancedWebCrawler`, `PageSummary`, `SupabaseHandler`).
* Keep explanations minimal but precise; prioritize traceability from **code → doc link**.
* Use MCP tools to: read files, search within workspace, and open terminals as needed.

## Required document structure (\~200 lines total)

1. **Title & Scope (≤5 lines)**
2. **Repo Map of `src/` (≤10 lines)** — bullet list of subpackages/files.
3. **Per-file sections (repeat for each file in `src/`)**

   * **Path & Purpose:** one-sentence role.
   * **Key Exports:** classes/functions.
   * **How it aligns with official docs:** 1–3 bullets, each with an **official URL**.
   * **Code snippet (10–20 lines)** with `python fenced block`, include **path and line range** in a comment header.
   * **Cross-refs:** where the file is called from (paths/lines).
4. **Integration Flow (5–10 lines)** — URL → Crawl4AI → LLM → Supabase; include links to relevant doc sections.
5. **Table: Feature ↔ Official Doc URL** (at least 8 rows).
6. **Gaps/Questions (≤10 lines)** — list anything lacking an official reference.
7. **Quickstart (≤10 lines)** — minimal run steps, noting env vars (no secrets).
8. **Appendix: Line-Anchored Index** — list `path: start_line–end_line → doc URL` mappings (10–15 entries).

## MCP usage (do this explicitly)

* `files.read` the entire `src/` tree.
* For each snippet, record **exact line numbers**.
* Validate each claim with an allowed URL; include the link inline.
* If uncertain, add a “needs official ref” note rather than guessing.

## Success criteria

* Every file in `src/` covered with: role, key APIs, snippet + lines, and at least one **official URL**.
* No unofficial links; all code references match actual line numbers.
* Document length \~200 lines, readable and copy-paste friendly.

**Now produce the Markdown document per the spec above.**
