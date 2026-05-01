#!/usr/bin/env python3
"""
Script to update all under-construction plant deadlines in the database
This normalizes past deadlines to future dates
"""

import sys
import json
import sqlite3
from pathlib import Path

# Add the app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import Database

def main():
    print("=" * 70)
    print("Updating Under-Construction Plant Deadlines")
    print("=" * 70)
    print()
    
    # Initialize database
    db = Database()
    
    # Get all under-construction plants
    print("Fetching under-construction plants from database...")
    plants = db.get_all_plants("under_construction")
    print(f"Found {len(plants)} under-construction plants")
    print()
    
    if len(plants) == 0:
        print("⚠️  No under-construction plants found in database.")
        print("   Run the backend server to fetch data from NVE first.")
        return 1
    
    # Update each plant with normalized deadline
    updated_count = 0
    unchanged_count = 0
    
    print("Processing plants...")
    print("-" * 70)
    
    for plant in plants:
        old_deadline = plant.get('deadline')
        new_deadline = db.normalize_deadline(old_deadline)
        
        if old_deadline != new_deadline:
            # Update the plant data
            plant['deadline'] = new_deadline
            updated_count += 1
            print(f"✓ {plant['name'][:50]:<50} | {old_deadline} → {new_deadline}")
        else:
            unchanged_count += 1
    
    print("-" * 70)
    print()
    
    # Save updated plants back to database
    if updated_count > 0:
        print(f"Saving {updated_count} updated plants to database...")
        db.save_plants(plants, "under_construction")
        print("✅ Database updated successfully!")
    else:
        print("ℹ️  No plants needed updating")
    
    print()
    print("=" * 70)
    print("Summary:")
    print(f"  Total plants:     {len(plants)}")
    print(f"  Updated:          {updated_count}")
    print(f"  Already current:  {unchanged_count}")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Restart your frontend if it's running")
    print("  2. The timeline slider should now filter plants correctly")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

