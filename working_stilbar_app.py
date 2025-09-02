"""
Working StilBAR to SMILES Converter - Streamlit Application
Fixed version with proper SMILES generation for complex structures
"""
import streamlit as st
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
from fixed_smiles_generator import FixedSMILESGenerator
from hash_compound_manager import HashCompoundManager

# Try to import RDKit, fallback gracefully if not available
try:
    from rdkit import Chem
    from rdkit.Chem import Draw, Descriptors, rdMolDescriptors
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    st.warning("⚠️ RDKit not available. Some features will be limited.")

def main():
    st.set_page_config(
        page_title="StilBAR to SMILES Converter",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🧬 StilBAR to SMILES Converter")
    st.markdown("Convert STILbenoid BARcode notation to SMILES strings with molecular analysis")
    
    # Initialize hash manager first 
    if 'hash_manager' not in st.session_state:
        st.session_state.hash_manager = HashCompoundManager()
    
    # Initialize generator to use the SAME hash manager
    if 'generator' not in st.session_state:
        st.session_state.generator = FixedSMILESGenerator(hash_manager=st.session_state.hash_manager)
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["StilBAR Converter", "Known Compounds", "Add New Compound", "Delete Compounds", "Batch Processing", "About"]
    )
    
    if page == "StilBAR Converter":
        converter_page()
    elif page == "Known Compounds":
        known_compounds_page()
    elif page == "Add New Compound":
        add_compound_page()
    elif page == "Delete Compounds":
        delete_compounds_page()
    elif page == "Batch Processing":
        batch_processing_page()
    else:
        about_page()

def converter_page():
    """Main converter interface"""
    st.header("StilBAR to SMILES Conversion")
    
    # Input section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Input StilBAR Code")
        
        # Example suggestions
        st.markdown("**Examples to try:**")
        example_buttons = st.columns(3)
        
        with example_buttons[0]:
            if st.button("H-77-H"):
                st.session_state.stilbar_input = "H-77-H"
        
        with example_buttons[1]:
            if st.button("T|–04r.15r–|H"):
                st.session_state.stilbar_input = "T|–04r.15r–|H"
        
        with example_buttons[2]:
            if st.button("H"):
                st.session_state.stilbar_input = "H"
        
        # Text input
        stilbar_code = st.text_input(
            "Enter StilBAR code:",
            value=st.session_state.get('stilbar_input', ''),
            placeholder="e.g., H-77-H, T|–04r.15r–|H, H|=4S8.5S7.74S=|5RhH",
            help="Enter a StilBAR code to convert to SMILES"
        )
        
        if st.button("Convert to SMILES", type="primary"):
            if stilbar_code.strip():
                process_stilbar_code(stilbar_code.strip(), col2)
            else:
                st.error("Please enter a StilBAR code")
    
    with col2:
        st.subheader("Results")
        # Display results if they exist
        if 'last_result' in st.session_state:
            display_results(st.session_state.last_result)

def process_stilbar_code(stilbar_code: str, result_column):
    """Process StilBAR code and display results"""
    generator = st.session_state.generator
    
    with st.spinner(f"Converting {stilbar_code} to SMILES..."):
        smiles, metadata = generator.generate_smiles(stilbar_code)
        
        result = {
            'stilbar_code': stilbar_code,
            'smiles': smiles,
            'metadata': metadata
        }
        
        # Store in session state with input tracking
        st.session_state.last_result = result
        st.session_state.last_input = stilbar_code

