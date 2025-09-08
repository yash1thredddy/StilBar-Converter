#!/usr/bin/env python3
"""
Clean and format the Stilabar_Smiles.csv file properly
Remove empty rows and fix formatting issues
"""

import csv
import re

def clean_csv_file():
    """Clean the CSV file and create a proper formatted version"""
    
    clean_data = []
    current_compound = {}
    
    print("🧹 Cleaning CSV file...")
    
    with open('Stilabar_Smiles.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        
        for row_num, row in enumerate(reader, 2):  # Start from row 2
            # Skip completely empty rows
            if not any(cell.strip() for cell in row if cell):
                continue
                
            # Ensure we have at least 4 columns
            while len(row) < 4:
                row.append('')
            
            num_str = row[0].strip() if row[0] else ''
            name = row[1].strip() if row[1] else ''
            barcode = row[2].strip() if row[2] else ''
            smiles = row[3].strip() if row[3] else ''
            
            # If we have a compound number, this starts a new compound
            if num_str and num_str.isdigit():
                # Save previous compound if it exists
                if current_compound and current_compound.get('smiles'):
                    clean_data.append(current_compound)
                
                # Start new compound
                current_compound = {
                    'num': int(num_str),
                    'name': name,
                    'barcode': barcode,
                    'smiles': smiles
                }
            
            # If we have a barcode but no number, add it to current compound
            elif barcode and not num_str and current_compound:
                if not current_compound.get('barcode'):
                    current_compound['barcode'] = barcode
            
            # If we have SMILES but no number, add it to current compound
            elif smiles and not num_str and current_compound:
                if not current_compound.get('smiles'):
                    current_compound['smiles'] = smiles
    
    # Don't forget the last compound
    if current_compound and current_compound.get('smiles'):
        clean_data.append(current_compound)
    
    # Sort by compound number
    clean_data.sort(key=lambda x: x['num'])
    
    # Write clean CSV
    with open('Stilabar_Smiles_Clean.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['num', 'compound_name', 'barcode', 'smiles'])
        
        for compound in clean_data:
            writer.writerow([
                compound['num'],
                compound['name'],
                compound['barcode'],
                compound['smiles']
            ])
    
    print(f"✅ Cleaned CSV created: Stilabar_Smiles_Clean.csv")
    print(f"📊 Found {len(clean_data)} valid compounds")
    
    # Validate the clean data
    compounds_with_barcodes = sum(1 for c in clean_data if c['barcode'])
    compounds_with_smiles = sum(1 for c in clean_data if c['smiles'])
    
    print(f"📋 Compounds with barcodes: {compounds_with_barcodes}")
    print(f"🧬 Compounds with SMILES: {compounds_with_smiles}")
    
    # Check for missing data
    missing_data = []
    for compound in clean_data:
        if not compound['smiles']:
            missing_data.append(f"Compound {compound['num']}: Missing SMILES")
        if not compound['name']:
            missing_data.append(f"Compound {compound['num']}: Missing name")
    
    if missing_data:
        print("⚠️ Issues found:")
        for issue in missing_data[:10]:  # Show first 10
            print(f"  - {issue}")
    else:
        print("✅ All compounds have required data!")
    
    return len(clean_data)

if __name__ == "__main__":
    count = clean_csv_file()
    print(f"\n🎉 CSV cleaning complete! {count} compounds processed.")