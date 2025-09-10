# Architecture Alignment Resolution Prompt

## Overview

**Objective**: Resolve the architectural mismatch between current general web crawler code and prediction market table schema through systematic analysis and micro-changes.

**Current Conflict**: 
- Code expects: `url`, `content`, `title`, `summary` (general web crawling)
- Table schema: `id`, `source_url`, `website_name`, `bet_title`, `odds`, `summary`, `timestamp` (prediction market)

**Safety Protocol**: One micro-change at a time, user approval required, validate with `python main.py` after each change.

## Decision Framework

Execute **Step 1-3** to gather context, then present **Option A** or **Option B** to user for architectural direction.

---

## Step 1: Repository Context Analysis

### MCP Tools Usage (ALL REQUIRED)
- **File System**: Map current codebase structure and identify all files requiring changes
- **Brave Search**: Research official Crawl4AI and Supabase documentation patterns  
- **Memory**: Track analysis findings and decision points
- **Supabase**: Query current table structure and validate schema
- **Sequential Thinking**: Break down the architectural analysis into logical components
- **Pylance**: Analyze Python code dependencies and type relationships

### Actions
1. **File System**: Use `mcp_filesystem_directory_tree` to map repository structure
2. **Pylance**: Use `mcp_pylance_mcp_s_pylanceWorkspaceUserFiles` to identify all Python files
3. **File System**: Read all schema-dependent files:
   - `/workspaces/supa-crawl/src/storage/supabase_handler.py`
   - `/workspaces/supa-crawl/src/models/schemas.py` 
   - `/workspaces/supa-crawl/src/crawlers/async_crawler.py`
   - `/workspaces/supa-crawl/.github/prompts/Table-Build.prompt.md`
4. **Supabase**: Use `mcp_supabase_list_tables` and `mcp_supabase_execute_sql` to validate current Testing table schema
5. **Memory**: Use `mcp_memory_create_entities` to track:
   - Current code expectations vs table schema
   - Files requiring modification for each approach
   - Official documentation references
6. **Sequential Thinking**: Use `mcp_sequential-th_sequentialthinking` to analyze:
   - Impact scope for Option A vs Option B
   - Risk assessment for each approach
   - Migration complexity estimation

### Deliverable
Complete inventory of:
- Current code dependencies on schema fields
- Table schema requirements from Table-Build.prompt.md
- Files that need modification for each option
- Complexity assessment for both approaches

---

## Step 2: Official Documentation Research

### MCP Tools Usage (ALL REQUIRED)
- **Brave Search**: Research official patterns for both approaches
- **Supabase**: Query documentation tables if available
- **Memory**: Store official patterns and best practices
- **File System**: Check existing documentation in `/workspaces/supa-crawl/docs/`
- **Sequential Thinking**: Evaluate official patterns against our use case
- **Pylance**: Validate type compatibility with official patterns

### Actions
1. **Brave Search**: Use `mcp_brave-search_brave_web_search` to find:
   - "Crawl4AI LLM extraction schema custom fields site:docs.crawl4ai.com"
   - "Supabase table schema migration best practices site:supabase.com"
   - "Crawl4AI prediction market scraping examples"
   - "Supabase PostgreSQL column rename migration"
2. **Supabase**: Use `mcp_supabase_search_docs` with GraphQL queries:
   ```graphql
   query {
     searchDocs(query: "table migration rename column") {
       nodes {
         title
         href  
         content
       }
     }
   }
   ```
3. **File System**: Use `mcp_filesystem_read_multiple_files` to read existing documentation
4. **Memory**: Use `mcp_memory_add_observations` to store official patterns
5. **Sequential Thinking**: Analyze official patterns for feasibility and risk

### Deliverable  
Official documentation references for:
- Crawl4AI custom schema extraction patterns
- Supabase migration best practices
- Recommended approach based on official guidelines

---

## Step 3: Impact Analysis & Recommendation

