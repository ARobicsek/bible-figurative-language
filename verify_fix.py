"""Verify that the highlighting fix works"""
import re

# Test data from Psalms 84:4
verse_text = 'גַּם־צִפּ֨וֹר מָ֪צְאָה בַ֡יִת וּדְר֤וֹר&thinsp;׀ קֵ֥ן לָהּ֮ אֲשֶׁר־שָׁ֢תָה אֶפְרֹ֫חֶ֥יהָ אֶֽת־מִ֭זְבְּחוֹתֶיךָ יְהֹוָ֣ה צְבָא֑וֹת מַ֝לְכִּ֗י וֵאלֹהָֽי'
fig_text = 'גַּם־צִפּ֨וֹר מָ֪צְאָה בַ֡יִת וּדְר֤וֹר&thinsp;׀ קֵ֥ן לָהּ֮ אֲשֶׁר־שָׁ֢תָה אֶפְרֹ֫חֶ֥יהָ אֶֽת־מִ֭זְבְּחוֹתֶיךָ'

print("=" * 80)
print("VERIFICATION: Psalms 84:4 Highlighting Fix")
print("=" * 80)

# Test 1: Basic text matching
print("\n1. Basic text matching:")
print(f"   Figurative text is in verse: {fig_text in verse_text}")

# Test 2: Build regex pattern with HTML entity handling (NEW FIX)
print("\n2. Building regex pattern with HTML entity handling:")

trimmed_fig_text = fig_text.strip()
flexible_pattern = ''
i = 0
entity_count = 0

while i < len(trimmed_fig_text):
    # Check if we're at the start of an HTML entity
    if trimmed_fig_text[i] == '&':
        entity_match = re.match(r'^&[a-zA-Z0-9#]+;', trimmed_fig_text[i:])
        if entity_match:
            # Found complete HTML entity
            entity = entity_match.group(0)
            escaped_entity = re.escape(entity)
            flexible_pattern += escaped_entity + r'(?:<br\s*\/??|<[^>]*>|\{[^}]*\}|[\u0591-\u05BD\u05BF-\u05C7\u05F0-\u05F4])*'
            i += len(entity)
            entity_count += 1
            print(f"   Found HTML entity: {entity}")
            continue

    # Regular character handling
    char = trimmed_fig_text[i]
    if char == ' ':
        flexible_pattern += r'(?:<br\s*\/??|<[^>]*>|&[a-zA-Z0-9#]+;|\{[^}]*\}|־|[\u0591-\u05BD\u05BF-\u05C7\u05F0-\u05F4]|\s)+'
    else:
        escaped_char = re.escape(char)
        flexible_pattern += escaped_char + r'(?:<br\s*\/??|<[^>]*>|&[a-zA-Z0-9#]+;|\{[^}]*\}|[\u0591-\u05BD\u05BF-\u05C7\u05F0-\u05F4])*'
    i += 1

print(f"   Total HTML entities found: {entity_count}")
print(f"   Pattern length: {len(flexible_pattern)} characters")

# Test 3: Apply regex
print("\n3. Testing regex match:")
regex = re.compile(flexible_pattern)
match = regex.search(verse_text)

if match:
    matched_text = match.group(0)
    print(f"   SUCCESS! Matched {len(matched_text)} characters")
    print(f"   Match position: {match.start()} to {match.end()}")
    print(f"   Contains &thinsp;: {'&thinsp;' in matched_text}")
else:
    print(f"   FAILED! No match found")

print("\n4. Comparison with old approach (split every character):")
# Old approach
old_pattern = ''.join([re.escape(c) + r'(?:<br\s*\/??|<[^>]*>|&[a-zA-Z0-9#]+;|\{[^}]*\}|־|[\u0591-\u05C7\u05F0-\u05F4])*' for c in fig_text])
old_regex = re.compile(old_pattern)
old_match = old_regex.search(verse_text)
print(f"   Old approach match: {'SUCCESS' if old_match else 'FAILED'}")

print("\n" + "=" * 80)
print("CONCLUSION:")
if match:
    print("SUCCESS - The fix works! HTML entities are now handled correctly.")
else:
    print("FAILED - The fix needs more work.")
print("=" * 80)
