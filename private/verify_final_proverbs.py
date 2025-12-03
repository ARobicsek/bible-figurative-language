import sqlite3
import os

def verify_proverbs_database():
    """Verify the final Proverbs database completeness and integrity"""

    db_path = "Proverbs.db"

    if not os.path.exists(db_path):
        print(f"ERROR: Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)

    print("=== FINAL PROVERBS DATABASE VERIFICATION ===")
    print(f"Database: {db_path}")

    # Overall statistics
    total_verses = conn.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
    total_instances = conn.execute("SELECT COUNT(*) FROM figurative_language").fetchone()[0]

    print(f"\nOVERALL STATISTICS:")
    print(f"Total verses: {total_verses}")
    print(f"Total figurative instances: {total_instances}")
    print(f"Instances per verse: {total_instances/total_verses:.2f}")

    # Chapter breakdown
    print(f"\nCHAPTER BREAKDOWN:")
    chapters = conn.execute("""
        SELECT chapter, COUNT(*) as verse_count
        FROM verses
        GROUP BY chapter
        ORDER BY chapter
    """).fetchall()

    expected_chapters = 18
    actual_chapters = len(chapters)

    for chapter, count in chapters:
        print(f"  Chapter {chapter:2d}: {count:2d} verses")

    print(f"\nCHAPTER COMPLETION:")
    print(f"Expected chapters: {expected_chapters}")
    print(f"Actual chapters: {actual_chapters}")
    completion_rate = (actual_chapters / expected_chapters) * 100
    print(f"Completion rate: {completion_rate:.1f}%")

    # Figurative language breakdown
    print(f"\nFIGURATIVE LANGUAGE BREAKDOWN:")

    types = ['metaphor', 'simile', 'personification', 'hyperbole', 'metonymy', 'idiom', 'other']

    for fig_type in types:
        count = conn.execute(f"""
            SELECT COUNT(*) FROM figurative_language
            WHERE {fig_type} = 'yes'
        """).fetchone()[0]
        if count > 0:
            percentage = (count / total_instances) * 100
            print(f"  {fig_type:12s}: {count:3d} instances ({percentage:5.1f}%)")

    # Chapter 15 specific verification
    print(f"\nCHAPTER 15 VERIFICATION:")
    ch15_verses = conn.execute("SELECT COUNT(*) FROM verses WHERE chapter = 15").fetchone()[0]
    ch15_instances = conn.execute("SELECT COUNT(*) FROM figurative_language WHERE verse_id IN (SELECT id FROM verses WHERE chapter = 15)").fetchone()[0]

    print(f"Chapter 15 verses: {ch15_verses}")
    print(f"Chapter 15 instances: {ch15_instances}")

    # Show some Chapter 15 content
    print(f"\nSAMPLE CHAPTER 15 VERSES:")
    sample_verses = conn.execute("""
        SELECT verse, english_text
        FROM verses
        WHERE chapter = 15
        ORDER BY verse
        LIMIT 5
    """).fetchall()

    for verse, text in sample_verses:
        print(f"  15:{verse:2d} - {text[:60]}...")

    # Database size
    db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
    print(f"\nDATABASE SIZE: {db_size:.1f} MB")

    # Final status
    print(f"\n=== FINAL STATUS ===")
    if actual_chapters == 18 and total_verses >= 525:
        print("*** PROVERBS DATABASE IS 100% COMPLETE! ***")
        print(f"All {expected_chapters} chapters processed")
        print(f"Total of {total_verses} verses with {total_instances} figurative instances")
        return True
    else:
        print(f"*** DATABASE NOT COMPLETE ***")
        print(f"Expected {expected_chapters} chapters, got {actual_chapters}")
        print(f"Expected ~525 verses, got {total_verses}")
        return False

if __name__ == "__main__":
    verify_proverbs_database()