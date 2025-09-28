#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Migration Script: Create Tag-Based Figurative Language System
Transforms rigid categorical system to flexible tag-based approach
"""

import sqlite3
import json
from typing import Dict, List, Tuple
from pathlib import Path

class TagSystemMigrator:
    """Handles migration from categorical to tag-based system"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def create_backup(self, backup_path: str = None):
        """Create database backup before migration"""
        if backup_path is None:
            backup_path = f"{self.db_path}.backup"

        print(f"Creating backup: {backup_path}")

        # Simple file copy backup
        import shutil
        shutil.copy2(self.db_path, backup_path)
        print(f"Backup created successfully at {backup_path}")
        return backup_path

    def add_schema_enhancements(self):
        """Add new tables and columns for tag system"""
        print("Adding tag system schema enhancements...")

        # Add primary category columns to existing figurative_language table
        try:
            self.cursor.execute('ALTER TABLE figurative_language ADD COLUMN primary_target_category TEXT')
            print("Added primary_target_category column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("primary_target_category column already exists")
            else:
                raise

        try:
            self.cursor.execute('ALTER TABLE figurative_language ADD COLUMN primary_vehicle_category TEXT')
            print("Added primary_vehicle_category column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("primary_vehicle_category column already exists")
            else:
                raise

        try:
            self.cursor.execute('ALTER TABLE figurative_language ADD COLUMN primary_ground_category TEXT')
            print("Added primary_ground_category column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("primary_ground_category column already exists")
            else:
                raise

        # Create tag system tables
        self.create_tag_system_tables()
        self.conn.commit()

    def create_tag_system_tables(self):
        """Create new tables for tag system"""
        print("Creating tag system tables...")

        # Tag categories table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tag_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dimension TEXT NOT NULL CHECK(dimension IN ('target', 'vehicle', 'ground')),
                category_name TEXT NOT NULL,
                description TEXT,
                parent_category_id INTEGER,
                sort_order INTEGER DEFAULT 0,
                active TEXT CHECK(active IN ('yes', 'no')) DEFAULT 'yes',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(dimension, category_name),
                FOREIGN KEY (parent_category_id) REFERENCES tag_categories (id)
            )
        ''')

        # Tags table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT NOT NULL,
                tag_category_id INTEGER NOT NULL,
                dimension TEXT NOT NULL CHECK(dimension IN ('target', 'vehicle', 'ground')),
                description TEXT,
                synonyms TEXT,
                related_tags TEXT,
                usage_notes TEXT,
                active TEXT CHECK(active IN ('yes', 'no')) DEFAULT 'yes',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(tag_name, dimension),
                FOREIGN KEY (tag_category_id) REFERENCES tag_categories (id)
            )
        ''')

        # Figurative tags (many-to-many) table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS figurative_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                figurative_language_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                dimension TEXT NOT NULL CHECK(dimension IN ('target', 'vehicle', 'ground')),
                confidence REAL CHECK(confidence >= 0.0 AND confidence <= 1.0) DEFAULT 1.0,
                is_primary TEXT CHECK(is_primary IN ('yes', 'no')) DEFAULT 'no',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(figurative_language_id, tag_id, dimension),
                FOREIGN KEY (figurative_language_id) REFERENCES figurative_language (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id)
            )
        ''')

        # Create indexes
        self.create_tag_system_indexes()

        print("Tag system tables created successfully")

    def create_tag_system_indexes(self):
        """Create performance indexes for tag system"""
        print("Creating tag system indexes...")

        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_primary_target_category ON figurative_language (primary_target_category)',
            'CREATE INDEX IF NOT EXISTS idx_primary_vehicle_category ON figurative_language (primary_vehicle_category)',
            'CREATE INDEX IF NOT EXISTS idx_primary_ground_category ON figurative_language (primary_ground_category)',
            'CREATE INDEX IF NOT EXISTS idx_tag_categories_dimension ON tag_categories (dimension)',
            'CREATE INDEX IF NOT EXISTS idx_tag_categories_active ON tag_categories (active)',
            'CREATE INDEX IF NOT EXISTS idx_tags_dimension ON tags (dimension)',
            'CREATE INDEX IF NOT EXISTS idx_tags_category ON tags (tag_category_id)',
            'CREATE INDEX IF NOT EXISTS idx_tags_active ON tags (active)',
            'CREATE INDEX IF NOT EXISTS idx_figurative_tags_instance ON figurative_tags (figurative_language_id)',
            'CREATE INDEX IF NOT EXISTS idx_figurative_tags_tag ON figurative_tags (tag_id)',
            'CREATE INDEX IF NOT EXISTS idx_figurative_tags_dimension ON figurative_tags (dimension)',
            'CREATE INDEX IF NOT EXISTS idx_figurative_tags_primary ON figurative_tags (is_primary)',
            'CREATE INDEX IF NOT EXISTS idx_figurative_tags_instance_dimension ON figurative_tags (figurative_language_id, dimension)',
            'CREATE INDEX IF NOT EXISTS idx_figurative_tags_tag_dimension ON figurative_tags (tag_id, dimension)',
            'CREATE INDEX IF NOT EXISTS idx_tags_dimension_category ON tags (dimension, tag_category_id)'
        ]

        for index_sql in indexes:
            self.cursor.execute(index_sql)

        print("Tag system indexes created successfully")

    def populate_tag_taxonomy(self):
        """Populate initial tag taxonomy from file"""
        print("Populating initial tag taxonomy...")

        # Read and execute initial taxonomy SQL
        taxonomy_file = Path(__file__).parent / "initial_tag_taxonomy.sql"
        if taxonomy_file.exists():
            with open(taxonomy_file, 'r', encoding='utf-8') as f:
                taxonomy_sql = f.read()

                # Split by semicolon and execute each statement
                statements = [stmt.strip() for stmt in taxonomy_sql.split(';') if stmt.strip()]
                for statement in statements:
                    if statement and not statement.startswith('--'):
                        try:
                            self.cursor.execute(statement)
                        except sqlite3.Error as e:
                            print(f"Error executing statement: {e}")
                            print(f"Statement: {statement[:100]}...")

                self.conn.commit()
                print("Initial tag taxonomy populated successfully")
        else:
            print("Warning: initial_tag_taxonomy.sql not found")

    def migrate_categorical_data(self):
        """Migrate existing categorical data to tag system"""
        print("Migrating categorical data to tag system...")

        # Mapping dictionaries for categorical to tag conversion
        target_mappings = {
            'God': 'deity',
            'natural world': 'natural_world',
            'state of being': 'state_of_being',
            'human parts': 'human_parts',
            'human action': 'human_action',
            'abstract concept': 'abstract_concept',
            'human individual': 'human_individual',
            'human collective': 'human_collective',
            'time': 'time_duration'
        }

        vehicle_mappings = {
            'natural world': 'natural_world',
            'human action': 'human_action',
            'human parts': 'human_parts',
            'animal': 'animal',
            'human relationship': 'human_relationship',
            'object': 'object_artifact',
            'plant': 'plant_agriculture',
            'structure': 'structure_building',
            'military': 'military_warfare'
        }

        ground_mappings = {
            'essential nature or identity': 'essential_nature',
            'physical quality': 'physical_quality',
            'status': 'status_position',
            'functional role': 'functional_role',
            'relational quality': 'relational_quality',
            'emotional quality': 'emotional_quality',
            'temporal quality': 'temporal_quality',
            'moral quality': 'moral_quality'
        }

        # Update primary categories
        print("Updating primary categories...")

        for old_cat, new_cat in target_mappings.items():
            self.cursor.execute(
                'UPDATE figurative_language SET primary_target_category = ? WHERE target_level_1 = ?',
                (new_cat, old_cat)
            )

        for old_cat, new_cat in vehicle_mappings.items():
            self.cursor.execute(
                'UPDATE figurative_language SET primary_vehicle_category = ? WHERE vehicle_level_1 = ?',
                (new_cat, old_cat)
            )

        for old_cat, new_cat in ground_mappings.items():
            self.cursor.execute(
                'UPDATE figurative_language SET primary_ground_category = ? WHERE ground_level_1 = ?',
                (new_cat, old_cat)
            )

        self.conn.commit()

        # Create detailed tag assignments
        self.create_detailed_tag_assignments()

        print("Categorical data migration completed")

    def create_detailed_tag_assignments(self):
        """Create detailed tag assignments based on categorical and specific data"""
        print("Creating detailed tag assignments...")

        # Get all figurative language instances
        self.cursor.execute('''
            SELECT id, target_level_1, target_specific, vehicle_level_1, vehicle_specific,
                   ground_level_1, ground_specific, figurative_text, explanation,
                   primary_target_category, primary_vehicle_category, primary_ground_category
            FROM figurative_language
            WHERE final_figurative_language = 'yes'
        ''')

        instances = self.cursor.fetchall()
        print(f"Processing {len(instances)} figurative language instances...")

        for instance in instances:
            fl_id = instance[0]
            self.assign_tags_to_instance(fl_id, instance)

        self.conn.commit()
        print("Detailed tag assignments completed")

    def assign_tags_to_instance(self, fl_id: int, instance_data: tuple):
        """Assign multiple tags to a single figurative language instance"""
        (_, target_l1, target_spec, vehicle_l1, vehicle_spec, ground_l1, ground_spec,
         fig_text, explanation, primary_target, primary_vehicle, primary_ground) = instance_data

        # Assign target tags
        target_tags = self.determine_target_tags(target_l1, target_spec, explanation)
        for tag_name in target_tags:
            self.assign_tag(fl_id, tag_name, 'target', primary=(tag_name == primary_target))

        # Assign vehicle tags
        vehicle_tags = self.determine_vehicle_tags(vehicle_l1, vehicle_spec, explanation)
        for tag_name in vehicle_tags:
            self.assign_tag(fl_id, tag_name, 'vehicle', primary=(tag_name == primary_vehicle))

        # Assign ground tags
        ground_tags = self.determine_ground_tags(ground_l1, ground_spec, explanation)
        for tag_name in ground_tags:
            self.assign_tag(fl_id, tag_name, 'ground', primary=(tag_name == primary_ground))

    def determine_target_tags(self, level_1: str, specific: str, explanation: str) -> List[str]:
        """Determine multiple target tags based on categorical and textual analysis"""
        tags = []

        # Base category mapping
        if level_1 == 'God':
            tags.append('deity')
            if specific and 'spirit' in specific.lower():
                tags.append('spirit_of_god')
            if specific and any(word in specific.lower() for word in ['presence', 'glory']):
                tags.append('divine_presence')
            tags.append('god')

        elif level_1 == 'natural world':
            tags.append('natural_world')
            if specific and any(word in specific.lower() for word in ['sun', 'moon', 'star', 'light']):
                tags.append('celestial_body')
            if specific and any(word in specific.lower() for word in ['earth', 'land', 'ground']):
                tags.append('earth_land')
            if specific and any(word in specific.lower() for word in ['water', 'sea', 'river']):
                tags.append('water_element')
            if specific and any(word in specific.lower() for word in ['creation', 'created', 'things']):
                tags.append('created_things')

        elif level_1 == 'state of being':
            tags.append('state_of_being')
            if specific and any(word in specific.lower() for word in ['marriage', 'marital', 'union']):
                tags.append('marital_union')
            if specific and any(word in specific.lower() for word in ['covenant', 'relationship']):
                tags.append('covenant_relationship')

        elif level_1 == 'human parts':
            tags.append('human_parts')

        return tags

    def determine_vehicle_tags(self, level_1: str, specific: str, explanation: str) -> List[str]:
        """Determine multiple vehicle tags based on categorical and textual analysis"""
        tags = []

        if level_1 == 'natural world':
            tags.append('natural_world')
            if specific and any(word in specific.lower() for word in ['bird', 'eagle', 'dove']):
                tags.append('animal')
                tags.append('bird')
                if 'eagle' in specific.lower():
                    tags.append('eagle')
                if 'dove' in specific.lower():
                    tags.append('dove')
            if specific and any(word in specific.lower() for word in ['hovering', 'brooding']):
                tags.append('hovering_brooding')
            if specific and any(word in specific.lower() for word in ['host', 'army', 'organized']):
                tags.append('organized_host')

        elif level_1 == 'human action':
            tags.append('human_action')
            if specific and any(word in specific.lower() for word in ['governance', 'rule', 'dominion']):
                tags.append('governance_rule')
            if specific and any(word in specific.lower() for word in ['nurture', 'care', 'protect']):
                tags.append('nurturing_care')

        elif level_1 == 'human parts':
            tags.append('human_parts')
            if specific and any(word in specific.lower() for word in ['flesh', 'body']):
                tags.append('flesh_body')

        elif level_1 == 'animal':
            tags.append('animal')
            if specific and 'bird' in specific.lower():
                tags.append('bird')

        return tags

    def determine_ground_tags(self, level_1: str, specific: str, explanation: str) -> List[str]:
        """Determine multiple ground tags based on categorical and textual analysis"""
        tags = []

        if level_1 == 'essential nature or identity':
            tags.append('essential_nature')
            if specific and any(word in specific.lower() for word in ['preparatory', 'nurturing']):
                tags.append('preparatory_nurturing')
            if specific and any(word in specific.lower() for word in ['unity', 'oneness', 'holistic']):
                tags.append('holistic_unity')
            if specific and any(word in specific.lower() for word in ['identity', 'shared']):
                tags.append('shared_identity')

        elif level_1 == 'physical quality':
            tags.append('physical_quality')
            if specific and any(word in specific.lower() for word in ['vast', 'magnitude', 'great']):
                tags.append('vastness_magnitude')
            if specific and any(word in specific.lower() for word in ['order', 'organize', 'discipline']):
                tags.append('order_organization')

        elif level_1 == 'status':
            tags.append('status_position')
            if specific and any(word in specific.lower() for word in ['primary', 'authority', 'chief']):
                tags.append('primary_authority')
            if specific and any(word in specific.lower() for word in ['influence', 'ordering']):
                tags.append('ordering_influence')

        return tags

    def assign_tag(self, fl_id: int, tag_name: str, dimension: str, primary: bool = False):
        """Assign a specific tag to a figurative language instance"""
        # Get tag ID
        self.cursor.execute('SELECT id FROM tags WHERE tag_name = ? AND dimension = ?', (tag_name, dimension))
        tag_result = self.cursor.fetchone()

        if tag_result:
            tag_id = tag_result[0]
            try:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO figurative_tags
                    (figurative_language_id, tag_id, dimension, is_primary, confidence)
                    VALUES (?, ?, ?, ?, ?)
                ''', (fl_id, tag_id, dimension, 'yes' if primary else 'no', 1.0))
            except sqlite3.IntegrityError:
                # Tag assignment already exists
                pass

    def validate_migration(self):
        """Validate migration success and data integrity"""
        print("Validating migration...")

        # Count original vs migrated instances
        self.cursor.execute('SELECT COUNT(*) FROM figurative_language WHERE final_figurative_language = "yes"')
        original_count = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(DISTINCT figurative_language_id) FROM figurative_tags')
        tagged_count = self.cursor.fetchone()[0]

        print(f"Original figurative instances: {original_count}")
        print(f"Instances with tags: {tagged_count}")
        print(f"Migration coverage: {(tagged_count/original_count*100):.1f}%" if original_count > 0 else "N/A")

        # Tag distribution analysis
        self.cursor.execute('''
            SELECT dimension, COUNT(*) as total_tags, COUNT(DISTINCT tag_id) as unique_tags
            FROM figurative_tags
            GROUP BY dimension
        ''')

        print("\nTag distribution by dimension:")
        for row in self.cursor.fetchall():
            print(f"  {row[0]}: {row[1]} total assignments, {row[2]} unique tags")

        # Average tags per instance
        self.cursor.execute('''
            SELECT dimension, AVG(tag_count) as avg_tags_per_instance
            FROM (
                SELECT figurative_language_id, dimension, COUNT(*) as tag_count
                FROM figurative_tags
                GROUP BY figurative_language_id, dimension
            ) subquery
            GROUP BY dimension
        ''')

        print("\nAverage tags per instance by dimension:")
        for row in self.cursor.fetchall():
            print(f"  {row[0]}: {row[1]:.1f} tags per instance")

        return tagged_count >= original_count * 0.95  # 95% coverage threshold

    def run_full_migration(self):
        """Execute complete migration process"""
        print("Starting full tag system migration...")

        try:
            self.connect()

            # Create backup
            backup_path = self.create_backup()

            # Execute migration phases
            self.add_schema_enhancements()
            self.populate_tag_taxonomy()
            self.migrate_categorical_data()

            # Validate results
            success = self.validate_migration()

            if success:
                print("\n✅ Migration completed successfully!")
                print(f"Backup available at: {backup_path}")
            else:
                print("\n❌ Migration validation failed - check results")

            return success

        except Exception as e:
            print(f"\n💥 Migration failed with error: {e}")
            print("Database backup available for rollback")
            raise
        finally:
            self.disconnect()


def main():
    """Main execution function"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python create_tag_system.py <database_path>")
        print("Example: python create_tag_system.py genesis_all_c_all_v_20250922_1050.db")
        return

    db_path = sys.argv[1]

    if not Path(db_path).exists():
        print(f"Error: Database file {db_path} not found")
        return

    migrator = TagSystemMigrator(db_path)
    success = migrator.run_full_migration()

    if success:
        print("\n🎉 Tag-based figurative language system is ready!")
        print("You can now use multi-dimensional tag searches for advanced biblical analysis.")
    else:
        print("\n🔧 Migration needs attention - check validation results")


if __name__ == "__main__":
    main()