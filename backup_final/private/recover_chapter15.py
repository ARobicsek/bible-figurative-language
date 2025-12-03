#!/usr/bin/env python3
"""
Recovery script for Proverbs Chapter 15 detection data.
Handles JSON corruption and uses enhanced extraction strategies.
"""

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'src'))

try:
    from unified_llm_client import UnifiedLLMClient
    from src.hebrew_figurative_db.database.db_manager import DatabaseManager
    from sefaria_text import SefariaTextClient
except ImportError:
    print("Falling back to direct processing approach...")
    UnifiedLLMClient = None
    DatabaseManager = None
    SefariaTextClient = None

class Chapter15DetectionRecovery:
    def __init__(self):
        self.llm_client = UnifiedLLMClient()
        self.db_manager = DatabaseManager()

    def extract_json_with_fallbacks(self, json_text):
        """Extract JSON using multiple strategies - same as enhanced validation system"""

        # Strategy 1: Standard markdown JSON block extraction
        pattern1 = r'```json\s*(.*?)\s*```'
        matches = re.findall(pattern1, json_text, re.DOTALL | re.IGNORECASE)
        if matches:
            try:
                return json.loads(matches[0])
            except:
                pass

        # Strategy 2: Generic code block extraction
        pattern2 = r'```\s*(.*?)\s*```'
        matches = re.findall(pattern2, json_text, re.DOTALL | re.IGNORECASE)
        if matches:
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue

        # Strategy 3: Bracket counting algorithm
        json_start = json_text.find('[')
        if json_start == -1:
            json_start = json_text.find('{')

        if json_start != -1:
            bracket_count = 0
            in_string = False
            escape_next = False

            for i in range(json_start, len(json_text)):
                char = json_text[i]

                if escape_next:
                    escape_next = False
                    continue

                if char == '\\':
                    escape_next = True
                    continue

                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue

                if not in_string:
                    if char in ['[', '{']:
                        bracket_count += 1
                    elif char in [']', '}']:
                        bracket_count -= 1
                        if bracket_count == 0:
                            try:
                                return json.loads(json_text[json_start:i+1])
                            except:
                                pass

        # Strategy 4: Greedy JSON array matching
        array_pattern = r'\[(.*?)\]'
        matches = re.findall(array_pattern, json_text, re.DOTALL)
        if matches:
            for match in matches:
                try:
                    return json.loads('[' + match + ']')
                except:
                    continue

        # Strategy 5: Manual object extraction
        object_pattern = r'\{(.*?)\}'
        matches = re.findall(object_pattern, json_text, re.DOTALL)
        if matches:
            for match in matches:
                try:
                    return json.loads('{' + match + '}')
                except:
                    continue

        # Strategy 6: Progressive parsing
        try:
            return json.loads(json_text)
        except:
            pass

        # Strategy 7: Advanced JSON repair
        try:
            return self._repair_json(json_text)
        except:
            pass

        return None

    def _repair_json(self, json_text):
        """Advanced JSON repair strategy"""
        # Find JSON boundaries
        start = json_text.find('[')
        if start == -1:
            start = json_text.find('{')

        if start == -1:
            raise ValueError("No JSON found")

        # Count brackets to find end
        bracket_count = 0
        in_string = False
        escape_next = False
        end_pos = start

        for i in range(start, len(json_text)):
            char = json_text[i]

            if escape_next:
                escape_next = False
                continue

            if char == '\\':
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if not in_string:
                if char in ['[', '{']:
                    bracket_count += 1
                elif char in [']', '}']:
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_pos = i + 1
                        break

        if end_pos == start:
            raise ValueError("Could not find JSON end")

        json_candidate = json_text[start:end_pos]

        # Basic repairs
        json_candidate = re.sub(r',(\s*[}\]])', r'\1', json_candidate)  # Remove trailing commas

        # Fix common issues
        json_candidate = json_candidate.replace('\u0000', '')  # Remove null bytes

        try:
            return json.loads(json_candidate)
        except Exception as e:
            print(f"JSON repair failed: {e}")
            raise

    def get_raw_response_data(self):
        """Try to extract raw response from log file"""
        log_file = "proverbs_c15_all_v_batched_20251202_2221_log.txt"

        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()

            # Look for JSON content in the log
            json_start = log_content.find('JSON text (first 1000 chars):')
            if json_start != -1:
                # Extract the part after the marker
                content_start = json_start + len('JSON text (first 1000 chars):')
                lines = log_content[content_start:].split('\n')

                # Skip the first line (the marker) and collect content
                json_lines = []
                for i, line in enumerate(lines[1:], 1):  # Skip the marker line
                    if line.strip().startswith('2025-12-02') or 'ERROR:' in line:
                        break
                    json_lines.append(line)

                json_content = '\n'.join(json_lines)
                if json_content.strip():
                    print(f"Extracted JSON content from log ({len(json_content)} chars)")
                    return json_content

        except Exception as e:
            print(f"Could not extract from log: {e}")

        return None

    def process_chapter_15_fresh(self):
        """Process Chapter 15 fresh with enhanced error handling"""
        print("Processing Chapter 15 fresh with enhanced error handling...")

        try:
            # Initialize the LLM client
            from hebrew_figurative_db.llm_client.unified_llm_client import UnifiedLLMClient
            llm_client = UnifiedLLMClient()

            # Get the text for Chapter 15
            from sefaria_text import SefariaTextClient
            sefaria_client = SefariaTextClient()
            hebrew_verses, english_verses = sefaria_client.get_book_text('Proverbs', 15)

            print(f"Retrieved {len(hebrew_verses)} verses from Proverbs 15")

            # Create the enhanced prompt (same as main processor)
            chapter_text = ""
            for i, (hebrew, english) in enumerate(zip(hebrew_verses, english_verses), 1):
                chapter_text += f"Verse {i}: {hebrew} - {english}\n"

            prompt = f"""
Analyze the following biblical chapter for figurative language. Focus on identifying metaphor, simile, personification, hyperbole, metonymy, and other figurative expressions.

Chapter context: Proverbs is wisdom literature that often uses comparative and imagistic language to convey moral and ethical teachings.

Text to analyze:
{chapter_text}

CRITICAL MULTI-INSTANCE DETECTION REQUIREMENTS:

For EACH verse, you MUST explicitly determine and report:
1. ZERO instances: No figurative language detected - provide EMPTY "instances" array []
2. ONE instance: Single figurative language expression - provide ONE object in "instances" array
3. MULTIPLE instances: Multiple DISTINCT expressions - provide MULTIPLE objects in "instances" array

ESSENTIAL GUIDELINES:
- Do NOT default to finding exactly one instance per verse
- Some verses may have ZERO figurative language instances - this is VALID
- Some verses may have SEVERAL figurative language instances - this is VALID
- Each instance must represent a DISTINCT figurative expression, NOT different aspects of the same expression

Return your analysis as a JSON array of verse objects with this exact structure:
[
  {{
    "verse": 1,
    "reference": "Proverbs 15:1",
    "deliberation": "Your analysis reasoning for this verse",
    "instances": [
      {{
        "figurative_language": "yes",
        "metaphor": "yes/no",
        "simile": "yes/no",
        "personification": "yes/no",
        "idiom": "yes/no",
        "hyperbole": "yes/no",
        "metonymy": "yes/no",
        "other": "yes/no",
        "hebrew_text": "Hebrew text here",
        "english_text": "English translation here",
        "target": ["Target domain(s)"],
        "vehicle": ["Vehicle/source domain(s)"],
        "ground": ["Common attributes"],
        "posture": ["Rhetorical stance/attitude"],
        "explanation": "Explanation of the figurative language",
        "confidence": 0.0-1.0
      }}
    ]
  }}
]
"""

            # Call the API with retry logic
            model = "gpt-5.1"
            reasoning_effort = "medium"

            print(f"Calling {model} for Proverbs 15...")
            response = llm_client.analyze_with_custom_prompt(
                prompt=prompt,
                model=model,
                reasoning_effort=reasoning_effort,
                max_tokens=16000,
                temperature=0.2
            )

            if not response or not response.content:
                print("No response received")
                return None

            json_text = response.content
            print(f"Received response: {len(json_text)} characters")

            # Try to extract JSON using enhanced strategies
            extracted_data = self.extract_json_with_fallbacks(json_text)

            if extracted_data:
                print(f"Successfully extracted JSON for {len(extracted_data)} verses")
                return extracted_data
            else:
                print("Failed to extract JSON from response")
                # Save raw response for debugging
                with open('chapter15_raw_response.txt', 'w', encoding='utf-8') as f:
                    f.write(json_text)
                print("Raw response saved to chapter15_raw_response.txt")
                return None

        except Exception as e:
            print(f"Error in fresh processing: {e}")
            import traceback
            traceback.print_exc()
            return None

    def save_to_database(self, verse_data):
        """Save extracted verse data to database"""
        try:
            # Create new database
            db_path = "proverbs_c15_recovered.db"
            conn = sqlite3.connect(db_path)

            # Create tables using existing schema
            self.db_manager.create_tables(conn)

            verses_processed = 0
            instances_processed = 0

            for verse_info in verse_data:
                verse_num = verse_info.get('verse', 0)
                reference = verse_info.get('reference', '')
                deliberation = verse_info.get('deliberation', '')
                instances = verse_info.get('instances', [])

                # Get the actual Hebrew and English text
                # This would need to be retrieved from Sefaria or stored somewhere
                hebrew_text = ""
                english_text = ""

                # Insert verse record
                verse_id = self.db_manager.insert_verse(
                    conn=conn,
                    book_name="Proverbs",
                    chapter=15,
                    verse=verse_num,
                    hebrew_text=hebrew_text,
                    english_text=english_text,
                    figurative_detection_deliberation=deliberation
                )

                verses_processed += 1

                # Insert figurative language instances
                for instance in instances:
                    if instance.get('figurative_language', 'no') == 'yes':
                        instance_id = self.db_manager.insert_figurative_language(
                            conn=conn,
                            verse_id=verse_id,
                            figurative_language=instance.get('figurative_language', 'no'),
                            simile=instance.get('simile', 'no'),
                            metaphor=instance.get('metaphor', 'no'),
                            personification=instance.get('personification', 'no'),
                            idiom=instance.get('idiom', 'no'),
                            hyperbole=instance.get('hyperbole', 'no'),
                            metonymy=instance.get('metonymy', 'no'),
                            other=instance.get('other', 'no'),
                            target=instance.get('target', []),
                            vehicle=instance.get('vehicle', []),
                            ground=instance.get('ground', []),
                            posture=instance.get('posture', []),
                            explanation=instance.get('explanation', ''),
                            confidence=instance.get('confidence', 0.0),
                            hebrew_text=instance.get('hebrew_text', ''),
                            english_text=instance.get('english_text', '')
                        )
                        instances_processed += 1

            conn.commit()
            conn.close()

            print(f"Successfully saved {verses_processed} verses and {instances_processed} instances to {db_path}")
            return db_path

        except Exception as e:
            print(f"Error saving to database: {e}")
            import traceback
            traceback.print_exc()
            return None

    def run_recovery(self):
        """Main recovery process"""
        print("=== CHAPTER 15 DETECTION RECOVERY ===")

        # Try to get raw response first
        raw_data = self.get_raw_response_data()

        if raw_data:
            print("Attempting to extract from existing response...")
            extracted_data = self.extract_json_with_fallbacks(raw_data)

            if extracted_data:
                print(f"Successfully recovered {len(extracted_data)} verses from existing response")
                db_path = self.save_to_database(extracted_data)
                if db_path:
                    print(f"Recovery complete! Database saved to: {db_path}")
                    return db_path

        # If recovery fails, process fresh
        print("Processing Chapter 15 fresh...")
        fresh_data = self.process_chapter_15_fresh()

        if fresh_data:
            print(f"Successfully processed {len(fresh_data)} verses fresh")
            db_path = self.save_to_database(fresh_data)
            if db_path:
                print(f"Fresh processing complete! Database saved to: {db_path}")
                return db_path

        print("Recovery failed")
        return None

if __name__ == "__main__":
    recovery = Chapter15DetectionRecovery()
    db_path = recovery.run_recovery()

    if db_path:
        print(f"\n✅ SUCCESS: Chapter 15 database created at {db_path}")
    else:
        print(f"\n❌ FAILED: Could not recover Chapter 15 data")