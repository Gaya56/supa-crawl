#!/usr/bin/env python3
"""
Test Runner for Crawl4AI + Supabase Project
Provides organized test execution following Python testing best practices

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --crawl4ai         # Run only Crawl4AI tests
    python run_tests.py --supabase         # Run only Supabase tests
    python run_tests.py --help             # Show help
"""

import argparse
import asyncio
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_pytest_command(test_paths, markers=None, verbose=True):
    """Run pytest with specified parameters"""
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if markers:
        for marker in markers:
            cmd.extend(["-m", marker])
    
    cmd.extend(test_paths)
    
    print(f"Running: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode == 0


async def run_async_tests_directly():
    """Run async tests directly without pytest for better error handling"""
    print("Running async tests directly...")
    print("=" * 60)
    
    # Import and run async tests
    try:
        # Run Crawl4AI basic tests
        from tests.crawl4ai.test_basic_crawling import run_async_tests as run_crawl4ai_tests
        print("Running Crawl4AI basic tests...")
        crawl4ai_success = await run_crawl4ai_tests()
        
        if not crawl4ai_success:
            return False
        
        # Run integration tests
        from tests.integration.test_crawl4ai_supabase import run_async_integration_tests
        print("\nRunning integration tests...")
        integration_success = await run_async_integration_tests()
        
        return integration_success
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Some dependencies may not be installed.")
        return False
    except Exception as e:
        print(f"Error running async tests: {e}")
        return False


def run_sync_tests():
    """Run synchronous tests using unittest"""
    print("Running synchronous tests...")
    print("=" * 60)
    
    try:
        # Run Supabase tests
        from tests.supabase.test_database_operations import run_tests as run_supabase_tests
        print("Running Supabase database tests...")
        return run_supabase_tests()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Some dependencies may not be installed.")
        return False
    except Exception as e:
        print(f"Error running sync tests: {e}")
        return False


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(
        description="Test runner for Crawl4AI + Supabase project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --unit             # Run only unit tests  
  python run_tests.py --integration      # Run only integration tests
  python run_tests.py --crawl4ai         # Run only Crawl4AI tests
  python run_tests.py --supabase         # Run only Supabase tests
  python run_tests.py --async-tests       # Run only async tests
  python run_tests.py --sync-tests        # Run only sync tests
        """
    )
    
    parser.add_argument(
        "--unit", 
        action="store_true", 
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration", 
        action="store_true", 
        help="Run only integration tests"
    )
    parser.add_argument(
        "--crawl4ai", 
        action="store_true", 
        help="Run only Crawl4AI tests"
    )
    parser.add_argument(
        "--supabase", 
        action="store_true", 
        help="Run only Supabase tests"
    )
    parser.add_argument(
        "--async-tests", 
        action="store_true", 
        help="Run only async tests"
    )
    parser.add_argument(
        "--sync-tests", 
        action="store_true", 
        help="Run only sync tests"
    )
    parser.add_argument(
        "--pytest", 
        action="store_true", 
        help="Use pytest runner (requires pytest installation)"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        default=True,
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    print("Crawl4AI + Supabase Test Runner")
    print("=" * 60)
    print(f"Project root: {project_root}")
    print(f"Python version: {sys.version}")
    print("=" * 60)
    
    # Determine which tests to run
    if args.pytest:
        # Use pytest runner
        test_paths = []
        markers = []
        
        if args.unit:
            markers.append("unit")
        if args.integration:
            markers.append("integration")
        if args.crawl4ai:
            markers.append("crawl4ai")
        if args.supabase:
            markers.append("supabase")
        
        if not any([args.unit, args.integration, args.crawl4ai, args.supabase]):
            test_paths = ["tests/"]
        else:
            if args.crawl4ai or args.unit:
                test_paths.append("tests/crawl4ai/")
            if args.supabase or args.unit:
                test_paths.append("tests/supabase/")
            if args.integration:
                test_paths.append("tests/integration/")
        
        success = run_pytest_command(test_paths, markers, args.verbose)
        
    else:
        # Use direct test execution
        success = True
        
        if args.async_tests or (not args.sync_tests and not args.supabase):
            print("Running async tests...")
            async_success = asyncio.run(run_async_tests_directly())
            success = success and async_success
        
        if args.sync_tests or args.supabase or (not args.async_tests and not args.crawl4ai and not args.integration):
            print("\nRunning sync tests...")
            sync_success = run_sync_tests()
            success = success and sync_success
    
    # Print final result
    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed successfully!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()