def display_results(result: Dict):
    """Display conversion results"""
    stilbar_code = result['stilbar_code']
    smiles = result['smiles']
    metadata = result['metadata']
    
    if smiles:
        # Display compound name if available
        compound_name = metadata.get('compound_name', 'Unknown')
        compound_number = metadata.get('compound_number', 'N/A')
        
        if compound_name != 'Unknown' and compound_number != 'N/A':
            st.success(f"✅ Conversion successful!")
            st.info(f"🧬 **Compound {compound_number}**: {compound_name}")
        else:
            st.success(f"✅ Conversion successful!")
        
        # SMILES output
        st.markdown("**SMILES String:**")
        st.code(smiles, language='text')
        
        # Copy button with unique key
        import time
        import hashlib
        # Create unique key using hash of stilbar code and timestamp
        unique_id = hashlib.md5(f"{stilbar_code}_{time.time()}".encode()).hexdigest()[:8]
        copy_key = f"copy_smiles_{unique_id}"
        if st.button("📋 Copy SMILES", key=copy_key):
            st.write("SMILES copied to clipboard!")
            st.code(smiles)  # Simple display since we can't actually copy to clipboard
        
        # Metadata
        with st.expander("Conversion Details"):
            st.write(f"**Method:** {metadata.get('method', 'unknown')}")
            st.write(f"**Confidence:** {metadata.get('confidence', 0.0):.2f}")
            st.write(f"**Type:** {metadata.get('type', 'unknown')}")
            
            if 'linkage_info' in metadata:
                st.write(f"**Linkage:** {metadata['linkage_info']}")
            
            if 'note' in metadata:
                if metadata.get('type') == 'partial_match':
                    st.warning(f"**Note:** {metadata['note']}")
                else:
                    st.info(f"**Note:** {metadata['note']}")
        
        # Molecular analysis (if RDKit is available)
        if RDKIT_AVAILABLE and smiles:
            analyze_molecule(smiles, stilbar_code)
        else:
            st.info("Install RDKit to see molecular structure and properties")
            
    else:
        st.error(f"❌ Conversion failed")
        if 'error' in metadata:
            st.error(f"Error: {metadata['error']}")

def analyze_molecule(smiles: str, compound_name: str):
    """Analyze molecule properties using RDKit"""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            st.warning("⚠️ Invalid SMILES structure - cannot analyze")
            return
        
        # 2D Structure
        st.markdown("**2D Structure:**")
        try:
            img = Draw.MolToImage(mol, size=(400, 300))
            st.image(img, caption=f"Structure of {compound_name}")
        except Exception as e:
            st.warning(f"Could not generate 2D structure: {e}")
        
        # Molecular properties
        st.markdown("**Molecular Properties:**")
        
        properties = {
            "Molecular Weight": f"{Descriptors.MolWt(mol):.2f} g/mol",
            "LogP": f"{Descriptors.MolLogP(mol):.2f}",
            "H-Bond Donors": Descriptors.NumHDonors(mol),
            "H-Bond Acceptors": Descriptors.NumHAcceptors(mol),
            "Rotatable Bonds": Descriptors.NumRotatableBonds(mol),
            "TPSA": f"{Descriptors.TPSA(mol):.2f} Ų",
            "Heavy Atoms": Descriptors.HeavyAtomCount(mol)
        }
        
        prop_col1, prop_col2 = st.columns(2)
        
        with prop_col1:
            for prop, value in list(properties.items())[:4]:
                st.metric(prop, value)
        
        with prop_col2:
            for prop, value in list(properties.items())[4:]:
                st.metric(prop, value)
        
        # Drug-likeness assessment
        st.markdown("**Drug-likeness Assessment:**")
        lipinski_violations = 0
        lipinski_rules = []
        
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
        
        if mw > 500:
            lipinski_violations += 1
            lipinski_rules.append("❌ Molecular Weight > 500")
        else:
            lipinski_rules.append("✅ Molecular Weight ≤ 500")
        
        if logp > 5:
            lipinski_violations += 1
            lipinski_rules.append("❌ LogP > 5")
        else:
            lipinski_rules.append("✅ LogP ≤ 5")
        
        if hbd > 5:
            lipinski_violations += 1
            lipinski_rules.append("❌ H-bond Donors > 5")
        else:
            lipinski_rules.append("✅ H-bond Donors ≤ 5")
        
        if hba > 10:
            lipinski_violations += 1
            lipinski_rules.append("❌ H-bond Acceptors > 10")
        else:
            lipinski_rules.append("✅ H-bond Acceptors ≤ 10")
        
        for rule in lipinski_rules:
            st.write(rule)
        
        if lipinski_violations <= 1:
            st.success(f"✅ Lipinski Rule of Five: PASS ({lipinski_violations} violations)")
        else:
            st.warning(f"⚠️ Lipinski Rule of Five: FAIL ({lipinski_violations} violations)")
            
    except Exception as e:
        st.error(f"Error analyzing molecule: {e}")

