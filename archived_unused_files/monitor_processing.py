#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitoring utilities for biblical text processing
"""
import sqlite3
import os
import json
import glob
from datetime import datetime

def check_database_status(db_path):
    """Check the status of a processing database"""
    if not os.path.exists(db_path):
        return {"status": "missing", "error": f"Database file {db_path} does not exist"}

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get basic stats
        cursor.execute("SELECT COUNT(*) FROM verses")
        verse_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM figurative_language")
        figurative_count = cursor.fetchone()[0]

        # Get chapter progress
        cursor.execute("SELECT book, MAX(chapter) as max_chapter FROM verses GROUP BY book")
        chapter_progress = cursor.fetchall()

        # Get latest processing time
        cursor.execute("SELECT MAX(processed_at) FROM verses")
        latest_time = cursor.fetchone()[0]

        conn.close()

        return {
            "status": "active" if verse_count > 0 else "empty",
            "verses": verse_count,
            "figurative_instances": figurative_count,
            "chapter_progress": chapter_progress,
            "latest_update": latest_time,
            "file_size_mb": os.path.getsize(db_path) / (1024 * 1024)
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_all_databases():
    """Check status of all databases in current directory"""
    print("=== DATABASE STATUS REPORT ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Find all database files
    db_files = glob.glob("*.db")

    if not db_files:
        print("No database files found in current directory.")
        return

    results = []

    for db_file in sorted(db_files):
        status = check_database_status(db_file)

        # Extract book and timestamp from filename
        book = "Unknown"
        timestamp = "Unknown"
        if "_conservative_" in db_file:
            parts = db_file.split("_conservative_")
            book = parts[0].capitalize()
            if len(parts) > 1:
                timestamp = parts[1].replace(".db", "")

        result = {
            "Database": db_file,
            "Book": book,
            "Status": status["status"],
            "Verses": status.get("verses", 0),
            "Figurative": status.get("figurative_instances", 0),
            "Size (MB)": f"{status.get('file_size_mb', 0):.1f}",
            "Latest Update": status.get("latest_update", "Never")
        }

        if status["status"] == "error":
            result["Error"] = status.get("error", "Unknown error")

        if status.get("chapter_progress"):
            max_chapters = {"Genesis": 50, "Deuteronomy": 34}
            for book_name, max_chapter in status["chapter_progress"]:
                expected_chapters = max_chapters.get(book_name, "Unknown")
                result["Progress"] = f"{max_chapter}/{expected_chapters}"

        results.append(result)

    # Print summary table
    headers = ["Database", "Book", "Status", "Verses", "Figurative", "Size (MB)", "Progress", "Latest Update"]
    table_data = []

    for result in results:
        row = [
            result.get("Database", ""),
            result.get("Book", ""),
            result.get("Status", ""),
            result.get("Verses", 0),
            result.get("Figurative", 0),
            result.get("Size (MB)", "0.0"),
            result.get("Progress", "N/A"),
            result.get("Latest Update", "Never") or "Never"
        ]
        table_data.append(row)

    # Print table manually since tabulate not available
    print(f"{'Database':<40} {'Book':<12} {'Status':<8} {'Verses':<8} {'Fig':<6} {'Size':<8} {'Progress':<10} {'Update':<20}")
    print("-" * 120)
    for row in table_data:
        print(f"{row[0]:<40} {row[1]:<12} {row[2]:<8} {row[3]:<8} {row[4]:<6} {row[5]:<8} {row[6]:<10} {row[7]:<20}")

    # Print detailed status for problematic databases
    print("\n=== DETAILED STATUS ===")

    for result in results:
        status = result.get("Status", "unknown")

        if status in ["empty", "error"]:
            print(f"\n⚠️  ISSUE: {result['Database']}")
            print(f"   Status: {status}")
            if "Error" in result:
                print(f"   Error: {result['Error']}")
            if status == "empty":
                print("   → This database was created but no data was inserted")
                print("   → Processing likely failed early or is still starting")

        elif status == "active":
            verses = result.get("Verses", 0)
            if verses < 10:
                print(f"\n⚠️  LOW PROGRESS: {result['Database']}")
                print(f"   Only {verses} verses processed - may have stalled")

    return results

def monitor_processing_logs():
    """Check for recent processing logs and errors"""
    print("\n=== PROCESSING LOGS ===")

    # Find recent log files
    log_files = glob.glob("*_log_*.txt")
    summary_files = glob.glob("*_summary_*.json")

    if log_files:
        print("Recent log files:")
        for log_file in sorted(log_files, key=os.path.getmtime, reverse=True)[:5]:
            mod_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            size_kb = os.path.getsize(log_file) / 1024
            print(f"  {log_file} - {mod_time.strftime('%Y-%m-%d %H:%M')} ({size_kb:.1f} KB)")

    if summary_files:
        print("\nProcessing summaries:")
        for summary_file in sorted(summary_files, key=os.path.getmtime, reverse=True)[:3]:
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary = json.load(f)

                print(f"\n📊 {summary_file}:")
                print(f"   Database: {summary.get('database', 'Unknown')}")
                print(f"   Total verses: {summary.get('total_verses', 0)}")
                print(f"   Total instances: {summary.get('total_instances', 0)}")
                print(f"   Errors: {summary.get('errors', 0)}")
                print(f"   Chapters completed: {summary.get('chapters_completed', 0)}")
                print(f"   Processing time: {summary.get('total_time_minutes', 0):.1f} minutes")

            except Exception as e:
                print(f"   ⚠️  Could not read summary: {e}")

def check_processing_health():
    """Overall health check for processing system"""
    print("\n=== PROCESSING HEALTH CHECK ===")

    # Check databases
    db_results = []
    for db_file in glob.glob("*conservative*.db"):
        status = check_database_status(db_file)
        db_results.append((db_file, status))

    healthy_dbs = sum(1 for _, status in db_results if status["status"] == "active" and status.get("verses", 0) > 50)
    total_dbs = len(db_results)

    print(f"Healthy databases: {healthy_dbs}/{total_dbs}")

    # Check for stalled processing
    stalled = []
    for db_file, status in db_results:
        if status["status"] == "active" and status.get("verses", 0) < 10:
            stalled.append(db_file)

    if stalled:
        print(f"⚠️  Potentially stalled: {', '.join(stalled)}")

    # Check for errors in recent logs
    recent_errors = 0
    for log_file in glob.glob("*_log_*.txt"):
        if os.path.getmtime(log_file) > (datetime.now().timestamp() - 3600):  # Last hour
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    recent_errors += content.count("ERROR")
            except:
                pass

    if recent_errors > 0:
        print(f"⚠️  Recent errors in logs: {recent_errors}")

    # Overall health
    if healthy_dbs == total_dbs and not stalled and recent_errors == 0:
        print("✅ All systems appear healthy")
    else:
        print("⚠️  Issues detected - check details above")

if __name__ == "__main__":
    check_all_databases()
    monitor_processing_logs()
    check_processing_health()