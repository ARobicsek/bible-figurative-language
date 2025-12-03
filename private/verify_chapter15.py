import sqlite3

# Connect to the Chapter 15 database
conn = sqlite3.connect('proverbs_c15_all_v_batched_20251202_2228.db')

# Check verses and instances
verse_count = conn.execute('SELECT COUNT(*) FROM verses').fetchone()[0]
instance_count = conn.execute('SELECT COUNT(*) FROM figurative_language').fetchone()[0]

print(f"Chapter 15 Database Verification:")
print(f"Verses: {verse_count}")
print(f"Instances: {instance_count}")

# Show sample verses
print("\nSample verses:")
for row in conn.execute('SELECT chapter, verse, english_text FROM verses LIMIT 5').fetchall():
    print(f"  {row[0]}:{row[1]} - {row[2][:60]}...")

# Check figurative language types
print("\nFigurative language breakdown:")
types = ['metaphor', 'simile', 'personification', 'hyperbole', 'metonymy', 'idiom', 'other']
for fig_type in types:
    count = conn.execute(f'SELECT COUNT(*) FROM figurative_language WHERE {fig_type} = "yes"').fetchone()[0]
    if count > 0:
        print(f"  {fig_type}: {count}")

# Check validation coverage
validation_count = conn.execute('SELECT COUNT(*) FROM figurative_language WHERE validation_response IS NOT NULL').fetchone()[0]
print(f"\nValidation coverage: {validation_count}/{instance_count} instances")

conn.close()