def known_compounds_page():
    """Display known compounds from the database using hash-based system"""
    st.header("Known StilBAR Compounds")
    
    hash_manager = st.session_state.hash_manager
    
    # Get all compounds from hash manager
    all_compounds = hash_manager.get_all_compounds()
    
    st.markdown(f"**Database contains {len(all_compounds)} validated compounds:**")
    
    # Create a dataframe for display with sequential numbers (but keep hash internally)
    compounds_data = []
    for index, compound in enumerate(all_compounds, 1):  # Start from 1 for user display
        hash_id = compound['hash']
        compound_name = compound['name']
        stilbar = compound['stilbar']
        smiles = compound['smiles']
        
        mol_weight = "N/A"
        if RDKIT_AVAILABLE:
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol:
                    mol_weight = f"{Descriptors.MolWt(mol):.2f}"
            except:
                pass
        
        compounds_data.append({
            "ID": index,  # Sequential number for user display
            "Hash": hash_id,  # Keep hash for internal operations
            "Compound Name": compound_name,
            "StilBAR Code": stilbar,
            "SMILES": smiles[:50] + "..." if len(smiles) > 50 else smiles,
            "Full_SMILES": smiles,  # Keep full SMILES for analysis
            "Molecular Weight": mol_weight
        })
    
    df = pd.DataFrame(compounds_data)
    
    # Display table with single selection (hide Hash column from users)
    display_df = df.drop(['Hash', 'Full_SMILES'], axis=1)  # Hide hash and full SMILES
    selected_indices = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    ).selection.rows
    
    # Show compound details when selected
    if 'selected_indices' in locals() and selected_indices:
        selected_idx = selected_indices[0]
        selected_compound = df.iloc[selected_idx]
        
        st.subheader(f"Selected: {selected_compound['StilBAR Code']}")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**StilBAR Code:**")
            st.code(selected_compound['StilBAR Code'])
            
            st.markdown("**SMILES:**")
            st.code(selected_compound['Full_SMILES'])
        
        with col2:
            if RDKIT_AVAILABLE and selected_compound['Full_SMILES']:
                analyze_molecule(selected_compound['Full_SMILES'], selected_compound['StilBAR Code'])
    

