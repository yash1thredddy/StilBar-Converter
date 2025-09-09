"""
Clean StilBAR to SMILES Converter - Supabase Only
Pure cloud-native application with PostgreSQL backend
"""
import streamlit as st
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
from supabase_smiles_generator import SupabaseSMILESGenerator
from security_utils import (
    validate_csv_file_size, secure_display_error, log_security_event,
    validate_stilbar_code, validate_smiles_input, validate_compound_name
)

# Try to import RDKit, fallback gracefully if not available
try:
    from rdkit import Chem
    from rdkit.Chem import Draw, Descriptors, rdMolDescriptors, AllChem
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
    
    # Initialize generator
    if 'generator' not in st.session_state:
        st.session_state.generator = SupabaseSMILESGenerator()
    
    # Check database connection
    if not st.session_state.generator.is_connected():
        st.error("❌ Database not connected! Please check your Supabase configuration.")
        st.info("Make sure SUPABASE_URL and SUPABASE_ANON_KEY are set in your environment or secrets.")
        return
    
    # Show connection status
    #st.success("✅ Connected to Supabase database")
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["StilBAR Converter", "Known Compounds", "Add New Compound", "About"]
    )
    
    if page == "StilBAR Converter":
        converter_page()
    elif page == "Known Compounds":
        known_compounds_page()
    elif page == "Add New Compound":
        add_compound_page()
    else:
        about_page()

def converter_page():
    """Enhanced converter interface with bidirectional conversion and batch processing"""
    st.header("🧬 Bidirectional StilBAR ⇔ SMILES Converter")
    
    # Conversion mode selector
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        conversion_mode = st.selectbox(
            "Conversion Direction:",
            ["StilBAR → SMILES", "SMILES → StilBAR"],
            key="conversion_mode"
        )
    
    with col2:
        batch_mode = st.toggle("Multiple Inputs", value=False, key="batch_mode")
    
    with col3:
        st.write("")  # Spacing
    
    st.divider()
    
    # Handle different modes
    if conversion_mode == "SMILES → StilBAR":
        smiles_to_stilbar_page(batch_mode)
        return
    
    # Original StilBAR to SMILES functionality (enhanced with batch mode)
    if batch_mode:
        batch_stilbar_to_smiles_page()
        return
    
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
        st.success(f"✅ Conversion successful!")
        
        # Display compound name if available
        compound_name = metadata.get('compound_name', 'Unknown')
        if compound_name != 'Unknown':
            st.info(f"🧬 **Compound**: {compound_name}")
        
        # Show StilBAR code for reference
        st.markdown("**StilBAR Code:**")
        st.code(stilbar_code, language='text')
        
        # SMILES output
        st.markdown("**SMILES String:**")
        st.code(smiles, language='text')
        
        # Show hash ID for reference
        if 'hash_id' in metadata:
            st.caption(f"Database ID: `{metadata['hash_id']}`")
        
        # Molecular analysis (if RDKit is available)
        if RDKIT_AVAILABLE and smiles:
            analyze_molecule(smiles, stilbar_code)
        else:
            st.info("Install RDKit to see molecular structure and properties")
            
    else:
        st.error("❌ Conversion failed")
        if 'error' in metadata:
            # Don't expose raw error details to users
            st.error("Please check your input and try again")
            log_security_event("CONVERSION_FAILED", f"StilBAR conversion failed", "INFO")

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
            # Generate optimized 2D coordinates to prevent overlapping
            AllChem.Compute2DCoords(mol)
            
            # Larger image size for better visibility
            img = Draw.MolToImage(mol, size=(600, 450))
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
        log_security_event("MOLECULE_ANALYSIS_ERROR", f"Error analyzing molecule", "INFO")
        st.warning("⚠️ Unable to analyze molecular structure")

def known_compounds_page():
    """Enhanced compound browser with search, filter, and detailed view"""
    st.header("Known StilBAR Compounds Browser")
    
    generator = st.session_state.generator
    all_compounds = generator.compound_manager.get_all_compounds()
    
    # Initialize session state for selected compound
    if 'selected_compound_hash' not in st.session_state:
        st.session_state.selected_compound_hash = None
    
    # Search and filter section
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input(
            "🔍 Search compounds:",
            placeholder="Enter name, StilBAR code, or partial match...",
            help="Search by compound name or StilBAR code"
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sort by:",
            ["Name", "StilBAR Code", "Molecular Weight", "Recent"],
            help="Choose sorting criteria"
        )
    
    with col3:
        if RDKIT_AVAILABLE:
            weight_filter = st.selectbox(
                "MW Filter:",
                ["All", "< 300", "300-500", "> 500"],
                help="Filter by molecular weight"
            )
        else:
            weight_filter = "All"
    
    # Apply search and filters
    if search_term:
        filtered_compounds = generator.search_compounds(search_term)
        st.info(f"🔍 Found {len(filtered_compounds)} compounds matching '{search_term}'")
    else:
        filtered_compounds = all_compounds
    
    # Apply molecular weight filter
    if RDKIT_AVAILABLE and weight_filter != "All":
        filtered_compounds = apply_weight_filter(filtered_compounds, weight_filter)
    
    # Sort compounds
    filtered_compounds = sort_compounds(filtered_compounds, sort_by)
    
    st.markdown(f"**Showing {len(filtered_compounds)} of {len(all_compounds)} total compounds**")
    
    if not filtered_compounds:
        st.warning("No compounds match your search criteria.")
        return
    
    # Layout: Compound list on left, details on right
    col_list, col_details = st.columns([1, 1])
    
    with col_list:
        st.subheader("📋 Compound List")
        display_compound_list(filtered_compounds)
    
    with col_details:
        st.subheader("📊 Compound Details")
        display_selected_compound_details()