### MCP Tools Usage (ALL REQUIRED)
- **Sequential Thinking**: Comprehensive impact analysis for both options
- **Memory**: Retrieve all previous analysis data
- **Pylance**: Analyze code dependencies and type impacts
- **File System**: Assess file modification requirements
- **Supabase**: Validate migration feasibility
- **Brave Search**: Final validation against official best practices

### Actions
1. **Sequential Thinking**: Use `mcp_sequential-th_sequentialthinking` to evaluate:
   - Option A: Convert to prediction market scraper (modify code to match table)
   - Option B: Align table with general web crawler (modify table to match code)
   - Risk, complexity, and maintainability for each
2. **Memory**: Use `mcp_memory_search_nodes` to compile all analysis findings
3. **Pylance**: Use `mcp_pylance_mcp_s_pylanceFileSyntaxErrors` to check current code health
4. **Supabase**: Validate current data and migration safety

### Deliverable
Present both options to user with:
- Clear pros/cons for each approach  
- Estimated complexity and risk level
- Official documentation support
- Recommended approach with justification

---

## Option A: Convert to Prediction Market Scraper

**Scope**: Modify crawler code to extract prediction market data matching current table schema.

### Phase A1: Schema Alignment (Micro-change 1)

#### MCP Tools Usage
- **File System**: Read current schemas.py for modification planning
- **Brave Search**: Research Crawl4AI custom field extraction patterns
- **Memory**: Track schema changes and validation requirements
- **Sequential Thinking**: Plan minimal schema modification approach  
- **Pylance**: Validate new schema types and imports
- **Supabase**: Confirm table schema compatibility

#### Actions
1. **Propose Schema Update**:
   - Create new `PredictionMarketResult` schema in `/workspaces/supa-crawl/src/models/schemas.py`
   - Add fields: `bet_title`, `odds`, `website_name`, `source_url`, `summary`
   - Include Pydantic validation and field descriptions
   - **Get user approval before implementing**

2. **Implementation**: 
   - Use `mcp_filesystem_edit_file` to add schema
   - Reference official Crawl4AI schema patterns: https://docs.crawl4ai.com/extraction/llm-strategies/

3. **Validation**:
   - Use `mcp_pylance_mcp_s_pylanceFileSyntaxErrors` to check syntax
   - Run `python main.py` to ensure no breaking changes
   - **If errors: revert immediately and propose smaller change**

### Phase A2: LLM Extraction Strategy Update (Micro-change 2)

#### MCP Tools Usage  
- **Brave Search**: Research prediction market data extraction prompts
- **File System**: Modify async_crawler.py LLM strategy
- **Memory**: Track LLM prompt engineering decisions
- **Sequential Thinking**: Design extraction logic for prediction market fields
- **Pylance**: Validate LLM strategy integration
- **Supabase**: Test extracted data compatibility

#### Actions
1. **Propose LLM Strategy Update**:
   - Modify `crawl_with_llm_analysis()` in `/workspaces/supa-crawl/src/crawlers/async_crawler.py`
   - Update extraction instruction to target prediction market elements
   - Use new `PredictionMarketResult` schema
   - **Get user approval before implementing**

2. **Implementation**:
   - Update LLM instruction prompt for prediction market extraction
   - Reference official pattern: https://docs.crawl4ai.com/extraction/llm-strategies/

3. **Validation**:
   - Run `python main.py` with test prediction market URL
   - Verify extracted data matches expected schema
   - **If errors: revert and propose smaller fix**

### Phase A3: Storage Handler Update (Micro-change 3)

#### MCP Tools Usage
- **File System**: Modify supabase_handler.py storage methods
- **Supabase**: Validate database insertion with new schema
- **Memory**: Track storage method changes
- **Sequential Thinking**: Plan storage method alignment
- **Pylance**: Validate method signatures and types
- **Brave Search**: Research Supabase upsert patterns for new fields

#### Actions
1. **Propose Storage Method Update**:
   - Modify `store_page_summary()` in `/workspaces/supa-crawl/src/storage/supabase_handler.py`
   - Update method to handle prediction market fields
   - Map new schema fields to table columns
   - **Get user approval before implementing**

