#!/usr/bin/env python3
"""
Analyze current classification issues
"""
import sqlite3

def analyze_personification_issues():
    """Analyze personification classification issues"""
    print("=== Personification Classification Analysis ===")

    conn = sqlite3.connect('deuteronomy_enhanced_validation_20250918_232507.db')
    cursor = conn.cursor()

    # Get personification examples
    cursor.execute('''
        SELECT figurative_text, explanation, v.english_text
        FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id
        WHERE fl.type = "personification"
        ORDER BY fl.id
        LIMIT 20
    ''')

    results = cursor.fetchall()
    print(f"Found {len(results)} personification examples")

    # Categories to look for in problematic classifications
    divine_anthropomorphism = []  # Should be metaphor
    normal_human_actions = []     # Should not be personification
    clear_personification = []    # Should remain personification

    for result in results:
        fig_text, explanation, verse_text = result

        # Safe text handling
        safe_fig_text = fig_text.encode('ascii', 'ignore').decode('ascii') if fig_text else "N/A"
        safe_explanation = explanation.encode('ascii', 'ignore').decode('ascii') if explanation else "N/A"
        safe_verse = verse_text.encode('ascii', 'ignore').decode('ascii') if verse_text else "N/A"

        print(f"\nText: {safe_fig_text[:50]}")
        print(f"Explanation: {safe_explanation[:80]}...")

        # Look for problematic patterns
        if any(term in safe_explanation.lower() for term in ['god', 'divine', 'yahweh', 'lord']):
            if any(term in safe_explanation.lower() for term in ['body', 'hand', 'arm', 'face', 'eye']):
                divine_anthropomorphism.append((safe_fig_text, safe_explanation))
                print(">>> ISSUE: Divine body parts should be METAPHOR")
            elif any(term in safe_explanation.lower() for term in ['love', 'desire', 'relationship']):
                divine_anthropomorphism.append((safe_fig_text, safe_explanation))
                print(">>> ISSUE: Divine love/relationship should be METAPHOR")

        if any(term in safe_explanation.lower() for term in ['locust', 'consume', 'enemy', 'fear', 'people', 'human']):
            normal_human_actions.append((safe_fig_text, safe_explanation))
            print(">>> ISSUE: Normal actions not personification")

    print(f"\n=== SUMMARY ===")
    print(f"Divine anthropomorphism (should be metaphor): {len(divine_anthropomorphism)}")
    print(f"Normal human/animal actions (not personification): {len(normal_human_actions)}")

    conn.close()
    return divine_anthropomorphism, normal_human_actions

if __name__ == "__main__":
    analyze_personification_issues()