def apply_weight_filter(compounds, weight_filter):
    """Apply molecular weight filter to compounds"""
    if not RDKIT_AVAILABLE or weight_filter == "All":
        return compounds
    
    filtered = []
    for compound in compounds:
        try:
            mol = Chem.MolFromSmiles(compound['smiles'])
            if mol:
                mw = Descriptors.MolWt(mol)
                
                if weight_filter == "< 300" and mw < 300:
                    filtered.append(compound)
                elif weight_filter == "300-500" and 300 <= mw <= 500:
                    filtered.append(compound)
                elif weight_filter == "> 500" and mw > 500:
                    filtered.append(compound)
        except:
            continue
    
    return filtered

def sort_compounds(compounds, sort_by):
    """Sort compounds based on criteria"""
    if sort_by == "Name":
        return sorted(compounds, key=lambda x: x['name'].lower())
    elif sort_by == "StilBAR Code":
        return sorted(compounds, key=lambda x: x['stilbar'].lower())
    elif sort_by == "Molecular Weight" and RDKIT_AVAILABLE:
        def get_mw(compound):
            try:
                mol = Chem.MolFromSmiles(compound['smiles'])
                return Descriptors.MolWt(mol) if mol else 0
            except:
                return 0
        return sorted(compounds, key=get_mw)
    else:  # Recent or fallback
        return compounds  # Already in creation order

def display_compound_list(compounds):
    """Display searchable, selectable compound list"""
    
    # Create compound list with key info
    compound_options = []
    compound_lookup = {}
    
    for i, compound in enumerate(compounds):
        # Calculate molecular weight if available
        mw_info = ""
        if RDKIT_AVAILABLE:
            try:
                mol = Chem.MolFromSmiles(compound['smiles'])
                if mol:
                    mw = Descriptors.MolWt(mol)
                    mw_info = f" (MW: {mw:.1f})"
            except:
                pass
        
        # Create display string
        display_name = f"{compound['name'][:40]}{'...' if len(compound['name']) > 40 else ''}"
        stilbar_display = f"{compound['stilbar'][:15]}{'...' if len(compound['stilbar']) > 15 else ''}"
        
        option_text = f"{display_name} | {stilbar_display}{mw_info}"
        compound_options.append(option_text)
        compound_lookup[option_text] = compound
    
    # Show pagination info
    if len(compound_options) > 50:
        st.info(f"📄 Showing first 50 of {len(compound_options)} compounds. Use search to narrow results.")
        compound_options = compound_options[:50]
    
    # Selectable list using radio buttons in a container
    selected_option = None
    
    # Use container with max height for scrolling
    with st.container(height=400):
        for i, option in enumerate(compound_options):
            compound = compound_lookup[option]
            
            # Check if this compound is currently selected
            is_selected = st.session_state.selected_compound_hash == compound['hash']
            
            if st.button(
                option,
                key=f"compound_btn_{i}_{compound['hash'][:8]}",
                help=f"Click to view details for {compound['name']}",
                type="primary" if is_selected else "secondary",
                use_container_width=True
            ):
                # Update selected compound
                st.session_state.selected_compound_hash = compound['hash']
                st.rerun()