2. **Implementation**:
   - Update storage method signatures and field mapping
   - Reference official Supabase patterns: https://supabase.com/docs/reference/python/upsert

3. **Validation**:
   - Run `python main.py` with complete pipeline
   - Verify data is correctly stored in Testing table
   - **If errors: revert and propose smaller fix**

---

## Option B: Align Table with General Web Crawler

**Scope**: Modify table schema to match current crawler code expectations.

### Phase B1: Migration Planning (Micro-change 1)

#### MCP Tools Usage
- **Supabase**: Analyze current table data and structure
- **Brave Search**: Research Supabase migration best practices
- **Memory**: Track migration requirements and data preservation needs
- **Sequential Thinking**: Plan safe migration strategy
- **File System**: Create migration file structure
- **Pylance**: Validate migration safety

#### Actions
1. **Propose Migration Strategy**:
   - Create new migration to rename/add columns: `bet_title` → `title`, `source_url` → `url`, add `content` column
   - Preserve existing data where possible
   - Plan rollback strategy
   - **Get user approval before implementing**

2. **Implementation**:
   - Use `mcp_supabase_apply_migration` to create migration file
   - Reference official migration patterns: https://supabase.com/docs/guides/cli/migrations

3. **Validation**:
   - Test migration on local database first
   - Verify data integrity after migration
   - **If errors: rollback immediately and propose smaller change**

### Phase B2: Code Validation (Micro-change 2)

#### MCP Tools Usage
- **Pylance**: Validate code compatibility with new table schema
- **File System**: Review all storage handler methods
- **Memory**: Track code validation results
- **Sequential Thinking**: Identify any remaining mismatches
- **Supabase**: Test database operations with new schema
- **Brave Search**: Research any additional compatibility requirements

#### Actions
1. **Propose Code Review**:
   - Verify `supabase_handler.py` methods work with new table schema
   - Update any hardcoded column references
   - **Get user approval before implementing any changes**

2. **Implementation**:
   - Make minimal adjustments to ensure compatibility
   - Reference current working code patterns

3. **Validation**:
   - Run `python main.py` with complete pipeline
   - Verify all functionality works as expected
   - **If errors: revert and propose smaller fix**

---

## Execution Protocol

### Before Each Micro-change
1. **All 6 MCP Tools**: Gather context and validate approach
2. **Present Proposal**: Exact files, lines, and changes with rationale
3. **Official References**: Include Crawl4AI and Supabase documentation URLs  
4. **Wait for Approval**: Do not proceed without explicit user confirmation

### After Each Micro-change  
1. **Validation**: Run `python main.py` from `/workspaces/supa-crawl`
2. **Error Handling**: If ANY errors occur, immediately revert and report
3. **Documentation**: Update memory with what was changed and why
4. **Next Step**: Propose next micro-change or declare completion

### Safety Checkpoints
- ✅ Never modify multiple files simultaneously
- ✅ Always get user approval before applying changes
- ✅ Always run `python main.py` after changes
- ✅ Immediately revert if any errors occur
- ✅ Reference only official documentation
- ✅ Use all 6 MCP tools for every step
- ✅ Document every decision and change

### Completion Criteria
- All code runs without errors (`python main.py` succeeds)
- Schema and code are fully aligned
- All functionality validated end-to-end
- User confirms satisfaction with chosen approach
- Documentation updated to reflect final architecture

---

## Emergency Protocols

**If Errors Occur**:
1. Immediately revert the last change
2. Report exact error output to user  
3. Use Sequential Thinking to analyze error cause
4. Propose smaller, safer alternative approach
5. Get user approval before proceeding

**If Uncertain**:
1. Stop and ask user for clarification
2. Use Memory to review previous decisions
3. Research official documentation for guidance
4. Present options to user rather than guessing

**If Complex Issues Arise**:
1. Break down into smaller micro-changes
2. Use all MCP tools to gather more context
3. Present simplified alternative approaches
4. Get user guidance on priority and direction

This prompt ensures systematic resolution of the architectural conflict while maintaining strict safety protocols and leveraging all available MCP tools for comprehensive analysis and implementation.