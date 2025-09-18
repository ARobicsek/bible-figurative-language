#!/usr/bin/env python3
"""
Test Text-Fabric setup and ETCBC data access
Goal: Extract Hebrew words with morphological data from Genesis 1:1-5
"""

from tf.app import use

def test_text_fabric_etcbc():
    print("Testing Text-Fabric with ETCBC data...")

    try:
        # Load ETCBC BHSA corpus
        print("Loading ETCBC BHSA corpus...")
        A = use("ETCBC/bhsa", checkout="clone")

        if A is None:
            print("[FAILURE] Could not load ETCBC data")
            return False

        print("[SUCCESS] ETCBC data loaded successfully")

        # Test access to API objects
        api = A.api
        F, E, T, L = api.F, api.E, api.T, api.L

        print("[SUCCESS] API objects accessible")

        # Find Genesis 1:1-5 verses
        print("\nTesting Genesis 1:1-5 extraction...")

        verses = []
        for verse_node in F.otype.s('verse'):
            book = F.book.v(verse_node)
            chapter = F.chapter.v(verse_node)
            verse = F.verse.v(verse_node)

            if book == 'Genesis' and chapter == 1 and verse <= 5:
                verses.append(verse_node)

        if not verses:
            print("[FAILURE] Could not find Genesis 1:1-5 verses")
            return False

        print(f"[SUCCESS] Found {len(verses)} verses in Genesis 1:1-5")

        # Extract Hebrew words with morphological data
        print("\nExtracting Hebrew words with morphological data...")

        sample_words = []
        for verse_node in verses[:2]:  # Test first 2 verses
            verse_num = F.verse.v(verse_node)
            print(f"\n--- Genesis 1:{verse_num} ---")

            # Get words in this verse
            words = L.d(verse_node, otype='word')

            for word_node in words[:5]:  # First 5 words per verse
                hebrew = F.g_word_utf8.v(word_node)
                lexeme = F.lex_utf8.v(word_node)
                pos = F.sp.v(word_node)
                morph = F.g_cons_utf8.v(word_node)

                word_data = {
                    'hebrew': hebrew,
                    'lexeme': lexeme,
                    'pos': pos,
                    'morphology': morph
                }

                sample_words.append(word_data)
                print(f"  {hebrew} | {lexeme} | {pos} | {morph}")

        if not sample_words:
            print("[FAILURE] Could not extract morphological data")
            return False

        print(f"\n[SUCCESS] Extracted {len(sample_words)} words with morphological data")
        print("[SUCCESS] Text-Fabric and ETCBC integration working correctly")

        return True

    except Exception as e:
        print(f"[FAILURE] Error during Text-Fabric test: {e}")
        return False

if __name__ == "__main__":
    success = test_text_fabric_etcbc()
    if success:
        print("\n[PHASE 0 CHECKPOINT] Text-Fabric + ETCBC validation PASSED")
    else:
        print("\n[PHASE 0 CHECKPOINT] Text-Fabric + ETCBC validation FAILED")
        print("Consider pivot to alternative Hebrew sources")