def display_selected_compound_details():
    """Display detailed information for selected compound"""
    
    if not st.session_state.selected_compound_hash:
        st.info("👆 Select a compound from the list to view detailed information")
        
        # Show quick stats
        generator = st.session_state.generator
        all_compounds = generator.compound_manager.get_all_compounds()
        
        stats = generator.get_stats()
        
        st.markdown("### 📊 Database Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Compounds", stats['total_compounds'])
        with col2:
            st.metric("With StilBAR", stats['compounds_with_stilbar'])
        with col3:
            st.metric("Without StilBAR", stats['compounds_without_stilbar'])
        
        return
    
    # Get selected compound details
    generator = st.session_state.generator
    compound = generator.compound_manager.get_compound_by_hash(st.session_state.selected_compound_hash)
    
    if not compound:
        st.error("❌ Selected compound not found in database")
        st.session_state.selected_compound_hash = None
        return
    
    # Display compound header
    st.markdown(f"### 🧬 {compound['name']}")
    
    # Basic information
    with st.expander("📝 Basic Information", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**StilBAR Code:**")
            if compound['stilbar']:
                st.code(compound['stilbar'], language='text')
            else:
                st.write("*No StilBAR code*")
            
            st.markdown("**Database Hash:**")
            st.code(compound['hash'], language='text')
        
        with col2:
            st.markdown("**SMILES String:**")
            st.code(compound['smiles'], language='text')
            
    
    # Molecular analysis
    if RDKIT_AVAILABLE and compound['smiles']:
        with st.expander("🔬 Molecular Analysis", expanded=True):
            analyze_molecule(compound['smiles'], compound['stilbar'] or compound['name'])
    
    # Additional actions
    with st.expander("⚙️ Actions"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Test Conversion", key=f"test_{compound['hash'][:8]}"):
                # Test the compound conversion
                test_conversion_result(compound)
        
        with col2:
            if st.button("🧪 Find Similar", key=f"similar_{compound['hash'][:8]}"):
                st.info("🔍 Similarity search feature coming soon!")
        
        with col3:
            if st.button("🗑️ Delete This", key=f"delete_{compound['hash'][:8]}", type="secondary"):
                # Set deletion confirmation state
                st.session_state[f'delete_confirm_{compound["hash"]}'] = True
                st.rerun()
    
    # Handle deletion confirmation
    if st.session_state.get(f'delete_confirm_{compound["hash"]}', False):
        show_deletion_confirmation(compound)

def test_conversion_result(compound):
    """Test compound conversion functionality"""
    generator = st.session_state.generator
    
    if compound['stilbar']:
        st.markdown("**Testing StilBAR → SMILES conversion:**")
        
        with st.spinner(f"Testing conversion of {compound['stilbar']}..."):
            smiles, metadata = generator.generate_smiles(compound['stilbar'])
            
            if smiles == compound['smiles']:
                st.success("✅ Conversion test passed! Generated SMILES matches database.")
                st.json(metadata)
            else:
                st.error("❌ Conversion test failed! Generated SMILES differs from database.")
                st.write("**Expected:**", compound['smiles'])
                st.write("**Generated:**", smiles or "None")
                st.json(metadata)
    else:
        st.warning("⚠️ No StilBAR code available for conversion testing.")

def show_deletion_confirmation(compound):
    """Show deletion confirmation dialog"""
    st.divider()
    st.warning(f"⚠️ **Delete Compound**: {compound['name']}")
    st.write(f"StilBAR: `{compound['stilbar']}`")
    st.write("**This action cannot be undone!**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Confirm Delete", type="primary", key=f"confirm_del_{compound['hash'][:8]}"):
            perform_single_deletion(compound)
    with col2:
        if st.button("↩️ Cancel", key=f"cancel_del_{compound['hash'][:8]}"):
            # Clear deletion confirmation state
            del st.session_state[f'delete_confirm_{compound["hash"]}']
            st.rerun()

def perform_single_deletion(compound):
    """Perform single compound deletion"""
    generator = st.session_state.generator
    
    with st.spinner(f"Deleting {compound['name']}..."):
        result = generator.delete_compounds([compound['hash']])
        
        if result['success']:
            st.success(f"✅ Successfully deleted {compound['name']}")
            # Clear deletion confirmation state
            if f'delete_confirm_{compound["hash"]}' in st.session_state:
                del st.session_state[f'delete_confirm_{compound["hash"]}']
            # Clear selection
            st.session_state.selected_compound_hash = None
            st.rerun()
        else:
            st.error("❌ Failed to delete compound:")
            for error in result['errors']:
                st.error(f"• {error}")

def add_compound_page():
    """Add new compound(s) to database - single or batch upload"""
    st.header("Add New StilBAR Compounds")
    
    # Mode selection
    col1, col2 = st.columns([1, 1])
    with col1:
        add_mode = st.radio(
            "Choose how to add compounds:",
            ["Single Compound", "Batch Upload (CSV)"],
            key="add_mode"
        )
    
    with col2:
        if add_mode == "Batch Upload (CSV)":
            st.info("📁 **Expected CSV format:**\n```\ncompound_name,stilbar_code,smiles,notes\nMy_Compound_1,H-77-H,OC1=CC=C...,Optional notes\nMy_Compound_2,T|–04r.15r–|H,OC(C=C1)...,More notes\n```\n*Note: All three fields (name, stilbar_code, smiles) are required. Only notes is optional.*")
    
    st.divider()
    
    if add_mode == "Single Compound":
        add_single_compound_form()
    else:
        add_batch_compounds_form()

def add_single_compound_form():
    """Form for adding a single compound"""
    st.subheader("Single Compound Entry")
    
    generator = st.session_state.generator
    
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

def add_batch_compounds_form():
    """Form for batch adding compounds via CSV upload"""
    st.subheader("Batch CSV Upload")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload CSV file with compounds",
        type=['csv'],
        help="CSV should have columns: compound_name, stilbar_code, smiles"
    )
    
    if uploaded_file is not None:
        # Validate file size
        file_size = uploaded_file.size if hasattr(uploaded_file, 'size') else len(uploaded_file.getvalue())
        size_valid, size_error = validate_csv_file_size(file_size)
        
        if not size_valid:
            st.error(f"❌ {size_error}")
            log_security_event("FILE_SIZE_EXCEEDED", f"CSV upload size: {file_size} bytes", "WARNING")
            return
        
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Validate CSV format
            validation_result = validate_csv_format(df)
            
            if validation_result['valid']:
                # Process and preview compounds
                processed_compounds = process_csv_compounds(df)
                preview_batch_compounds(processed_compounds, validation_result)
            else:
                st.error("❌ CSV format validation failed:")
                for error in validation_result['errors']:
                    st.error(f"• {error}")
                
                # Show expected format
                st.info("**Expected CSV format:**")
                sample_df = pd.DataFrame([
                    {"compound_name": "Example_Compound_1", "stilbar_code": "H-77-H", "smiles": "OC1=CC=C(CCC2=CC=C(O)C=C2)C=C1"},
                    {"compound_name": "Example_Compound_2", "stilbar_code": "T|–04r.15r–|H", "smiles": "OC(C=C1)=CC=C1[C@H](O2)[C@H](C3=CC(O)=CC(O)=C3)C4=C2C=CC(/C=C/C5=CC(O)=CC(O)=C5)=C4"}
                ])
                st.dataframe(sample_df, use_container_width=True)
                
        except Exception as e:
            log_security_event("CSV_READ_ERROR", f"Error reading CSV file", "WARNING")
            secure_display_error(e, "reading CSV file")
            st.info("Please ensure your CSV file is properly formatted and not corrupted.")

def validate_csv_format(df):
    """Validate CSV format and required columns"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check required columns - all three are mandatory
    required_columns = ['compound_name', 'stilbar_code', 'smiles']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        result['valid'] = False
        result['errors'].append(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Check if DataFrame is empty
    if df.empty:
        result['valid'] = False
        result['errors'].append("CSV file is empty")
        return result
    
    # Show warnings for rows with missing data (will be skipped but processing continues)
    if result['valid']:
        for col in required_columns:
            empty_count = df[col].isna().sum() + (df[col] == '').sum()
            if empty_count > 0:
                result['warnings'].append(f"Found {empty_count} row(s) with missing '{col}' - these will be skipped")
    
    # Additional column checks
    extra_columns = [col for col in df.columns if col not in required_columns + ['notes']]
    if extra_columns:
        result['warnings'].append(f"Extra columns found (will be ignored): {', '.join(extra_columns)}")
    
    return result

def process_csv_compounds(df):
    """Process and clean CSV compounds data"""
    generator = st.session_state.generator
    processed_compounds = []
    
    for index, row in df.iterrows():
        # Clean data
        name = str(row.get('compound_name', '')).strip()
        
        # Handle StilBAR code - must be present and valid
        stilbar = str(row.get('stilbar_code', '')).strip().replace(' ', '').replace('-', '–')
        
        smiles = re.sub(r'\s+', '', str(row.get('smiles', '')))  # Remove all whitespace
        notes = str(row.get('notes', '')).strip()
        
        # Validation status for this compound
        compound_data = {
            'row_number': index + 1,
            'original_name': str(row.get('compound_name', '')),
            'original_stilbar': str(row.get('stilbar_code', '')),
            'original_smiles': str(row.get('smiles', '')),
            'cleaned_name': name,
            'cleaned_stilbar': stilbar,
            'cleaned_smiles': smiles,
            'notes': notes,
            'errors': [],
            'warnings': [],
            'status': 'valid'
        }
        
        # Validation checks - all three fields are required
        if not name:
            compound_data['errors'].append("Empty compound name")
            compound_data['status'] = 'error'
        
        if not stilbar:
            compound_data['errors'].append("Empty StilBAR code")
            compound_data['status'] = 'error'
        
        if not smiles:
            compound_data['errors'].append("Empty SMILES string")
            compound_data['status'] = 'error'
        
        # Check for duplicate in current batch
        existing_names = [comp['cleaned_name'] for comp in processed_compounds]
        existing_stilbars = [comp['cleaned_stilbar'] for comp in processed_compounds]
        
        if name in existing_names:
            compound_data['errors'].append("Duplicate compound name in batch")
            compound_data['status'] = 'error'
        
        if stilbar in existing_stilbars:
            compound_data['errors'].append("Duplicate StilBAR code in batch")
            compound_data['status'] = 'error'
        
        # Check for existing in database - treat as warning (will skip but show)
        if stilbar and compound_data['status'] != 'error':
            existing_compound = generator.compound_manager.get_compound_by_stilbar(stilbar)
            if existing_compound:
                compound_data['warnings'].append(f"Already exists in database: {existing_compound['name']}")
                compound_data['status'] = 'duplicate'  # Special status for duplicates
        
        # Validate SMILES with RDKit if available
        if RDKIT_AVAILABLE and smiles and compound_data['status'] != 'error':
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    compound_data['errors'].append("Invalid SMILES format")
                    compound_data['status'] = 'error'
            except Exception as e:
                compound_data['errors'].append(f"SMILES validation error: {str(e)}")
                compound_data['status'] = 'error'
        
        # Data cleaning warnings
        if compound_data['cleaned_name'] != compound_data['original_name'].strip():
            compound_data['warnings'].append("Compound name was cleaned")
        
        if compound_data['cleaned_stilbar'] != compound_data['original_stilbar'].strip():
            compound_data['warnings'].append("StilBAR code was normalized")
        
        if compound_data['cleaned_smiles'] != compound_data['original_smiles'].strip():
            compound_data['warnings'].append("SMILES was cleaned (whitespace removed)")
        
        processed_compounds.append(compound_data)
    
    return processed_compounds

def preview_batch_compounds(processed_compounds, validation_result):
    """Preview and confirm batch compound addition"""
    
    # Summary statistics
    total_compounds = len(processed_compounds)
    valid_compounds = [comp for comp in processed_compounds if comp['status'] == 'valid']
    warning_compounds = [comp for comp in processed_compounds if comp['status'] == 'warning']
    duplicate_compounds = [comp for comp in processed_compounds if comp['status'] == 'duplicate']
    error_compounds = [comp for comp in processed_compounds if comp['status'] == 'error']
    
    # Compounds that will be processed (valid + warnings, but not duplicates or errors)
    processable_compounds = valid_compounds + warning_compounds
    
    st.subheader("📊 Batch Upload Summary")
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Compounds", total_compounds)
    with col2:
        st.metric("✅ Valid", len(valid_compounds), delta=None)
    with col3:
        st.metric("⚠️ Warnings", len(warning_compounds), delta=None)
    with col4:
        st.metric("🔄 Duplicates", len(duplicate_compounds), delta=None)
    with col5:
        st.metric("❌ Errors", len(error_compounds), delta=None)
    
    # Show validation warnings if any
    if validation_result['warnings']:
        st.warning("⚠️ CSV Format Warnings:")
        for warning in validation_result['warnings']:
            st.write(f"• {warning}")
    
    # Detailed compound preview
    st.subheader("📋 Compound Details")
    
    # Tabs for different status types
    tab1, tab2, tab3, tab4 = st.tabs([
        f"✅ Valid ({len(valid_compounds)})",
        f"⚠️ Warnings ({len(warning_compounds)})",
        f"🔄 Duplicates ({len(duplicate_compounds)})",
        f"❌ Errors ({len(error_compounds)})"
    ])
    
    with tab1:
        if valid_compounds:
            display_compound_preview(valid_compounds, "valid")
        else:
            st.info("No valid compounds found.")
    
    with tab2:
        if warning_compounds:
            display_compound_preview(warning_compounds, "warning")
            st.warning("⚠️ Compounds with warnings can still be added, but please review them carefully.")
        else:
            st.info("No compounds with warnings.")
    
    with tab3:
        if duplicate_compounds:
            display_compound_preview(duplicate_compounds, "duplicate")
            st.info("🔄 These compounds already exist in the database and will be skipped.")
        else:
            st.success("No duplicate compounds!")
    
    with tab4:
        if error_compounds:
            display_compound_preview(error_compounds, "error")
            st.error("❌ Compounds with errors will be skipped. Fix the CSV file and re-upload to include them.")
        else:
            st.success("No compounds with errors!")
    
    # Confirmation and upload
    if processable_compounds:
        st.divider()
        confirm_batch_upload(processable_compounds, duplicate_compounds, error_compounds)
    else:
        st.error("No valid compounds to upload. Please fix the errors and try again.")

def display_compound_preview(compounds, status_type):
    """Display compound preview table"""
    if not compounds:
        return
    
    # Create preview dataframe
    preview_data = []
    for comp in compounds:
        preview_data.append({
            "Row": comp['row_number'],
            "Compound Name": comp['cleaned_name'][:30] + "..." if len(comp['cleaned_name']) > 30 else comp['cleaned_name'],
            "StilBAR Code": comp['cleaned_stilbar'][:20] + "..." if len(comp['cleaned_stilbar']) > 20 else comp['cleaned_stilbar'],
            "SMILES": comp['cleaned_smiles'][:40] + "..." if len(comp['cleaned_smiles']) > 40 else comp['cleaned_smiles'],
            "Issues": "; ".join(comp['errors'] + comp['warnings']) if comp['errors'] + comp['warnings'] else "None"
        })
    
    preview_df = pd.DataFrame(preview_data)
    st.dataframe(preview_df, use_container_width=True, hide_index=True)

def confirm_batch_upload(uploadable_compounds, duplicate_compounds, error_compounds):
    """Confirmation interface for batch upload"""
    st.subheader("🚀 Confirm Batch Upload")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**Ready to upload {len(uploadable_compounds)} compounds:**")
        valid_count = len([comp for comp in uploadable_compounds if comp['status'] == 'valid'])
        warning_count = len([comp for comp in uploadable_compounds if comp['status'] == 'warning'])
        duplicate_count = len(duplicate_compounds)
        error_count = len(error_compounds)
        
        if valid_count > 0:
            st.write(f"• ✅ {valid_count} compounds without issues")
        if warning_count > 0:
            st.write(f"• ⚠️ {warning_count} compounds with warnings (will be uploaded)")
        
        if duplicate_count > 0:
            st.write(f"• 🔄 {duplicate_count} duplicates (will be skipped)")
        if error_count > 0:
            st.write(f"• ❌ {error_count} compounds with errors (will be skipped)")
    
    with col2:
        # Store compounds in session state for upload
        if st.button("✅ Confirm Upload", type="primary", key="confirm_batch_upload"):
            st.session_state.pending_batch_upload = uploadable_compounds
            perform_batch_upload(uploadable_compounds)

def perform_batch_upload(compounds):
    """Perform the actual batch upload with progress tracking"""
    st.subheader("🔄 Uploading Compounds...")
    
    generator = st.session_state.generator
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = {
        'successful': [],
        'failed': [],
        'skipped': []
    }
    
    # Process each compound
    for i, compound in enumerate(compounds):
        progress_bar.progress((i + 1) / len(compounds))
        status_text.text(f"Uploading {i+1}/{len(compounds)}: {compound['cleaned_name'][:50]}...")
        
        try:
            success, result = generator.add_compound(
                compound['cleaned_name'],
                compound['cleaned_stilbar'],
                compound['cleaned_smiles']
            )
            
            if success:
                results['successful'].append({
                    'name': compound['cleaned_name'],
                    'stilbar': compound['cleaned_stilbar'],
                    'hash_id': result
                })
            else:
                results['failed'].append({
                    'name': compound['cleaned_name'],
                    'error': result
                })
                
        except Exception as e:
            results['failed'].append({
                'name': compound['cleaned_name'],
                'error': str(e)
            })
    
    # Display results
    status_text.text("Upload completed!")
    
    st.subheader("📊 Upload Results")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Successful", len(results['successful']))
    with col2:
        st.metric("❌ Failed", len(results['failed']))
    with col3:
        st.metric("⏭️ Skipped", len(results['skipped']))
    
    # Detailed results
    if results['successful']:
        st.success(f"✅ Successfully uploaded {len(results['successful'])} compounds!")
        with st.expander("Show successful uploads"):
            for compound in results['successful']:
                st.write(f"• **{compound['name']}** (`{compound['stilbar']}`) - Hash: `{compound['hash_id']}`")
    
    if results['failed']:
        st.error(f"❌ Failed to upload {len(results['failed'])} compounds:")
        for compound in results['failed']:
            st.error(f"• **{compound['name']}**: {compound['error']}")
    
    # Clear session state
    if 'pending_batch_upload' in st.session_state:
        del st.session_state.pending_batch_upload
    
    if results['successful']:
        st.balloons()
        st.info("💡 New compounds are now available in the database and can be searched immediately!")

def add_new_compound(name: str, stilbar: str, smiles: str, notes: str = ""):
    """Process and add new compound to database"""
    generator = st.session_state.generator
    
    # Input validation using security utils
    name_valid, name_error = validate_compound_name(name)
    if not name_valid:
        st.error(f"❌ {name_error}")
        return
    
    stilbar_valid, stilbar_error = validate_stilbar_code(stilbar)
    if not stilbar_valid:
        st.error(f"❌ {stilbar_error}")
        return
    
    smiles_valid, smiles_error = validate_smiles_input(smiles)
    if not smiles_valid:
        st.error(f"❌ {smiles_error}")
        return
    
    # Validate and clean inputs
    cleaned_name = name.strip()
    cleaned_stilbar = stilbar.strip().replace(' ', '').replace('-', '–')
    # Clean SMILES: remove only whitespace characters
    import re
    cleaned_smiles = re.sub(r'\s+', '', smiles)
    
    # Show cleaned versions to user for confirmation
    if cleaned_stilbar != stilbar.strip():
        st.info(f"**Normalized StilBAR Code:** `{stilbar.strip()}` → `{cleaned_stilbar}`")
    
    if cleaned_smiles != smiles.strip():
        st.info("**Cleaned SMILES (spaces and newlines removed):**")
        st.code(cleaned_smiles, language='text')
    
    # Basic validation - now handled by security utils above, but keep RDKit validation
    validation_errors = []
    
    # Validate SMILES format using RDKit if available
    if RDKIT_AVAILABLE and cleaned_smiles:
        try:
            mol = Chem.MolFromSmiles(cleaned_smiles)
            if mol is None:
                validation_errors.append("Invalid SMILES format - cannot create molecule")
        except Exception as e:
            validation_errors.append(f"SMILES validation error: {str(e)}")
    
    # Check for duplicates
    existing_compound = generator.compound_manager.get_compound_by_stilbar(cleaned_stilbar)
    if existing_compound:
        validation_errors.append(f"StilBAR code '{cleaned_stilbar}' already exists in database (compound: {existing_compound['name']})")
    
    # Display validation results
    if validation_errors:
        st.error("Validation failed:")
        for error in validation_errors:
            st.error(f"• {error}")
        return
    
    # If validation passes, add to database
    try:
        success, result = generator.add_compound(cleaned_name, cleaned_stilbar, cleaned_smiles)
        
        if success:
            st.success(f"✅ Successfully added compound with hash: {result}")
            log_security_event("COMPOUND_ADDED", f"User added compound: {cleaned_name}", "INFO")
            
            # Show compound details
            with st.expander("Added Compound Details", expanded=True):
                st.write(f"**Hash ID:** {result}")
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
                        # Generate optimized 2D coordinates to prevent overlapping
                        AllChem.Compute2DCoords(mol)
                        
                        # Larger image size for better visibility
                        img = Draw.MolToImage(mol, size=(600, 450))
                        st.image(img, caption=f"Structure of {cleaned_name}")
                except:
                    pass
            
            st.info(f"💡 You can now test the new compound using StilBAR code: **{cleaned_stilbar}**")
            
        else:
            st.error(f"❌ Failed to add compound: {result}")
            log_security_event("COMPOUND_ADD_FAILED", f"Failed to add compound: {cleaned_name}", "WARNING")
        
    except Exception as e:
        log_security_event("COMPOUND_ADD_ERROR", f"Error adding compound", "ERROR")
        secure_display_error(e, "adding compound to database")


def batch_stilbar_to_smiles_page():
    """Batch StilBAR to SMILES conversion"""
    st.markdown("**Enter multiple StilBAR codes (one per line):**")
    stilbar_input = st.text_area(
        "StilBAR Codes:",
        placeholder="H–77–H\nH–17–H\nH–11–H\nT|–04r.15r–|H\n...",
        height=150,
        key="batch_stilbar_textarea"
    )
    
    if st.button("🔬 Convert All to SMILES", type="primary", key="batch_convert_all"):
        if stilbar_input:
            process_batch_stilbar_codes(stilbar_input.strip())
        else:
            st.warning("Please enter at least one StilBAR code")

def smiles_to_stilbar_page(batch_mode=False):
    """SMILES to StilBAR conversion (reverse lookup)"""
    
    st.info("💡 **SMILES Cleaning**: Spaces, tabs, and newlines will be automatically removed from input SMILES strings for accurate matching.")
    
    if batch_mode:
        st.markdown("**Enter multiple SMILES strings (one per line):**")
        smiles_input = st.text_area(
            "SMILES Strings:",
            placeholder="OC1=CC=C(CCC2=CC=C(O)C=C2)C=C1\nOC1=CC(O)=CC(CCC2=CC=C(O)C=C2)=C1\n...",
            height=150,
            key="batch_smiles_textarea"
        )
        
        if st.button("🔍 Find All StilBAR Codes", type="primary", key="batch_find_stilbar"):
            if smiles_input:
                process_batch_smiles_strings(smiles_input.strip())
            else:
                st.warning("Please enter at least one SMILES string")
    else:
        st.markdown("**Enter a SMILES string to find its StilBAR code:**")
        smiles_input = st.text_input(
            "SMILES String:", 
            placeholder="e.g., OC1=CC=C(CCC2=CC=C(O)C=C2)C=C1", 
            key="single_smiles_input"
        )
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("🔍 Find StilBAR Code", type="primary", key="find_stilbar"):
                if smiles_input:
                    process_smiles_string(smiles_input.strip(), col2)
                else:
                    st.warning("Please enter a SMILES string")

def process_batch_stilbar_codes(stilbar_input: str):
    """Process multiple StilBAR codes"""
    generator = st.session_state.generator
    stilbar_codes = [code.strip() for code in stilbar_input.split('\n') if code.strip()]
    
    st.subheader(f"🔬 Processing {len(stilbar_codes)} StilBAR codes...")
    
    results = []
    progress_bar = st.progress(0)
    
    for i, code in enumerate(stilbar_codes):
        progress_bar.progress((i + 1) / len(stilbar_codes))
        
        smiles, metadata = generator.generate_smiles(code)
        
        if smiles:
            results.append({
                "StilBAR Code": code,
                "SMILES": smiles,
                "Compound": metadata.get('compound_name', 'Unknown'),
                "Status": "✅ Found"
            })
        else:
            results.append({
                "StilBAR Code": code, 
                "SMILES": "Not found",
                "Compound": "N/A",
                "Status": "❌ Not found"
            })
    
    # Display results
    st.subheader("📊 Batch Results")
    found_count = sum(1 for r in results if "✅" in r["Status"])
    st.info(f"Found: {found_count}/{len(stilbar_codes)} ({found_count/len(stilbar_codes)*100:.1f}%)")
    
    # Show results table
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)

def process_batch_smiles_strings(smiles_input: str):
    """Process multiple SMILES strings to find StilBAR codes"""
    generator = st.session_state.generator
    smiles_strings = [smiles.strip() for smiles in smiles_input.split('\n') if smiles.strip()]
    
    st.subheader(f"🔍 Searching {len(smiles_strings)} SMILES strings...")
    
    results = []
    progress_bar = st.progress(0)
    all_compounds = generator.compound_manager.get_all_compounds()
    
    for i, smiles in enumerate(smiles_strings):
        progress_bar.progress((i + 1) / len(smiles_strings))
        
        # Clean input SMILES
        import re
        original_smiles = smiles.strip()
        clean_smiles = re.sub(r'\s+', '', original_smiles)
        was_cleaned = clean_smiles != original_smiles
        
        # Find matching compound
        found = False
        for compound in all_compounds:
            if compound['smiles'] == clean_smiles:
                status = "✅ Found" + (" (cleaned)" if was_cleaned else "")
                results.append({
                    "SMILES": original_smiles[:50] + "..." if len(original_smiles) > 50 else original_smiles,
                    "StilBAR Code": compound['stilbar'],
                    "Compound": compound['name'],
                    "Status": status
                })
                found = True
                break
        
        if not found:
            status = "❌ Not found" + (" (cleaned)" if was_cleaned else "")
            results.append({
                "SMILES": original_smiles[:50] + "..." if len(original_smiles) > 50 else original_smiles,
                "StilBAR Code": "Not found",
                "Compound": "N/A", 
                "Status": status
            })
    
    # Display results
    st.subheader("📊 Reverse Lookup Results")
    found_count = sum(1 for r in results if "✅" in r["Status"])
    st.info(f"Found: {found_count}/{len(smiles_strings)} ({found_count/len(smiles_strings)*100:.1f}%)")
    
    # Show results table
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)

def process_smiles_string(smiles_input: str, result_column):
    """Process single SMILES string to find StilBAR code"""
    with result_column:
        st.subheader("🔍 Reverse Lookup Results")
        
        generator = st.session_state.generator
        
        # Clean input SMILES
        import re
        clean_smiles = re.sub(r'\s+', '', smiles_input.strip())
        
        # Show cleaning info if needed
        if clean_smiles != smiles_input.strip():
            st.info(f"🧹 Cleaned SMILES: `{clean_smiles}`")
        
        all_compounds = generator.compound_manager.get_all_compounds()
        
        # Find matching compound
        found_compound = None
        for compound in all_compounds:
            if compound['smiles'] == clean_smiles:
                found_compound = compound
                break
        
        if found_compound:
            st.success("✅ Match found!")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("**StilBAR Code:**")
                st.code(found_compound['stilbar'])
                
                st.markdown("**Compound Name:**")
                st.write(found_compound['name'])
                
                st.markdown("**Database Hash:**")
                st.code(found_compound['hash'])
            
            with col2:
                if RDKIT_AVAILABLE:
                    analyze_molecule(clean_smiles, found_compound['stilbar'])
        else:
            st.error("❌ No matching compound found in database")
            st.info("This SMILES string is not present in our StilBAR database.")

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
    
    # Database backend info
    generator = st.session_state.generator
    
    # System information
    status_data = {
        "Database Backend": "🗄️ Supabase PostgreSQL",
        "Database Connected": "✅ Yes" if generator.is_connected() else "❌ No",
        "RDKit Available": "✅ Yes" if RDKIT_AVAILABLE else "❌ No",
        "Total Compounds": len(generator.compound_manager.get_all_compounds()),
        "Available Barcodes": len([comp for comp in generator.compound_manager.get_all_compounds() if comp['stilbar']])
    }
    
    for key, value in status_data.items():
        st.metric(key, value)
    
    # Database statistics
    if generator.is_connected():
        stats = generator.get_stats()
        st.subheader("Database Statistics")
        
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("Total Compounds", stats['total_compounds'])
        with stat_col2:
            st.metric("With StilBAR Codes", stats['compounds_with_stilbar'])
        with stat_col3:
            st.metric("Without StilBAR", stats['compounds_without_stilbar'])
    
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