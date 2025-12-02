"""
Comparison script for MEDIUM vs HIGH reasoning test results
Generates a detailed markdown comparison showing what each model detected and why
"""
import json
import sys

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def load_results(filepath):
    """Load test results from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_instance(inst):
    """Format a single instance for display"""
    types = []
    if inst.get('simile') == 'yes': types.append('Simile')
    if inst.get('metaphor') == 'yes': types.append('Metaphor')
    if inst.get('personification') == 'yes': types.append('Personification')
    if inst.get('idiom') == 'yes': types.append('Idiom')
    if inst.get('hyperbole') == 'yes': types.append('Hyperbole')
    if inst.get('metonymy') == 'yes': types.append('Metonymy')
    if inst.get('other') == 'yes': types.append('Other')

    type_str = ', '.join(types) if types else 'None'

    output = []
    output.append(f"**{inst['english_text']}** ({type_str})")
    output.append(f"- Confidence: {inst.get('confidence', 'N/A')}")
    output.append(f"- Explanation: {inst.get('explanation', 'N/A')}")

    return '\n'.join(output)

def extract_reasoning(verse_data):
    """Extract COMPLETE reasoning from raw_response or deliberation"""
    raw = verse_data.get('raw_response', '')
    delib = verse_data.get('deliberation', '')

    # Try to extract deliberation section from raw_response
    if 'DELIBERATION:' in raw:
        start = raw.find('DELIBERATION:')
        # Find where JSON starts (usually after deliberation)
        json_start = raw.find('[', start)
        if json_start > start:
            reasoning = raw[start:json_start].strip()
        else:
            # Take everything from DELIBERATION onwards
            reasoning = raw[start:].strip()
    elif delib:
        reasoning = delib
    else:
        # Return FULL raw response (no truncation)
        reasoning = raw if raw else "No reasoning available"

    return reasoning

def compare_verses(medium_data, high_data, output_file):
    """Compare verses between MEDIUM and HIGH reasoning"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Proverbs 3:11-18 Comparison: MEDIUM vs HIGH Reasoning\n\n")
        f.write("## Test Summary\n\n")

        # Summary table
        f.write("| Metric | MEDIUM Reasoning | HIGH Reasoning |\n")
        f.write("|--------|------------------|----------------|\n")
        f.write(f"| Total Instances | {medium_data['test_info']['total_detected']} | {high_data['test_info']['total_detected']} |\n")
        f.write(f"| Detection Rate | {medium_data['test_info']['total_detected']/8:.2f} per verse | {high_data['test_info']['total_detected']/8:.2f} per verse |\n")
        f.write(f"| Total Cost | ${medium_data['test_info']['total_cost']:.2f} | ${high_data['test_info']['total_cost']:.2f} |\n")
        f.write(f"| Cost per Verse | ${medium_data['test_info']['total_cost']/8:.2f} | ${high_data['test_info']['total_cost']/8:.2f} |\n")
        f.write(f"| Total Time | {medium_data['test_info']['total_time']/60:.1f} min | {high_data['test_info']['total_time']/60:.1f} min |\n")
        f.write(f"| Time per Verse | {medium_data['test_info']['total_time']/8:.1f}s | {high_data['test_info']['total_time']/8:.1f}s |\n\n")

        # Detailed verse-by-verse comparison
        f.write("## Verse-by-Verse Analysis\n\n")

        for m_verse, h_verse in zip(medium_data['verses'], high_data['verses']):
            ref = m_verse['reference']
            f.write(f"### {ref}\n\n")
            f.write(f"**Text**: {m_verse['english']}\n\n")

            # Comparison table with token counts
            f.write(f"| Model | Instances | Cost | Time | Input Tokens | Output Tokens |\n")
            f.write(f"|-------|-----------|------|------|--------------|---------------|\n")

            # Get token info if available
            m_in = m_verse.get('input_tokens', 'N/A')
            m_out = m_verse.get('output_tokens', 'N/A')
            h_in = h_verse.get('input_tokens', 'N/A')
            h_out = h_verse.get('output_tokens', 'N/A')

            f.write(f"| MEDIUM | {m_verse['detected_count']} | ${m_verse['cost']:.4f} | {m_verse['processing_time']:.1f}s | {m_in} | {m_out} |\n")
            f.write(f"| HIGH | {h_verse['detected_count']} | ${h_verse['cost']:.4f} | {h_verse['processing_time']:.1f}s | {h_in} | {h_out} |\n\n")

            # MEDIUM detections
            f.write(f"#### MEDIUM Reasoning Detected ({m_verse['detected_count']} instances):\n\n")
            if m_verse['detected_count'] > 0:
                for i, inst in enumerate(m_verse['instances'], 1):
                    f.write(f"{i}. {format_instance(inst)}\n\n")
            else:
                f.write("*No instances detected*\n\n")

            # MEDIUM reasoning - COMPLETE TEXT
            f.write("**MEDIUM Reasoning (complete)**:\n")
            f.write("```\n")
            reasoning = extract_reasoning(m_verse)
            f.write(reasoning + "\n")  # NO TRUNCATION
            f.write("```\n\n")

            # HIGH detections
            f.write(f"#### HIGH Reasoning Detected ({h_verse['detected_count']} instances):\n\n")
            if h_verse['detected_count'] > 0:
                for i, inst in enumerate(h_verse['instances'], 1):
                    f.write(f"{i}. {format_instance(inst)}\n\n")
            else:
                f.write("*No instances detected*\n\n")

            # HIGH reasoning - COMPLETE TEXT
            f.write("**HIGH Reasoning (complete)**:\n")
            f.write("```\n")
            reasoning = extract_reasoning(h_verse)
            f.write(reasoning + "\n")  # NO TRUNCATION
            f.write("```\n\n")

            f.write("---\n\n")

    print(f"Comparison written to: {output_file}")

if __name__ == "__main__":
    import glob
    import os

    # File paths
    medium_file = "output/proverbs_3_11-18_single_medium_20251130_095404_results.json"

    # Find the most recent HIGH results file
    high_files = sorted(glob.glob("output/proverbs_3_11-18_single_high_*_results.json"))
    if not high_files:
        print("ERROR: No HIGH results files found!")
        sys.exit(1)

    high_file = high_files[-1]  # Use most recent
    print(f"Loading test results...")
    print(f"  MEDIUM: {medium_file}")
    print(f"  HIGH: {high_file}")

    medium_data = load_results(medium_file)
    high_data = load_results(high_file)

    # Generate comparison
    output_file = "docs/PROVERBS_MEDIUM_VS_HIGH_COMPARISON.md"
    compare_verses(medium_data, high_data, output_file)
