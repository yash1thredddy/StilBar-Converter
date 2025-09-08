#!/usr/bin/env python3
"""
Hash-based compound management system for StilBAR compounds
Uses StilBAR codes to generate unique hashes for consistent identification
"""
import hashlib
import csv
import json
from typing import Dict, List, Tuple, Optional

class HashCompoundManager:
    """Manage compounds using hash-based identification from StilBAR codes"""
    
    def __init__(self, csv_file: str = 'Stilabar_Smiles_Perfect.csv'):
        self.csv_file = csv_file
        self.compounds = {}  # hash -> compound data
        self.stilbar_to_hash = {}  # stilbar -> hash
        self.load_compounds()
    
    def generate_hash(self, stilbar_code: str, compound_name: str = '') -> str:
        """Generate a unique hash from StilBAR code and compound name"""
        # Clean the stilbar code
        clean_stilbar = stilbar_code.strip().replace(' ', '').replace('-', '–')
        # Combine stilbar and compound name for uniqueness
        combined = f"{clean_stilbar}|{compound_name.strip()}"
        # Generate SHA-256 hash and take first 8 characters
        hash_obj = hashlib.sha256(combined.encode('utf-8'))
        return hash_obj.hexdigest()[:8]
    
    def load_compounds(self):
        """Load all compounds from CSV and create hash mapping"""
        # Clear existing data first
        self.compounds = {}
        self.stilbar_to_hash = {}
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    if not row.get('num') or not row.get('smiles'):
                        print(f"🔍 Skipping row due to missing num or smiles: {row}")
                        continue
                    
                    stilbar_code = row.get('barcode', '').strip()
                    compound_name = row.get('compound_name', '').strip()
                    smiles = row.get('smiles', '').strip()
                    
                    # Generate hash from StilBAR code and compound name for uniqueness
                    hash_key = self.generate_hash(stilbar_code if stilbar_code else compound_name, compound_name)
                    
                    # Store compound data
                    compound_data = {
                        'hash': hash_key,
                        'name': compound_name,
                        'stilbar': stilbar_code,
                        'smiles': smiles,
                        'original_num': row.get('num', '')
                    }
                    
                    self.compounds[hash_key] = compound_data
                    if stilbar_code:
                        self.stilbar_to_hash[stilbar_code] = hash_key
                
                print(f"✅ Loaded {len(self.compounds)} compounds with hash-based IDs")
                
        except FileNotFoundError:
            print(f"❌ CSV file not found: {self.csv_file}")
        except Exception as e:
            print(f"❌ Error loading compounds: {e}")
    
    def get_compound_by_stilbar(self, stilbar_code: str) -> Optional[Dict]:
        """Get compound data by StilBAR code"""
        # Try direct lookup first
        hash_key = self.stilbar_to_hash.get(stilbar_code)
        if hash_key:
            return self.compounds.get(hash_key)
        
        # Try generating hash and looking up (without compound name since we don't know it)
        # This won't work perfectly with the new system, but we'll try
        return None
    
    def get_compound_by_hash(self, hash_key: str) -> Optional[Dict]:
        """Get compound data by hash"""
        return self.compounds.get(hash_key)
    
    def add_compound(self, name: str, stilbar_code: str, smiles: str) -> str:
        """Add a new compound and return its hash"""
        # Generate hash
        hash_key = self.generate_hash(stilbar_code, name)
        
        # Check if already exists
        if hash_key in self.compounds:
            raise ValueError(f"Compound with StilBAR code '{stilbar_code}' already exists (hash: {hash_key})")
        
        # Create compound data
        compound_data = {
            'hash': hash_key,
            'name': name,
            'stilbar': stilbar_code,
            'smiles': smiles,
            'original_num': str(len(self.compounds) + 1)  # Sequential for display
        }
        
        # Store in memory
        self.compounds[hash_key] = compound_data
        if stilbar_code:
            self.stilbar_to_hash[stilbar_code] = hash_key
        
        # Add to CSV
        self._add_to_csv(compound_data)
        
        return hash_key
    
    def delete_compounds(self, hash_keys: List[str]) -> Dict:
        """Delete compounds by hash keys"""
        result = {
            'success': False,
            'deleted_count': 0,
            'deleted_compounds': [],
            'errors': []
        }
        
        try:
            # Validate hash keys
            compounds_to_delete = []
            for hash_key in hash_keys:
                if hash_key in self.compounds:
                    compounds_to_delete.append(self.compounds[hash_key])
                else:
                    result['errors'].append(f"Hash not found: {hash_key}")
            
            if not compounds_to_delete:
                result['errors'].append("No valid compounds found to delete")
                return result
            
            # Create backup
            backup_file = self.csv_file + '.backup'
            import shutil
            shutil.copy(self.csv_file, backup_file)
            print(f"✅ Created backup: {backup_file}")
            
            # Remove from CSV
            self._remove_from_csv([comp['hash'] for comp in compounds_to_delete])
            
            # Remove from memory
            for compound in compounds_to_delete:
                hash_key = compound['hash']
                stilbar = compound['stilbar']
                
                del self.compounds[hash_key]
                if stilbar and stilbar in self.stilbar_to_hash:
                    del self.stilbar_to_hash[stilbar]
                
                result['deleted_compounds'].append({
                    'hash': hash_key,
                    'name': compound['name'],
                    'stilbar': compound['stilbar']
                })
            
            result['deleted_count'] = len(compounds_to_delete)
            result['success'] = True
            
            print(f"✅ Successfully deleted {result['deleted_count']} compounds")
            return result
            
        except Exception as e:
            result['errors'].append(f"Exception during deletion: {str(e)}")
            return result
    
    def _add_to_csv(self, compound_data: Dict):
        """Add compound to CSV file"""
        try:
            # Read existing data
            existing_data = []
            with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                existing_data = list(reader)
            
            # Add new compound (use hash as the ID for consistency)
            new_row = [
                compound_data['hash'],  # Use hash instead of sequential number
                compound_data['name'],
                compound_data['stilbar'],
                compound_data['smiles']
            ]
            existing_data.append(new_row)
            
            # Write back to CSV
            with open(self.csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerows(existing_data)
            
        except Exception as e:
            raise Exception(f"Failed to add to CSV: {e}")
    
    def _remove_from_csv(self, hash_keys: List[str]):
        """Remove compounds from CSV by finding them by compound data"""
        try:
            # Read existing data
            existing_data = []
            with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                header = reader.fieldnames
                existing_data = [header]  # Keep header as list
                for row in reader:
                    existing_data.append([row.get(field, '') for field in header])
            
            print(f"🔍 CSV has {len(existing_data)} rows (including header)")
            
            # Get compound details for hashes to delete
            compounds_to_delete = {}
            for hash_key in hash_keys:
                if hash_key in self.compounds:
                    comp = self.compounds[hash_key]
                    compounds_to_delete[hash_key] = {
                        'name': comp['name'],
                        'stilbar': comp['stilbar'],
                        'smiles': comp['smiles']
                    }
            
            print(f"🔍 Looking for {len(compounds_to_delete)} compounds to delete")
            
            # Filter out deleted compounds by matching name+stilbar+smiles
            filtered_data = [existing_data[0]]  # Keep header
            deleted_count = 0
            
            for i, row in enumerate(existing_data[1:], 1):
                if len(row) >= 4:
                    row_name = row[1].strip()
                    row_stilbar = row[2].strip()
                    row_smiles = row[3].strip()
                    
                    # Check if this row matches any compound to delete
                    should_delete = False
                    for hash_key, comp_data in compounds_to_delete.items():
                        if (row_name == comp_data['name'] and 
                            row_stilbar == comp_data['stilbar'] and 
                            row_smiles == comp_data['smiles']):
                            should_delete = True
                            deleted_count += 1
                            print(f"🗑️ Deleting CSV row {i}: {row_name} ({row_stilbar})")
                            break
                    
                    if not should_delete:
                        filtered_data.append(row)
                else:
                    print(f"🔍 Skipping invalid row {i}: {row}")
            
            print(f"🔍 Filtered data: {len(existing_data)} -> {len(filtered_data)} rows")
            print(f"🔍 Deleted {deleted_count} rows from CSV")
            
            # Write back to CSV
            with open(self.csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerows(filtered_data)
            
        except Exception as e:
            raise Exception(f"Failed to remove from CSV: {e}")
    
    def get_all_compounds(self) -> List[Dict]:
        """Get all compounds as a list"""
        return list(self.compounds.values())
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        return {
            'total_compounds': len(self.compounds),
            'compounds_with_stilbar': len(self.stilbar_to_hash),
            'compounds_without_stilbar': len(self.compounds) - len(self.stilbar_to_hash)
        }

def main():
    """Test the hash-based system"""
    manager = HashCompoundManager()
    
    print("\n📊 Database Stats:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n🔍 Sample compounds:")
    compounds = manager.get_all_compounds()[:5]
    for comp in compounds:
        print(f"  Hash: {comp['hash']} | StilBAR: {comp['stilbar']} | Name: {comp['name'][:30]}...")
    
    # Test lookup by StilBAR
    test_stilbar = "H–77–H"
    compound = manager.get_compound_by_stilbar(test_stilbar)
    if compound:
        print(f"\n🔍 Found compound by StilBAR '{test_stilbar}':")
        print(f"  Hash: {compound['hash']}")
        print(f"  Name: {compound['name']}")
        print(f"  SMILES: {compound['smiles'][:50]}...")

if __name__ == "__main__":
    main()