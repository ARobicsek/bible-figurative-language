"""
Clean figurative_detection_deliberation and figurative_detection_deliberation_non_sacred fields
by removing trailing carriage returns and ```json strings.
"""

import sqlite3
import re

DB_PATH = 'database/Pentateuch_Psalms_fig_language.db'

def clean_deliberation_text(text):
    """Remove trailing carriage return + ```json pattern from deliberation text."""
    if not text:
        return text

    # Remove trailing newline/carriage return followed by ```json
    cleaned = re.sub(r'\s*\n\s*```json\s*$', '', text, flags=re.IGNORECASE)

    return cleaned

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check how many records have the contamination pattern
    print("Checking for contamination patterns...")

    cursor.execute("""
        SELECT COUNT(*)
        FROM verses
        WHERE figurative_detection_deliberation LIKE '%```json%'
           OR figurative_detection_deliberation_non_sacred LIKE '%```json%'
    """)
    contaminated_count = cursor.fetchone()[0]
    print(f"Found {contaminated_count} verses with contamination pattern")

    if contaminated_count == 0:
        print("No contamination found. Exiting.")
        conn.close()
        return

    # Show a few examples before cleaning
    print("\nExample BEFORE cleaning:")
    cursor.execute("""
        SELECT id, reference,
               SUBSTR(figurative_detection_deliberation, LENGTH(figurative_detection_deliberation) - 50, 51) as tail
        FROM verses
        WHERE figurative_detection_deliberation LIKE '%```json%'
        LIMIT 3
    """)
    for row in cursor.fetchall():
        print(f"  Verse {row[0]} ({row[1]}): ...{repr(row[2])}")

    # Clean figurative_detection_deliberation field
    print("\nCleaning figurative_detection_deliberation field...")
    cursor.execute("SELECT id, figurative_detection_deliberation FROM verses WHERE figurative_detection_deliberation IS NOT NULL")
    verses_to_update = []

    for verse_id, deliberation in cursor.fetchall():
        cleaned = clean_deliberation_text(deliberation)
        if cleaned != deliberation:
            verses_to_update.append((cleaned, verse_id))

    print(f"Updating {len(verses_to_update)} records in figurative_detection_deliberation...")
    cursor.executemany(
        "UPDATE verses SET figurative_detection_deliberation = ? WHERE id = ?",
        verses_to_update
    )

    # Clean figurative_detection_deliberation_non_sacred field
    print("Cleaning figurative_detection_deliberation_non_sacred field...")
    cursor.execute("SELECT id, figurative_detection_deliberation_non_sacred FROM verses WHERE figurative_detection_deliberation_non_sacred IS NOT NULL")
    verses_to_update_ns = []

    for verse_id, deliberation in cursor.fetchall():
        cleaned = clean_deliberation_text(deliberation)
        if cleaned != deliberation:
            verses_to_update_ns.append((cleaned, verse_id))

    print(f"Updating {len(verses_to_update_ns)} records in figurative_detection_deliberation_non_sacred...")
    cursor.executemany(
        "UPDATE verses SET figurative_detection_deliberation_non_sacred = ? WHERE id = ?",
        verses_to_update_ns
    )

    # Commit changes
    conn.commit()

    # Verify cleaning
    print("\nVerifying cleanup...")
    cursor.execute("""
        SELECT COUNT(*)
        FROM verses
        WHERE figurative_detection_deliberation LIKE '%```json%'
           OR figurative_detection_deliberation_non_sacred LIKE '%```json%'
    """)
    remaining = cursor.fetchone()[0]

    print(f"\nCleaning complete!")
    print(f"  Updated {len(verses_to_update)} records in figurative_detection_deliberation")
    print(f"  Updated {len(verses_to_update_ns)} records in figurative_detection_deliberation_non_sacred")
    print(f"  Remaining contaminated records: {remaining}")

    # Show examples after cleaning
    print("\nExample AFTER cleaning:")
    cursor.execute("""
        SELECT id, reference,
               SUBSTR(figurative_detection_deliberation, LENGTH(figurative_detection_deliberation) - 50, 51) as tail
        FROM verses
        WHERE id IN (SELECT id FROM verses WHERE figurative_detection_deliberation LIKE '%deliberation%' LIMIT 3)
    """)
    for row in cursor.fetchall():
        print(f"  Verse {row[0]} ({row[1]}): ...{repr(row[2])}")

    conn.close()

if __name__ == "__main__":
    main()
