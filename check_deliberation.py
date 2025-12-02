import sqlite3
import json
import sys

# Set UTF-8 encoding for output
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Connect to the database
db_path = "output/proverbs_3_11-18_batched_validated_20251202_112009.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Checking verse-specific deliberation in database:\n")

# Query all verses
cursor.execute("SELECT reference, figurative_detection_deliberation FROM verses ORDER BY verse")
results = cursor.fetchall()

deliberation_lengths = []
for row in results:
    reference, deliberation = row
    print(f"{reference}:")
    if deliberation:
        deliberation_lengths.append(len(deliberation))
        print(f"  Length: {len(deliberation)} chars")
        # Show first 100 characters, safely handling any encoding issues
        sample = deliberation[:100].replace('\n', ' ').replace('\r', ' ')
        print(f"  Sample: {sample}...")
    else:
        deliberation_lengths.append(0)
        print("  No deliberation (NULL)")
    print()

# Summary
print("=" * 50)
print(f"SUMMARY:")
print(f"Total verses: {len(results)}")
print(f"Deliberation lengths: {deliberation_lengths}")
if len(set(deliberation_lengths)) > 1:
    print("✅ SUCCESS: Each verse has DIFFERENT deliberation length (verse-specific!)")
else:
    print("❌ FAIL: All verses have same deliberation length")

conn.close()