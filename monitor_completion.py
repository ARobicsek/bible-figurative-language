#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor completion of Deuteronomy processing and create completion signals
"""
import time
import os
import glob
from datetime import datetime

def monitor_completion():
    """Monitor for completion signals and create notification file"""

    print("🔍 Monitoring Deuteronomy processing completion...")
    print(f"Start monitoring: {datetime.now()}")

    completion_signals = [
        "DEUTERONOMY PROCESSING COMPLETE!",
        "deuteronomy_complete_",
        "=== CHAPTER 34 COMPLETE ==="
    ]

    check_count = 0

    while True:
        check_count += 1

        # Check for completion database files
        db_files = glob.glob("deuteronomy_complete_*.db")
        if db_files:
            latest_db = max(db_files, key=os.path.getctime)
            db_size = os.path.getsize(latest_db)

            if db_size > 1000000:  # > 1MB suggests significant processing
                print(f"\n🎉 COMPLETION DETECTED! 🎉")
                print(f"Database found: {latest_db}")
                print(f"Size: {db_size:,} bytes")
                print(f"Detection time: {datetime.now()}")

                # Create completion signal file
                signal_file = f"DEUTERONOMY_COMPLETE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.signal"
                with open(signal_file, 'w') as f:
                    f.write(f"Deuteronomy processing completed!\n")
                    f.write(f"Completion detected: {datetime.now()}\n")
                    f.write(f"Database: {latest_db}\n")
                    f.write(f"Database size: {db_size:,} bytes\n")
                    f.write(f"Checks performed: {check_count}\n")

                print(f"Signal file created: {signal_file}")
                break

        # Check for summary files
        summary_files = glob.glob("deuteronomy_processing_summary_*.json")
        if summary_files:
            latest_summary = max(summary_files, key=os.path.getctime)
            print(f"\n📊 SUMMARY DETECTED!")
            print(f"Summary file: {latest_summary}")
            print(f"Detection time: {datetime.now()}")

            # Create completion signal file
            signal_file = f"DEUTERONOMY_COMPLETE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.signal"
            with open(signal_file, 'w') as f:
                f.write(f"Deuteronomy processing completed!\n")
                f.write(f"Completion detected: {datetime.now()}\n")
                f.write(f"Summary: {latest_summary}\n")
                f.write(f"Checks performed: {check_count}\n")

            print(f"Signal file created: {signal_file}")
            break

        # Progress indicator
        if check_count % 10 == 0:
            print(f"⏰ Check #{check_count} at {datetime.now().strftime('%H:%M:%S')}")

            # Show any existing databases
            if db_files:
                latest_db = max(db_files, key=os.path.getctime)
                db_size = os.path.getsize(latest_db)
                print(f"   Current DB: {latest_db} ({db_size:,} bytes)")

        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    try:
        monitor_completion()
    except KeyboardInterrupt:
        print(f"\n⏹️  Monitoring stopped by user at {datetime.now()}")
    except Exception as e:
        print(f"\n❌ Monitoring error: {e}")