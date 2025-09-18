#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapping for converting single subcategory to two-level subcategory system
Based on subcategories.md structure
"""

# Level 1 categories from subcategories.md
LEVEL_1_CATEGORIES = {
    "The Natural World": [
        "animal", "agricultural", "elemental", "geological", "celestial"
    ],
    "Human Institutions and Relationships": [
        "familial", "military", "architectural", "social", "political", "sensory"
    ],
    "Abstract and Internal States": [
        "emotional", "medical", "covenantal", "spiritual", "temporal", "economic", "industrial"
    ]
}

# Mapping from old subcategory values to new two-level system
SUBCATEGORY_MAPPING = {
    # The Natural World
    "animal": ("The Natural World", "animal"),
    "biological": ("The Natural World", "animal"),
    "anatomical": ("The Natural World", "animal"),

    "agricultural": ("The Natural World", "agricultural"),

    "elemental": ("The Natural World", "elemental"),
    "natural": ("The Natural World", "elemental"),
    "maritime": ("The Natural World", "elemental"),

    "geological": ("The Natural World", "geological"),
    "GEOLOGICAL": ("The Natural World", "geological"),
    "geographic": ("The Natural World", "geological"),

    "celestial": ("The Natural World", "celestial"),
    "cosmological": ("The Natural World", "celestial"),

    # Human Institutions and Relationships
    "familial": ("Human Institutions and Relationships", "familial"),
    "Familial": ("Human Institutions and Relationships", "familial"),
    "FAMILIAL": ("Human Institutions and Relationships", "familial"),

    "military": ("Human Institutions and Relationships", "military"),
    "MILITARY": ("Human Institutions and Relationships", "military"),

    "architectural": ("Human Institutions and Relationships", "architectural"),
    "ARCHITECTURAL": ("Human Institutions and Relationships", "architectural"),
    "material": ("Human Institutions and Relationships", "architectural"),

    "social": ("Human Institutions and Relationships", "social"),
    "political": ("Human Institutions and Relationships", "political"),
    "demographic": ("Human Institutions and Relationships", "social"),
    "anthropological": ("Human Institutions and Relationships", "social"),
    "behavioral": ("Human Institutions and Relationships", "social"),
    "legal": ("Human Institutions and Relationships", "social"),

    "sensory": ("Human Institutions and Relationships", "sensory"),
    "physical": ("Human Institutions and Relationships", "sensory"),

    # Abstract and Internal States
    "emotional": ("Abstract and Internal States", "emotional"),
    "Emotional": ("Abstract and Internal States", "emotional"),

    "medical": ("Abstract and Internal States", "medical"),
    "disease": ("Abstract and Internal States", "medical"),

    "covenantal": ("Abstract and Internal States", "covenantal"),
    "spiritual": ("Abstract and Internal States", "spiritual"),
    "religious": ("Abstract and Internal States", "covenantal"),
    "divine": ("Abstract and Internal States", "covenantal"),
    "divine action": ("Abstract and Internal States", "covenantal"),
    "divine judgment": ("Abstract and Internal States", "covenantal"),

    "temporal": ("Abstract and Internal States", "temporal"),
    "TEMPORAL": ("Abstract and Internal States", "temporal"),
    "historical": ("Abstract and Internal States", "temporal"),

    "economic": ("Abstract and Internal States", "economic"),
    "industrial": ("Abstract and Internal States", "industrial"),
    "metallurgical": ("Abstract and Internal States", "industrial"),

    # Handle generic/unclear categories
    "conceptual": ("Abstract and Internal States", "emotional"),
    "CONCEPTUAL": ("Abstract and Internal States", "emotional"),
    "Conceptual": ("Abstract and Internal States", "emotional"),
    "general": ("Abstract and Internal States", "emotional"),
    "human": ("Human Institutions and Relationships", "social"),
    "rhetorical": ("Abstract and Internal States", "emotional"),
    "spatial": ("The Natural World", "geological"),
    "Spatial": ("The Natural World", "geological"),
    "numerical": ("Abstract and Internal States", "temporal"),
}

def get_two_level_subcategory(old_subcategory: str) -> tuple:
    """
    Convert old single subcategory to two-level system

    Args:
        old_subcategory: Original subcategory value

    Returns:
        Tuple of (level_1, level_2) or (None, None) if not found
    """
    if old_subcategory in SUBCATEGORY_MAPPING:
        return SUBCATEGORY_MAPPING[old_subcategory]
    else:
        # For unmapped categories, try to guess based on common patterns
        lower_sub = old_subcategory.lower()

        # Default fallbacks
        if any(word in lower_sub for word in ['god', 'divine', 'holy', 'sacred']):
            return ("Abstract and Internal States", "covenantal")
        elif any(word in lower_sub for word in ['people', 'nation', 'social']):
            return ("Human Institutions and Relationships", "social")
        elif any(word in lower_sub for word in ['heart', 'mind', 'emotion']):
            return ("Abstract and Internal States", "emotional")
        elif any(word in lower_sub for word in ['time', 'day', 'year']):
            return ("Abstract and Internal States", "temporal")
        else:
            # Default to emotional if unclear
            return ("Abstract and Internal States", "emotional")

def validate_mapping():
    """Validate that all level 2 categories are properly assigned to level 1"""
    all_level_2 = set()
    for level_1, level_2_list in LEVEL_1_CATEGORIES.items():
        all_level_2.update(level_2_list)

    mapped_level_2 = set()
    for level_1, level_2 in SUBCATEGORY_MAPPING.values():
        mapped_level_2.add(level_2)

    print("Level 2 categories defined:", sorted(all_level_2))
    print("Level 2 categories used in mapping:", sorted(mapped_level_2))
    print("Unmapped level 2:", sorted(mapped_level_2 - all_level_2))

if __name__ == "__main__":
    validate_mapping()