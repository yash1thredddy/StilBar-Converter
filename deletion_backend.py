#!/usr/bin/env python3
"""
Backend deletion script for StilBAR compounds
This runs independently of Streamlit to avoid session state issues
"""
import csv
import sys
import os
import json
from typing import List

def delete_compounds(compound_ids: List[str], csv_file: str = 'Stilabar_Smiles_Perfect.csv') -> dict:
    """
    Delete compounds from CSV file by compound IDs
    Returns a result dictionary with success status and details
    """
    result = {
        'success': False,
        'deleted_count': 0,
        'errors': [],
        'deleted_compounds': [],
        'csv_rows_before': 0,
        'csv_rows_after': 0
    }
    
    try:
        # Ensure we're working with string IDs
        compound_ids_str = {str(cid).strip() for cid in compound_ids}
        
        print(f"🔍 Backend: Attempting to delete compound IDs: {compound_ids_str}")
        
        # Check if CSV file exists
        if not os.path.exists(csv_file):
            result['errors'].append(f"CSV file not found: {csv_file}")
            return result
        
        # Read existing data
        existing_data = []
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            existing_data = list(reader)
        
        result['csv_rows_before'] = len(existing_data)
        print(f"🔍 Backend: CSV has {len(existing_data)} rows (including header)")
        
        if len(existing_data) <= 1:  # Only header or empty
            result['errors'].append("CSV file is empty or contains only header")
            return result
        
        # Show first few rows for debugging
        print("🔍 Backend: First 3 CSV rows:")
        for i, row in enumerate(existing_data[:3]):
            print(f"  Row {i}: {row}")
        
        # Filter out deleted compounds
        filtered_data = [existing_data[0]]  # Keep header
        deleted_count = 0
        
        for i, row in enumerate(existing_data[1:], 1):  # Skip header
            if len(row) >= 1:
                row_id = row[0].strip()
                if row_id not in compound_ids_str:
                    filtered_data.append(row)
                    print(f"🔍 Backend: Keeping row {i}: ID={row_id}")
                else:
                    deleted_count += 1
                    compound_name = row[1] if len(row) > 1 else 'Unknown'
                    result['deleted_compounds'].append({
                        'id': row_id,
                        'name': compound_name,
                        'row': row
                    })
                    print(f"🔍 Backend: DELETING row {i}: ID={row_id}, Name={compound_name}")
            else:
                print(f"🔍 Backend: Skipping empty row {i}")
        
        result['csv_rows_after'] = len(filtered_data)
        result['deleted_count'] = deleted_count
        
        print(f"🔍 Backend: Rows before: {result['csv_rows_before']}, after: {result['csv_rows_after']}")
        print(f"🔍 Backend: Deleted count: {deleted_count}")
        
        if deleted_count == 0:
            result['errors'].append(f"No compounds found with IDs: {compound_ids_str}")
            return result
        
        # Create backup of original file
        backup_file = csv_file + '.backup'
        with open(backup_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(existing_data)
        print(f"🔍 Backend: Created backup: {backup_file}")
        
        # Write filtered data back to file
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(filtered_data)
        
        print(f"🔍 Backend: Updated {csv_file} successfully")
        
        result['success'] = True
        return result
        
    except Exception as e:
        result['errors'].append(f"Exception: {str(e)}")
        print(f"🔍 Backend: ERROR - {e}")
        return result

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python deletion_backend.py <compound_id1> [compound_id2] ...")
        print("Example: python deletion_backend.py 62 15 23")
        return
    
    compound_ids = sys.argv[1:]
    result = delete_compounds(compound_ids)
    
    # Print result as JSON for easy parsing
    print("🔍 Backend: RESULT:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()