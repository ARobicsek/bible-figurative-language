#!/usr/bin/env python3
"""
Simple retry script for Proverbs Chapter 15 using the main processor with error recovery.
"""

import subprocess
import sys
import os
import time

def run_chapter15_processing():
    """Run Chapter 15 processing with retry logic"""
    max_retries = 3

    for attempt in range(max_retries):
        print(f"\n=== ATTEMPT {attempt + 1}/{max_retries} ===")

        try:
            # Run the main processor
            result = subprocess.run([
                sys.executable, 'interactive_parallel_processor.py', 'Proverbs', '15'
            ],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
            )

            print("STDOUT:")
            print(result.stdout[-2000:])  # Show last 2000 chars

            if result.stderr:
                print("STDERR:")
                print(result.stderr[-1000:])  # Show last 1000 chars

            # Check if processing was successful
            if "Total instances found: 0" in result.stdout:
                print("❌ Processing failed - no instances found")
                if attempt < max_retries - 1:
                    print("Retrying in 10 seconds...")
                    time.sleep(10)
                    continue
                else:
                    print("All retries exhausted")
                    return False
            else:
                print("✅ Processing appears successful!")

                # Check database creation
                db_files = [f for f in os.listdir('.') if f.startswith('proverbs_c15') and f.endswith('.db')]
                if db_files:
                    print(f"Database files created: {db_files}")

                    # Check database content
                    import sqlite3
                    for db_file in db_files:
                        try:
                            conn = sqlite3.connect(db_file)
                            verses = conn.execute('SELECT COUNT(*) FROM verses').fetchone()[0]
                            instances = conn.execute('SELECT COUNT(*) FROM figurative_language').fetchone()[0]
                            print(f"Database {db_file}: {verses} verses, {instances} instances")
                            conn.close()

                            if verses > 0 and instances > 0:
                                print(f"✅ SUCCESS: {db_file} contains valid data")
                                return db_file
                        except Exception as e:
                            print(f"Error checking {db_file}: {e}")

                return True

        except subprocess.TimeoutExpired:
            print("❌ Processing timed out")
            if attempt < max_retries - 1:
                print("Retrying...")
                continue
            else:
                print("All retries exhausted due to timeouts")
                return False

        except Exception as e:
            print(f"❌ Error during processing: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(5)
                continue
            else:
                print("All retries exhausted due to errors")
                return False

    return False

if __name__ == "__main__":
    print("=== PROVERBS CHAPTER 15 RETRY PROCESSOR ===")

    # Change to the private directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    result = run_chapter15_processing()

    if result:
        print(f"\n✅ SUCCESS: Chapter 15 processing completed!")
        if isinstance(result, str):
            print(f"Database: {result}")
    else:
        print(f"\n❌ FAILED: Could not process Chapter 15 after retries")
        sys.exit(1)