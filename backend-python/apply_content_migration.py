"""
Apply Content Table Migration to Supabase

This script reads the migration SQL file and executes it via Supabase client.
Since Supabase doesn't have a direct SQL execution API, you'll need to:

1. Go to your Supabase Dashboard
2. Navigate to SQL Editor
3. Copy the contents of migrations/002_add_content_table.sql
4. Paste and execute in the SQL Editor

OR

Run this script if you have direct PostgreSQL access:
python apply_content_migration.py
"""

from app.database import supabase
import os

def apply_migration():
    """
    Apply the content table migration
    """
    print("="*60)
    print("  CONTENT TABLE MIGRATION")
    print("="*60)
    
    # Read migration file
    migration_path = "migrations/002_add_content_table.sql"
    
    if not os.path.exists(migration_path):
        print(f"❌ Migration file not found: {migration_path}")
        return False
    
    with open(migration_path, 'r') as f:
        sql = f.read()
    
    print(f"\n✅ Read migration file: {migration_path}")
    print(f"   SQL length: {len(sql)} characters")
    
    print("\n📋 MANUAL MIGRATION STEPS:")
    print("\n1. Go to: https://supabase.com/dashboard/project/YOUR_PROJECT/sql")
    print("2. Create a new query")
    print("3. Copy the SQL from migrations/002_add_content_table.sql")
    print("4. Paste into the SQL Editor")
    print("5. Click 'Run' to execute")
    
    print("\n" + "="*60)
    print("  MIGRATION SQL PREVIEW")
    print("="*60)
    print(sql[:500] + "..." if len(sql) > 500 else sql)
    
    print("\n" + "="*60)
    print("  After applying migration:")
    print("  1. Check table exists: SELECT * FROM content LIMIT 1;")
    print("  2. Run test suite: python test_content_layer.py")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        apply_migration()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
