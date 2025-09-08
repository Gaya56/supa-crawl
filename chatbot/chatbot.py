#!/usr/bin/env python3
"""
Terminal Chatbot for Supabase Pages Database
Following official Supabase Python client documentation and the supa-crawl project architecture.

Usage:
    python -m chatbot.chatbot
    
Commands:
    latest              - Show latest 5 pages
    latest N            - Show latest N pages
    find <url>          - Find page by URL
    search title <query> - Search pages by title
    search summary <query> - Search pages by summary content
    count               - Show total number of pages
    summaries           - Show pages with LLM summaries
    content <id>        - View full content of a specific page by ID
    help                - Show this help message
    quit/exit           - Exit the chatbot
"""
import sys
import os
from typing import Optional

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Supabase client not installed. Install with: pip install supabase")
    sys.exit(1)

from src.config.environment import env_config
from .queries import (
    latest_pages,
    find_page_by_url,
    search_pages_by_title,
    search_pages_by_summary,
    count_total_pages,
    get_pages_with_summaries,
    get_page_content,
    format_pages_list,
    format_page_result
)


class SupabaseChatbot:
    """
    Terminal chatbot for querying the Supabase pages database.
    """
    
    def __init__(self):
        """Initialize the chatbot with Supabase client."""
        self.client: Optional[Client] = None
        self._initialize_client()
        
    def _initialize_client(self) -> None:
        """
        Initialize Supabase client using the existing environment configuration.
        """
        if not env_config.has_supabase_config:
            print("❌ Supabase configuration missing!")
            print("Please ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file.")
            sys.exit(1)
        
        try:
            # Use the official Supabase client initialization pattern
            self.client = create_client(env_config.supabase_url, env_config.supabase_key)
            print(f"✓ Connected to Supabase: {env_config.supabase_url[:50]}...")
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {str(e)}")
            sys.exit(1)
    
    def test_connection(self) -> bool:
        """Test the Supabase connection."""
        try:
            response = self.client.table('pages').select('id').limit(1).execute()
            print("✓ Database connection verified")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False
    
    def show_help(self) -> None:
        """Display help message with available commands."""
        help_text = """
🤖 Supabase Pages Chatbot - Available Commands:

📋 Data Retrieval:
  latest              - Show latest 5 pages
  latest N            - Show latest N pages (e.g., 'latest 10')
  find <url>          - Find page by URL
  count               - Show total number of pages in database
  summaries           - Show pages with LLM-generated summaries
  content <id>        - View full content of a specific page by ID

🔍 Search Commands:
  search title <query>    - Search pages by title (case-insensitive)
  search summary <query>  - Search pages by summary content

ℹ️  System Commands:
  help                - Show this help message
  test                - Test database connection
  quit/exit           - Exit the chatbot

💡 Examples:
  > latest 3
  > find https://example.com
  > search title "python tutorial"
  > search summary "machine learning"
  > content 5
        """
        print(help_text)
    
    def handle_latest_command(self, parts: list) -> None:
        """Handle the 'latest' command with optional limit parameter."""
        limit = 5  # default
        
        if len(parts) > 1:
            try:
                limit = int(parts[1])
                if limit <= 0:
                    print("❌ Limit must be a positive number")
                    return
                if limit > 50:
                    print("⚠️  Limiting to 50 results for performance")
                    limit = 50
            except ValueError:
                print("❌ Invalid number format. Usage: latest [number]")
                return
        
        print(f"📊 Fetching latest {limit} pages...")
        pages = latest_pages(self.client, limit)
        print(format_pages_list(pages))
    
    def handle_find_command(self, parts: list) -> None:
        """Handle the 'find' command to search by URL."""
        if len(parts) < 2:
            print("❌ Usage: find <url>")
            return
        
        url = " ".join(parts[1:])  # Join in case URL has spaces
        print(f"🔍 Looking for page: {url}")
        
        page = find_page_by_url(self.client, url)
        if page:
            print(format_page_result(page, include_content=True))
        else:
            print("❌ Page not found")
    
    def handle_search_command(self, parts: list) -> None:
        """Handle search commands (title or summary)."""
        if len(parts) < 3:
            print("❌ Usage: search [title|summary] <query>")
            return
        
        search_type = parts[1].lower()
        query = " ".join(parts[2:])
        
        if search_type == "title":
            print(f"🔍 Searching titles for: '{query}'")
            pages = search_pages_by_title(self.client, query)
        elif search_type == "summary":
            print(f"🔍 Searching summaries for: '{query}'")
            pages = search_pages_by_summary(self.client, query)
        else:
            print("❌ Search type must be 'title' or 'summary'")
            return
        
        print(format_pages_list(pages))
    
    def handle_count_command(self) -> None:
        """Handle the 'count' command to show total pages."""
        print("📊 Counting pages...")
        total = count_total_pages(self.client)
        print(f"📈 Total pages in database: {total}")
    
    def handle_summaries_command(self) -> None:
        """Handle the 'summaries' command to show pages with LLM summaries."""
        print("📚 Fetching pages with summaries...")
        pages = get_pages_with_summaries(self.client)
        print(format_pages_list(pages))
    
    def handle_content_command(self, parts: list) -> None:
        """Handle the 'content' command to show full content of a specific page."""
        if len(parts) < 2:
            print("❌ Usage: content <page_id>")
            return
        
        try:
            page_id = int(parts[1])
        except ValueError:
            print("❌ Invalid page ID. Must be a number.")
            return
        
        print(f"📝 Fetching content for page ID {page_id}...")
        page = get_page_content(self.client, page_id)
        
        if page:
            print(format_page_result(page, include_content=True))
        else:
            print(f"❌ Page with ID {page_id} not found")
    
    def process_command(self, command: str) -> bool:
        """
        Process a user command and return False if the user wants to quit.
        
        Args:
            command: User input command
            
        Returns:
            False if user wants to quit, True otherwise
        """
        command = command.strip()
        
        if not command:
            return True
        
        parts = command.split()
        main_command = parts[0].lower()
        
        if main_command in {"quit", "exit"}:
            print("👋 Goodbye!")
            return False
        elif main_command == "help":
            self.show_help()
        elif main_command == "test":
            self.test_connection()
        elif main_command == "latest":
            self.handle_latest_command(parts)
        elif main_command == "find":
            self.handle_find_command(parts)
        elif main_command == "search":
            self.handle_search_command(parts)
        elif main_command == "count":
            self.handle_count_command()
        elif main_command == "summaries":
            self.handle_summaries_command()
        elif main_command == "content":
            self.handle_content_command(parts)
        else:
            print(f"❌ Unknown command: '{main_command}'. Type 'help' for available commands.")
        
        return True
    
    def run(self) -> None:
        """Start the chatbot REPL loop."""
        print("🤖 Supabase Pages Chatbot")
        print("Type 'help' for available commands or 'quit' to exit.")
        print("=" * 50)
        
        # Test connection on startup
        if not self.test_connection():
            print("❌ Exiting due to connection failure")
            return
        
        try:
            while True:
                try:
                    user_input = input("\n📥 query> ").strip()
                    
                    if not self.process_command(user_input):
                        break
                        
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except EOFError:
                    print("\n👋 Goodbye!")
                    break
                    
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")


def main():
    """Main entry point for the chatbot."""
    chatbot = SupabaseChatbot()
    chatbot.run()


if __name__ == "__main__":
    main()