#!/usr/bin/env python3
"""
Setup script to create Supabase database schema and migrate CSV data
Run this once after setting up your Supabase project
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client
    import pandas as pd
    import hashlib
    from datetime import datetime
except ImportError as e:
    print(f"❌ Missing required packages: {e}")
    print("Run: pip install supabase pandas python-dotenv")
    sys.exit(1)

def create_database_schema(client):
    """Check if the stilbar_compounds table exists"""
    print("🔍 Checking database schema...")
    
    try:
        # Try to query the table to check if it exists
        result = client.table('stilbar_compounds').select('count', count='exact').execute()
        print("✅ Table 'stilbar_compounds' exists and is accessible")
        return True
        
    except Exception as e:
        print(f"❌ Table doesn't exist or not accessible: {e}")
        print("💡 Please create the table manually in Supabase dashboard")
        print("Go to: Database → SQL Editor and run:")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS stilbar_compounds (
            id SERIAL PRIMARY KEY,
            hash_id VARCHAR(16) UNIQUE NOT NULL,
            compound_name TEXT NOT NULL,
            stilbar_code TEXT,
            smiles TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        create_indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_stilbar_code ON stilbar_compounds(stilbar_code);",
            "CREATE INDEX IF NOT EXISTS idx_compound_name ON stilbar_compounds(compound_name);", 
            "CREATE INDEX IF NOT EXISTS idx_hash_id ON stilbar_compounds(hash_id);"
        ]
        
        print(create_table_sql)
        for idx_sql in create_indexes_sql:
            print(idx_sql)
        return False

def generate_hash(stilbar_code: str, compound_name: str = '') -> str:
    """Generate hash for compound"""
    clean_stilbar = stilbar_code.strip().replace(' ', '').replace('-', '–')
    combined = f"{clean_stilbar}|{compound_name.strip()}"
    hash_obj = hashlib.sha256(combined.encode('utf-8'))
    return hash_obj.hexdigest()[:16]

def migrate_csv_data(client, csv_file='Stilabar_Smiles_Perfect.csv'):
    """Migrate data from CSV to Supabase"""
    print(f"📊 Migrating data from {csv_file}...")
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return False
    
    try:
        # Read CSV data
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        print(f"📁 Found {len(df)} compounds in CSV")
        
        # Prepare data for insertion
        compounds_data = []
        current_time = datetime.utcnow().isoformat()
        
        for index, row in df.iterrows():
            stilbar_code = str(row.get('barcode', '')).strip()
            compound_name = str(row.get('compound_name', '')).strip()
            smiles = str(row.get('smiles', '')).strip()
            
            if not compound_name or not smiles:
                print(f"⚠️ Skipping row {index + 1}: missing compound_name or smiles")
                continue
            
            hash_id = generate_hash(stilbar_code if stilbar_code else compound_name, compound_name)
            
            compound_data = {
                'hash_id': hash_id,
                'compound_name': compound_name,
                'stilbar_code': stilbar_code,
                'smiles': smiles,
                'created_at': current_time,
                'updated_at': current_time
            }
            compounds_data.append(compound_data)
        
        print(f"✅ Prepared {len(compounds_data)} compounds for insertion")
        
        # Insert data in batches
        batch_size = 50
        inserted_count = 0
        
        for i in range(0, len(compounds_data), batch_size):
            batch = compounds_data[i:i + batch_size]
            
            try:
                result = client.table('stilbar_compounds').insert(batch).execute()
                inserted_count += len(batch)
                print(f"✅ Inserted batch {i//batch_size + 1}: {len(batch)} compounds")
                
            except Exception as e:
                print(f"❌ Error inserting batch {i//batch_size + 1}: {e}")
                # Try individual insertions for this batch
                for compound in batch:
                    try:
                        client.table('stilbar_compounds').insert(compound).execute()
                        inserted_count += 1
                    except Exception as e2:
                        print(f"⚠️ Failed to insert {compound['compound_name']}: {e2}")
        
        print(f"🎉 Migration complete! Inserted {inserted_count} compounds")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

def verify_migration(client):
    """Verify the migration was successful"""
    print("🔍 Verifying migration...")
    
    try:
        result = client.table('stilbar_compounds').select('count', count='exact').execute()
        count = result.count
        print(f"✅ Database contains {count} compounds")
        
        # Get a sample record
        sample_result = client.table('stilbar_compounds').select('*').limit(1).execute()
        if sample_result.data:
            sample = sample_result.data[0]
            print(f"📝 Sample record: {sample['compound_name']} ({sample['stilbar_code']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Supabase database for StilBAR compounds...")
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        print("Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file")
        sys.exit(1)
    
    # Initialize Supabase client
    try:
        client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)
    
    # Step 1: Check if schema exists (you've already created it)
    schema_exists = create_database_schema(client)
    if not schema_exists:
        print("⚠️ Please create the table manually in Supabase and re-run this script")
        return
    
    # Step 2: Migrate data
    migration_successful = migrate_csv_data(client)
    if not migration_successful:
        print("❌ Migration failed")
        return
    
    # Step 3: Verify
    verification_successful = verify_migration(client)
    if verification_successful:
        print("🎉 Setup complete! Your Supabase database is ready.")
        print("💡 You can now run your Streamlit app with Supabase backend")
    else:
        print("⚠️ Setup completed but verification failed")

if __name__ == "__main__":
    main()