def delete_selected_compounds(indices_to_delete: list):
    """Delete selected compounds from the database using hash-based system"""
    st.write(f"🔍 delete_selected_compounds called with indices: {indices_to_delete}")
    
    if not indices_to_delete:
        st.warning("No compounds selected for deletion")
        return
    
    # Get the current compounds data from hash manager
    hash_manager = st.session_state.hash_manager
    all_compounds = hash_manager.get_all_compounds()
    
    st.write(f"🔍 Total compounds available: {len(all_compounds)}")
    
    # Get compounds to delete by index
    compounds_to_delete = []
    for i in indices_to_delete:
        if i < len(all_compounds):
            compound = all_compounds[i]
            compounds_to_delete.append({
                "Hash": compound['hash'],
                "Compound Name": compound['name'],
                "StilBAR Code": compound['stilbar'],
                "Full_SMILES": compound['smiles']
            })
    
    st.write(f"🔍 Compounds to delete: {len(compounds_to_delete)}")
    for i, comp in enumerate(compounds_to_delete, 1):
        st.write(f"  - {i}: {comp['Compound Name']} (Hash: {comp['Hash'][:8]})")
    
    if not compounds_to_delete:
        st.error("Invalid selection indices")
        return
    
    # Show confirmation dialog
    st.subheader("⚠️ Confirm Deletion")
    st.error("**You are about to delete the following compounds:**")
    for i, compound in enumerate(compounds_to_delete, 1):
        st.write(f"• **{i}** - {compound['Compound Name']} (`{compound['StilBAR Code']}`)")
    
    st.warning("This action cannot be undone!")
    
    # Use form for more reliable submission
    with st.form("delete_confirmation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            confirm_delete = st.form_submit_button("✅ Confirm Delete", type="primary")
        
        with col2:
            cancel_delete = st.form_submit_button("❌ Cancel")
        
        if confirm_delete:
            st.write("🔍 Confirm Delete clicked via form!")
            with st.spinner("Deleting compounds..."):
                perform_deletion_via_backend(compounds_to_delete)
        
        if cancel_delete:
            st.write("🔍 Cancel clicked via form!")
            st.session_state.compounds_to_delete = []
            st.rerun()

def simple_delete_compounds(selected_compounds: list):
    """Simple, direct deletion function with progress tracking"""
    st.write(f"🔄 Starting deletion of {len(selected_compounds)} compounds...")
    
    # Create progress tracking
    progress_bar = st.progress(0, text="Initializing deletion...")
    status_text = st.empty()
    
    try:
        # Step 1: Get hash manager
        progress_bar.progress(10, text="Getting hash manager...")
        hash_manager = st.session_state.hash_manager
        
        # Step 2: Extract hashes
        progress_bar.progress(20, text="Extracting compound hashes...")
        hashes_to_delete = [comp['hash'] for comp in selected_compounds]
        st.write(f"📝 Deleting hashes: {[h[:8] for h in hashes_to_delete]}")
        
        # Step 3: Show counts before deletion
        before_count = len(hash_manager.get_all_compounds())
        st.write(f"🔍 Compounds before deletion: {before_count}")
        
        # Step 4: Perform deletion
        progress_bar.progress(50, text="Performing deletion...")
        status_text.write("🗑️ Calling hash_manager.delete_compounds()...")
        
        result = hash_manager.delete_compounds(hashes_to_delete)
        
        # Step 5: Show counts after deletion
        after_count = len(hash_manager.get_all_compounds())
        st.write(f"🔍 Compounds after deletion: {after_count}")
        st.write(f"🔍 Expected reduction: {len(hashes_to_delete)}, Actual reduction: {before_count - after_count}")
        
        # Step 4: Check results
        progress_bar.progress(70, text="Checking deletion results...")
        
        if result.get('success'):
            # Step 5: Show results
            progress_bar.progress(80, text="Processing results...")
            st.success(f"✅ Successfully deleted {result.get('deleted_count', 0)} compounds!")
            
            # Show what was deleted
            for deleted in result.get('deleted_compounds', []):
                st.write(f"🗑️ {deleted['name']} ({deleted['stilbar']})")
            
            # Step 6: Reload data
            progress_bar.progress(90, text="Reloading databases...")
            
            # Force reload hash manager from disk (this reloads from CSV)
            hash_manager.load_compounds()
            
            # Since generator uses same hash manager, it's already updated
            # No need to recreate anything - they share the same data source
            
            # Get fresh count after reload
            final_count = hash_manager.get_all_compounds()
            st.write(f"🔍 Final compound count after reload: {len(final_count)}")
            
            # Step 7: Complete
            progress_bar.progress(100, text="Deletion completed successfully!")
            status_text.write("✅ Deletion process completed!")
            
            # Mark completion in session state
            st.session_state.deletion_completed = True
            st.session_state.deletion_success = True
            
            st.balloons()
            
            # Small delay to show completion
            import time
            time.sleep(1)
            
            st.rerun()
        else:
            progress_bar.progress(100, text="Deletion failed!")
            st.error("❌ Deletion failed:")
            for error in result.get('errors', []):
                st.error(f"• {error}")
            
            # Mark failure in session state
            st.session_state.deletion_completed = True
            st.session_state.deletion_success = False
                
    except Exception as e:
        progress_bar.progress(100, text="Error occurred during deletion!")
        st.error(f"💥 Error: {e}")
        import traceback
        st.code(traceback.format_exc())
        
        # Mark error in session state
        st.session_state.deletion_completed = True
        st.session_state.deletion_success = False

def perform_deletion_via_backend(compounds_to_delete: list):
    """Legacy function - redirects to simple delete"""
    simple_delete_compounds(compounds_to_delete)

def perform_deletion(compounds_to_delete: list):
    """Legacy deletion function - kept for reference"""
    st.warning("This function is deprecated - using backend deletion instead")

def add_compound_page():
    """Add new compound to database"""
    st.header("Add New StilBAR Compound")
    
    st.markdown("Enter details for a new compound to add to the database.")
    
    # Form for new compound entry
    with st.form("add_compound_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            compound_name = st.text_input(
                "Compound Name *",
                placeholder="e.g., My_New_Compound_cpd1",
                help="Enter a descriptive name for the compound"
            )
            
            stilbar_code = st.text_input(
                "StilBAR Code *",
                placeholder="e.g., H-77-H or T|–04r.15r–|H",
                help="Enter the StilBAR notation for this compound"
            )
        
        with col2:
            smiles_string = st.text_area(
                "SMILES String *",
                placeholder="e.g., OC1=CC=C(CCC2=C(C3=C(CCC4=CC=C(O)C=C4)C=C(O)C=C3O)C(O)=CC(O)=C2)C=C1",
                help="Enter the SMILES string for this compound. Spaces and newlines will be automatically removed.",
                height=100
            )
            
            notes = st.text_area(
                "Notes (optional)",
                placeholder="Additional information about this compound",
                height=100
            )
        
        submitted = st.form_submit_button("Add Compound", type="primary")
        
        if submitted:
            if compound_name and stilbar_code and smiles_string:
                add_new_compound(compound_name, stilbar_code, smiles_string, notes)
            else:
                st.error("Please fill in all required fields (marked with *)")

def add_new_compound(name: str, stilbar: str, smiles: str, notes: str = ""):
    """Process and add new compound to database"""
    
    # Validate and clean inputs
    cleaned_name = name.strip()
    cleaned_stilbar = stilbar.strip().replace(' ', '').replace('-', '–')  # Normalize
    # Clean SMILES: remove only whitespace characters (spaces, newlines, tabs) but preserve structure
    import re
    # Remove whitespace characters but preserve all structural characters like (), [], @, etc.
    cleaned_smiles = re.sub(r'\s+', '', smiles)  # Remove all whitespace characters
    
    # Show cleaned versions to user for confirmation
    if cleaned_stilbar != stilbar.strip():
        st.info(f"**Normalized StilBAR Code:** `{stilbar.strip()}` → `{cleaned_stilbar}`")
    
    if cleaned_smiles != smiles.strip():
        st.info("**Cleaned SMILES (spaces and newlines removed):**")
        st.code(cleaned_smiles, language='text')
    
    # Basic validation
    validation_errors = []
    
    if not cleaned_name:
        validation_errors.append("Compound name cannot be empty")
    
    if not cleaned_stilbar:
        validation_errors.append("StilBAR code cannot be empty")
    
    if not cleaned_smiles:
        validation_errors.append("SMILES string cannot be empty")
    
    # Validate SMILES format using RDKit if available
    if RDKIT_AVAILABLE and cleaned_smiles:
        try:
            mol = Chem.MolFromSmiles(cleaned_smiles)
            if mol is None:
                validation_errors.append("Invalid SMILES format - cannot create molecule")
        except Exception as e:
            validation_errors.append(f"SMILES validation error: {e}")
    
    # Check for duplicates in current database
    generator = st.session_state.generator
    
    if cleaned_stilbar in generator.barcode_to_smiles:
        validation_errors.append(f"StilBAR code '{cleaned_stilbar}' already exists in database")
    
    # Display validation results
    if validation_errors:
        st.error("Validation failed:")
        for error in validation_errors:
            st.error(f"• {error}")
        return
    
    # If validation passes, add to database
    try:
        # Get next compound number
        existing_numbers = generator.get_all_compound_numbers()
        next_number = max(existing_numbers) + 1 if existing_numbers else 1
        
        # Add to CSV file
        import csv
        csv_file = 'Stilabar_Smiles_Perfect.csv'
        
        # Read existing data
        existing_data = []
        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                existing_data = list(reader)
        except FileNotFoundError:
            # Create with header if file doesn't exist
            existing_data = [['num', 'compound_name', 'barcode', 'smiles']]
        
        # Add new compound
        new_row = [str(next_number), cleaned_name, cleaned_stilbar, cleaned_smiles]
        existing_data.append(new_row)
        
        # Write back to file
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(existing_data)
        
        # Reload the generator's database to include the new compound
        generator.reload_database()
        
        # Success message
        st.success(f"✅ Successfully added compound {next_number}")
        
        # Show compound details
        with st.expander("Added Compound Details", expanded=True):
            st.write(f"**Compound Number:** {next_number}")
            st.write(f"**Name:** {cleaned_name}")
            st.write(f"**StilBAR Code:** {cleaned_stilbar}")
            st.write(f"**SMILES:** {cleaned_smiles}")
            if notes:
                st.write(f"**Notes:** {notes}")
        
        # Show structure if RDKit available
        if RDKIT_AVAILABLE:
            try:
                mol = Chem.MolFromSmiles(cleaned_smiles)
                if mol:
                    st.markdown("**2D Structure:**")
                    img = Draw.MolToImage(mol, size=(400, 300))
                    st.image(img, caption=f"Structure of {cleaned_name}")
            except:
                pass
        
        # Suggest testing the new compound
        st.info(f"💡 You can now test the new compound using StilBAR code: **{cleaned_stilbar}** or compound number: **{next_number}**")
        
    except Exception as e:
        st.error(f"Error adding compound to database: {e}")

def delete_compounds_page():
    """Dedicated page for deleting compounds"""
    st.header("🗑️ Delete Compounds")
    st.markdown("Select compounds to delete from the database. **This action cannot be undone!**")
    
    # Get hash manager and compounds
    hash_manager = st.session_state.hash_manager
    all_compounds = hash_manager.get_all_compounds()
    
    if not all_compounds:
        st.warning("No compounds found in database.")
        return
    
    st.info(f"📊 Total compounds in database: {len(all_compounds)}")
    
    # Search and filter functionality
    st.subheader("🔍 Filter Compounds")
    search_term = st.text_input("Search by name or StilBAR code:")
    
    # Filter compounds based on search
    filtered_compounds = []
    for i, compound in enumerate(all_compounds):
        if not search_term or search_term.lower() in compound['name'].lower() or search_term.lower() in compound['stilbar'].lower():
            filtered_compounds.append((i, compound))
    
    st.write(f"Found {len(filtered_compounds)} compounds (showing all)")
    
    # Show all compounds - no pagination limit
    compounds_to_show = filtered_compounds
    
    # Deletion form  
    with st.form("deletion_form"):
        st.subheader("📋 Select Compounds to Delete")
        st.write(f"Select from {len(compounds_to_show)} compounds:")
        
        selected_for_deletion = []
        
        # Select all option
        if st.checkbox("🔘 Select All Visible", key="select_all_delete"):
            select_all_state = True
        else:
            select_all_state = False
        
        # Individual compound selection
        selected_hashes = []
        for i, (original_index, compound) in enumerate(compounds_to_show):
            is_selected = st.checkbox(
                f"**ID {original_index + 1}** - {compound['name'][:50]}{'...' if len(compound['name']) > 50 else ''} (`{compound['stilbar']}`)",
                value=select_all_state,
                key=f"delete_compound_{original_index}"
            )
            
            if is_selected:
                selected_hashes.append(compound['hash'])
                selected_for_deletion.append({
                    'hash': compound['hash'],
                    'name': compound['name'],
                    'stilbar': compound['stilbar'],
                    'original_index': original_index
                })
        
        # Show selection count
        st.write(f"🔍 Selected {len(selected_for_deletion)} compounds for deletion")
        
        # Deletion button - save to session state when clicked
        delete_submitted = st.form_submit_button(
            f"🗑️ Delete {len(selected_for_deletion)} Selected" if selected_for_deletion else "🗑️ Delete Selected",
            type="primary"
        )
        
        # Save selection to session state when form is submitted
        if delete_submitted:
            st.session_state.pending_deletion = selected_for_deletion
            st.write(f"🔍 Saved {len(selected_for_deletion)} compounds to session state")
    
    # Check for completed deletions and show results
    if hasattr(st.session_state, 'deletion_completed') and st.session_state.deletion_completed:
        if st.session_state.deletion_success:
            st.success("🎉 Deletion completed successfully!")
            
            # Use the existing session state hash manager (already updated)
            current_count = len(hash_manager.get_all_compounds())
            st.info(f"📊 Database now contains {current_count} compounds")
        else:
            st.error("❌ Deletion failed!")
        
        # Clear completion flags
        del st.session_state.deletion_completed
        del st.session_state.deletion_success
    
    # Process deletion using session state (survives rerun)
    elif hasattr(st.session_state, 'pending_deletion') and st.session_state.pending_deletion:
        pending = st.session_state.pending_deletion
        st.write(f"🔄 Processing deletion of {len(pending)} compounds from session state...")
        
        for comp in pending:
            st.write(f"• {comp['name']} (`{comp['stilbar']}`)")
        
        # DON'T clear session state until deletion completes
        # The deletion function will manage this
        
        # Call deletion function
        simple_delete_compounds(pending)
        
        # Clear pending deletion only after function call
        st.session_state.pending_deletion = []

def batch_processing_page():
    """Batch processing interface"""
    st.header("Batch Processing")
    
    st.markdown("Process multiple StilBAR codes at once")
    
    # Input methods
    input_method = st.radio(
        "Input method:",
        ["Text Area", "File Upload"]
    )
    
    stilbar_codes = []
    
    if input_method == "Text Area":
        codes_text = st.text_area(
            "Enter StilBAR codes (one per line):",
            placeholder="H-77-H\nT|–04r.15r–|H\nH\nT",
            height=150
        )
        if codes_text:
            stilbar_codes = [line.strip() for line in codes_text.split('\n') if line.strip()]
    
    else:
        uploaded_file = st.file_uploader(
            "Upload text file with StilBAR codes",
            type=['txt', 'csv']
        )
        if uploaded_file:
            try:
                content = uploaded_file.read().decode('utf-8')
                stilbar_codes = [line.strip() for line in content.split('\n') if line.strip()]
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    if stilbar_codes:
        st.write(f"Found {len(stilbar_codes)} StilBAR codes")
        
        if st.button("Process All", type="primary"):
            process_batch(stilbar_codes)

def process_batch(stilbar_codes: List[str]):
    """Process multiple StilBAR codes"""
    generator = st.session_state.generator
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, code in enumerate(stilbar_codes):
        status_text.text(f"Processing {i+1}/{len(stilbar_codes)}: {code}")
        
        smiles, metadata = generator.generate_smiles(code)
        
        results.append({
            'StilBAR Code': code,
            'SMILES': smiles if smiles else 'FAILED',
            'Confidence': metadata.get('confidence', 0.0),
            'Method': metadata.get('method', 'unknown'),
            'Status': 'SUCCESS' if smiles else 'FAILED'
        })
        
        progress_bar.progress((i + 1) / len(stilbar_codes))
    
    status_text.text("Processing complete!")
    
    # Display results
    df = pd.DataFrame(results)
    st.subheader("Results")
    st.dataframe(df, use_container_width=True)
    
    # Summary
    success_count = len([r for r in results if r['Status'] == 'SUCCESS'])
    st.metric("Success Rate", f"{success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    # Download option
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name="stilbar_batch_results.csv",
        mime="text/csv"
    )

def about_page():
    """About page with system information"""
    st.header("About StilBAR Converter")
    
    st.markdown("""
    ## What is StilBAR?
    
    STILbenoid BARcodes (StilBAR) is a systematic nomenclature for encoding stilbenoid molecular structures into readable formats.
    
    ### Key Components:
    
    **Monomers:**
    - T = trans-Resveratrol
    - H = diH-Resveratrol  
    - C = cis-Resveratrol
    - P = diH-Pterostilbene
    - M = 0-Methoxy-diH-Resveratrol
    - X = 8-Methoxy-diH-Resveratrol
    
    **Linkage Types:**
    - F = Furanoid motif (C-C and C-O-C bonds)
    - K = All C-C bonds (Karbon)
    - E = Only C-O-C bonds (Ether) 
    - FK = Furanoid with additional C-C bond
    
    ### Examples:
    - `H-77-H` → Complex stilbenoid dimer
    - `T|–04r.15r–|H` → trans-δ-Viniferin
    - `H` → Simple diH-Resveratrol monomer
    """)
    
    st.subheader("System Status")
    
    # System information
    status_data = {
        "RDKit Available": "✅ Yes" if RDKIT_AVAILABLE else "❌ No",
        "Total Compounds": st.session_state.generator.get_database_size(),
        "Available Barcodes": len(st.session_state.generator.barcode_to_smiles)
    }
    
    for key, value in status_data.items():
        st.metric(key, value)
    
    if not RDKIT_AVAILABLE:
        st.warning("""
        ⚠️ **RDKit not installed**
        
        To enable full functionality including molecular visualization and property calculations, install RDKit:
        
        ```bash
        conda install -c conda-forge rdkit
        # or
        pip install rdkit
        ```
        """)

if __name__ == "__main__":
    main()