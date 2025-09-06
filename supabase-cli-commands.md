# 🚀 Supabase CLI Commands - Complete Reference

## 📥 Installation Commands

### Download and Install Supabase CLI (GitHub Release Method)
```bash
# Download official binary from GitHub releases
wget -O supabase_linux_amd64.tar.gz "https://github.com/supabase/cli/releases/download/v2.39.2/supabase_linux_amd64.tar.gz"

# Extract to separate directory
mkdir -p supabase-cli && tar -xzf supabase_linux_amd64.tar.gz -C supabase-cli

# Install to local bin (persists across Codespace sessions)
mkdir -p $HOME/.local/bin && cp supabase-cli/supabase $HOME/.local/bin/

# Make it permanent in PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Clean up temporary files
rm -rf supabase-cli supabase_linux_amd64.tar.gz
```

### Verify Installation
```bash
# Check version
supabase --version

# Check if CLI is available
which supabase
```

## 🔐 Authentication Commands

### Login to Supabase CLI
```bash
# Interactive login (opens browser)
supabase login

# Login with no browser (manual token entry)
supabase login --no-browser

# Login with personal access token directly
supabase login --token sbp_your_personal_access_token_here

# Alternative: Set environment variable
export SUPABASE_ACCESS_TOKEN="sbp_your_personal_access_token_here"
```

### Logout
```bash
# Logout interactively
supabase logout

# Force logout
supabase logout --yes
```

### Check Authentication Status
```bash
# List projects (works only if authenticated)
supabase projects list
```

## 🗂️ Project Management Commands

### List All Projects
```bash
supabase projects list
```

### Navigate to Project Directory
```bash
cd /workspaces/codespaces-blank/supabase
```

## 🔄 Migration Commands

### View Migration Status
```bash
supabase migration list
```

### Repair Migration Issues
```bash
# Repair specific migration
supabase migration repair --status reverted 20250906034456
supabase migration repair --status reverted 20250906034506

# Check status after repair
supabase migration list
```

### Pull Database Schema from Remote
```bash
supabase db pull
```

## 📊 Database Inspection Commands

### View All Table Data
```bash
# Dump all data from public schema
supabase db dump --data-only --schema public

# Save data to file
supabase db dump --data-only --schema public > my_table_data.sql
```

### View Table Structure Only
```bash
# Get schema structure
supabase db dump --schema public

# View just table creation statements
supabase db dump --schema public | grep -A 10 "CREATE TABLE"
```

### View Specific Data Portions
```bash
# View first 50 lines of data
supabase db dump --data-only --schema public | head -50

# View last 20 lines of data
supabase db dump --data-only --schema public | tail -20

# Count total INSERT statements (rows)
supabase db dump --data-only --schema public | grep -c "INSERT INTO"

# View first 3 data rows
supabase db dump --data-only --schema public | grep "INSERT INTO" | head -3

# View last 3 data rows
supabase db dump --data-only --schema public | grep "INSERT INTO" | tail -3
```

### View Other Schemas
```bash
# View auth schema structure
supabase db dump --schema auth | head -20

# View storage schema
supabase db dump --schema storage | head -20
```

### Dry Run Commands (See what would execute)
```bash
# See what dump command would do without executing
supabase db dump --dry-run
```

## 📁 Local File Inspection

### View Migration Files
```bash
# List migration files
ls -la migrations/

# View contents of all migrations
cat migrations/*.sql

# View specific migration
cat migrations/20250905230727_create_pages_table.sql
```

### View Project Configuration
```bash
# View Supabase config
cat config.toml

# View first 20 lines of config
cat config.toml | head -20
```

## 🔍 Project Information Commands

### View Current Directory Structure
```bash
# Current directory
pwd

# List files in current directory
ls -la

# List files in supabase directory
ls -la /workspaces/codespaces-blank/supabase/
```

### View Project Status
```bash
# Note: This works for local development, not remote projects
supabase status
```

## 🛠️ Troubleshooting Commands

### Debug Mode
```bash
# Run any command with debug output
supabase [command] --debug
```

### Help Commands
```bash
# General help
supabase --help

# Help for specific commands
supabase login --help
supabase db --help
supabase migration --help
supabase projects --help
```

## 📋 Quick Reference Summary

### Essential Daily Commands
```bash
# 1. Navigate to project
cd /workspaces/codespaces-blank/supabase

# 2. Check authentication
supabase projects list

# 3. View your data
supabase db dump --data-only --schema public

# 4. Check migrations
supabase migration list

# 5. Pull latest schema changes
supabase db pull
```

### Project Details Discovered
- **Project Name**: Market Predictions
- **Project ID**: ygthtpoydaxupxxuflym
- **Region**: West US (North California)
- **Main Table**: `pages` (id, url, content, summary, title)
- **Total Records**: 26 entries
- **Data Type**: Web crawling results with AI summaries

## 🔑 Important Notes

1. **Two Types of Keys**:
   - `SUPABASE_KEY` in `.env` = Project anon key (for app API calls)
   - Personal access token = For CLI authentication (starts with `sbp_`)

2. **Installation Persistence**:
   - CLI installed in `$HOME/.local/bin/` persists across Codespace restarts
   - PATH added to `~/.bashrc` for permanent availability

3. **Authentication**:
   - Use `supabase login` for interactive authentication
   - Personal access tokens start with `sbp_` not `eyJ...`
   - Project anon keys (`eyJ...`) are for application API calls, not CLI

4. **Migration Management**:
   - Always run migrations from `/workspaces/codespaces-blank/supabase/` directory
   - Use `supabase migration repair` to fix history conflicts
   - Pull schema changes with `supabase db pull`

---
*Generated on: September 6, 2025*
*Supabase CLI Version: 2.39.2*
