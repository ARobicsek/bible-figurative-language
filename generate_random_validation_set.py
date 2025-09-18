#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate 200 random verses from the Pentateuch for validation
"""
import random
import json
from typing import List, Dict
from src.hebrew_figurative_db.text_extraction import SefariaClient

# Pentateuch book structures (approximate chapter counts)
PENTATEUCH_BOOKS = {
    'Genesis': 50,
    'Exodus': 40,
    'Leviticus': 27,
    'Numbers': 36,
    'Deuteronomy': 34
}

def generate_random_verses(verses_per_book: int = 40) -> List[str]:
    """Generate random verse references from each book of the Pentateuch"""

    random_refs = []

    for book, max_chapters in PENTATEUCH_BOOKS.items():
        print(f"Generating {verses_per_book} random verses from {book} (1-{max_chapters} chapters)...")

        book_refs = []
        attempts = 0

        while len(book_refs) < verses_per_book and attempts < verses_per_book * 3:
            # Random chapter (1 to max_chapters)
            chapter = random.randint(1, max_chapters)

            # Random verse (1 to 30, most chapters have at least 20 verses)
            verse = random.randint(1, 30)

            ref = f"{book}.{chapter}.{verse}"

            # Avoid duplicates within the same book
            if ref not in book_refs:
                book_refs.append(ref)

            attempts += 1

        if len(book_refs) < verses_per_book:
            print(f"Warning: Only generated {len(book_refs)} verses for {book} (attempted {attempts} times)")

        random_refs.extend(book_refs)

    return random_refs

def validate_verse_references(refs: List[str]) -> List[str]:
    """Validate that verse references actually exist by testing a few"""

    client = SefariaClient()
    valid_refs = []
    invalid_count = 0

    print(f"\nValidating {len(refs)} verse references...")

    # Test all references (for small sets) or sample (for large sets)
    test_refs = refs if len(refs) <= 50 else random.sample(refs, 50)

    for ref in test_refs:
        try:
            verses, _ = client.extract_hebrew_text(ref)
            if verses and len(verses) > 0:
                valid_refs.append(ref)
            else:
                invalid_count += 1
                print(f"  Invalid: {ref} (no verses returned)")
        except Exception as e:
            invalid_count += 1
            print(f"  Invalid: {ref} (error: {e})")

    validation_rate = len(valid_refs) / len(test_refs) * 100
    print(f"Validation complete: {len(valid_refs)}/{len(test_refs)} valid ({validation_rate:.1f}%)")

    if validation_rate < 80:
        print("WARNING: Low validation rate. Consider adjusting verse ranges.")

    return refs  # Return all refs since we only sampled for validation

def save_validation_set(refs: List[str], filename: str = "validation_set_200_verses.json"):
    """Save the validation set to a file"""

    validation_data = {
        'description': 'Random 200 verses from Pentateuch for LLM validation',
        'total_verses': len(refs),
        'verses_per_book': len(refs) // 5,
        'books': list(PENTATEUCH_BOOKS.keys()),
        'references': refs,
        'generated_at': str(random.randint(1000000, 9999999))  # Simple timestamp replacement
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(validation_data, f, indent=2, ensure_ascii=False)

    print(f"\nValidation set saved to: {filename}")
    return filename

def main():
    """Generate and save random validation set"""

    print("=== GENERATING RANDOM PENTATEUCH VALIDATION SET ===")

    # Set random seed for reproducibility
    random.seed(42)

    # Generate 40 random verses from each book (200 total)
    verse_refs = generate_random_verses(verses_per_book=40)

    print(f"\nGenerated {len(verse_refs)} total verse references")

    # Show sample of references
    print(f"\nSample references:")
    for i, ref in enumerate(random.sample(verse_refs, min(10, len(verse_refs)))):
        print(f"  {i+1}. {ref}")

    # Validate references
    validated_refs = validate_verse_references(verse_refs)

    # Save to file
    filename = save_validation_set(validated_refs)

    # Summary by book
    print(f"\nBreakdown by book:")
    for book in PENTATEUCH_BOOKS.keys():
        book_count = len([ref for ref in validated_refs if ref.startswith(book)])
        print(f"  {book}: {book_count} verses")

    print(f"\n✅ Validation set ready for LLM processing!")
    print(f"📁 File: {filename}")
    print(f"📊 Total verses: {len(validated_refs)}")

    return validated_refs, filename

if __name__ == "__main__":
    main()