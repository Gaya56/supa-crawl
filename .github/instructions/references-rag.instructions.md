---
applyTo: '*/workspaces/supa-crawl*'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

title: "Copilot Agent Rules"

- --

## Purpose

Make **one small, reversible change at a time**, confirm with the user **before** applying, and **run `python main.py`** after every change to verify nothing breaks.

## Authoritative Sources

- **Only official docs** (Crawl4AI, Supabase). Include URLs for every suggestion.
- **Cross-check against the repo** (current files/paths/lines) before proposing.

## Data References (Supabase)

Two tables with identical schema: `id`, `url`, `content`, `summary`, `title`

- `Crawl4AI-Docs`
- `Supabase-Docs`

Use `url` to open the doc and `summary` to understand scope.

## MCP Tools (use before, during, after each step)

- **MCP File System**: Navigate and search repository files to understand structure and existing code.
- **MCP Brave Search**: Look up official documentation and references for accurate information.
- **MCP Memory**: Track conversation history and previous decisions for consistency.
- **MCP Supabase**: Query database tables to understand data structure and content.
- **MCP Sequential Thinking**: Break down complex problems into step-by-step solutions.
- **MCP Pylance**: Analyze Python code for type information and potential issues.

Use ALL SIX tools for EVERY step - don't skip any tool!

## Implementation Loop (repeat)

1. **Understand & Locate**

- Search repo (File System + Pylance).

- Query tables (Supabase) → pick relevant `url`; open official doc (Brave).

2. **Propose**

- Draft **minimal diff** (file path + exact lines).

- Add 1–3 sentence rationale + **official links**.

- **Ask for approval** before editing.

3. **Apply**

- After approval, modify exactly one file/area.

4. **Validate**

- From `/workspaces/supa-crawl`, run: `python main.py`

- If errors: **revert**, report error/output, propose a smaller fix.

5. **Summarize**

- Short step summary + links used + next micro-step.

## Safety Policies

- 🔒 **One change at a time** – never edit multiple files or large sections at once.
- ✅ **Always confirm with us first** before applying any change.
- 🧪 **Run `python main.py` after each change** to confirm functionality.
- ♻️ **Revert immediately** if errors appear, then propose a smaller fix.
- 📑 **Document every step** – what was changed, why, and official link references.
- ⏸️ **Stop and wait for approval** if something is unclear or if multiple options exist.
- 🔍 **Cross-check repo + Supabase tables** before proposing new code.
- 📝 **Commit message template**: `chore|fix|feat(scope): brief reason — refs: <official URL>`

Would you like me to also create a shorter “quick-rules” version (just the safety bullets) for faster reference inside your repo?