"""Test script to debug Psalms 84:4 highlighting issue"""
import sqlite3
import json
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'database/Pentateuch_Psalms_fig_language.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the verse data
cursor.execute('''
    SELECT v.hebrew_text, v.hebrew_text_non_sacred,
           fl.figurative_text_in_hebrew, fl.figurative_text_in_hebrew_non_sacred,
           fl.final_metaphor, fl.final_simile, fl.final_idiom, fl.final_metonymy,
           fl.final_hyperbole, fl.final_personification, fl.final_other
    FROM verses v
    JOIN figurative_language fl ON v.id = fl.verse_id
    WHERE v.reference = "Psalms 84:4"
''')

row = cursor.fetchone()

if row:
    verse_heb_sacred = row[0]
    verse_heb_non_sacred = row[1]
    fig_heb_sacred = row[2]
    fig_heb_non_sacred = row[3]

    print("=" * 80)
    print("PSALMS 84:4 DEBUGGING")
    print("=" * 80)

    print("\n1. VERSE TEXT (Sacred):")
    print(f"   Length: {len(verse_heb_sacred)}")
    print(f"   Text: {verse_heb_sacred}")

    print("\n2. FIGURATIVE TEXT (Sacred):")
    print(f"   Length: {len(fig_heb_sacred)}")
    print(f"   Text: {fig_heb_sacred}")

    print("\n3. MATCH TEST (Sacred):")
    print(f"   Is figurative text IN verse text? {fig_heb_sacred in verse_heb_sacred}")
    print(f"   Position: {verse_heb_sacred.find(fig_heb_sacred)}")

    print("\n4. VERSE TEXT (Non-Sacred):")
    print(f"   Length: {len(verse_heb_non_sacred)}")
    print(f"   Text: {verse_heb_non_sacred}")

    print("\n5. FIGURATIVE TEXT (Non-Sacred):")
    print(f"   Length: {len(fig_heb_non_sacred)}")
    print(f"   Text: {fig_heb_non_sacred}")

    print("\n6. MATCH TEST (Non-Sacred):")
    print(f"   Is figurative text IN verse text? {fig_heb_non_sacred in verse_heb_non_sacred}")
    print(f"   Position: {verse_heb_non_sacred.find(fig_heb_non_sacred)}")

    print("\n7. FIGURATIVE TYPES:")
    types = []
    if row[4] == 'yes': types.append('metaphor')
    if row[5] == 'yes': types.append('simile')
    if row[6] == 'yes': types.append('idiom')
    if row[7] == 'yes': types.append('metonymy')
    if row[8] == 'yes': types.append('hyperbole')
    if row[9] == 'yes': types.append('personification')
    if row[10] == 'yes': types.append('other')
    print(f"   Types: {', '.join(types)}")

    print("\n8. HTML ENTITY CHECK:")
    print(f"   Verse contains &thinsp;: {'&thinsp;' in verse_heb_sacred}")
    print(f"   Figurative contains &thinsp;: {'&thinsp;' in fig_heb_sacred}")

    # Check if there are any differences in the text that might prevent matching
    print("\n9. CHARACTER-BY-CHARACTER COMPARISON (first 50 chars):")
    for i in range(min(50, len(fig_heb_sacred))):
        if i < len(verse_heb_sacred):
            v_char = verse_heb_sacred[i]
            f_char = fig_heb_sacred[i]
            match = "✓" if v_char == f_char else "✗"
            print(f"   [{i:2d}] Verse: '{v_char}' (U+{ord(v_char):04X}) | Fig: '{f_char}' (U+{ord(f_char):04X}) {match}")

    print("\n" + "=" * 80)
else:
    print("No data found for Psalms 84:4")

conn.close()
