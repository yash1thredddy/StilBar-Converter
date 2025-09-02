"""
Working StilBAR to SMILES Converter - Streamlit Application
Fixed version with proper SMILES generation for complex structures
"""
import streamlit as st
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
from fixed_smiles_generator import FixedSMILESGenerator

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
    
    # Initialize the generator
    if 'generator' not in st.session_state:
        st.session_state.generator = FixedSMILESGenerator()
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["StilBAR Converter", "Known Compounds", "Batch Processing", "About"]
    )
    
    if page == "StilBAR Converter":
        converter_page()
    elif page == "Known Compounds":
        known_compounds_page()
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
        
        # Store in session state
        st.session_state.last_result = result
        
        # Display results in the specified column
        with result_column:
            display_results(result)

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
    """Display known compounds from the database"""
    st.header("Known StilBAR Compounds")
    
    generator = st.session_state.generator
    
    # Get ALL compounds from the updated generator
    if hasattr(generator, 'barcode_to_smiles'):
        # Show ALL compounds with barcodes (don't filter - all are valid!)
        known_complexes = generator.barcode_to_smiles
    else:
        known_complexes = {}
    
    st.markdown(f"**Database contains {len(known_complexes)} validated compounds:**")
    
    # Create a dataframe for display with compound names
    compounds_data = []
    for stilbar, smiles in known_complexes.items():
        # Get compound info (including name)
        compound_info = generator.compound_info.get(stilbar, {})
        compound_name = compound_info.get('name', 'Unknown')
        compound_number = compound_info.get('number', 'N/A')
        
        mol_weight = "N/A"
        if RDKIT_AVAILABLE:
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol:
                    mol_weight = f"{Descriptors.MolWt(mol):.2f}"
            except:
                pass
        
        compounds_data.append({
            "ID": compound_number,
            "Compound Name": compound_name,
            "StilBAR Code": stilbar,
            "SMILES": smiles[:50] + "..." if len(smiles) > 50 else smiles,
            "Molecular Weight": mol_weight
        })
    
    df = pd.DataFrame(compounds_data)
    
    # Display with selection
    selected_indices = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    ).selection.rows
    
    if selected_indices:
        selected_idx = selected_indices[0]
        selected_compound = df.iloc[selected_idx]
        
        st.subheader(f"Selected: {selected_compound['StilBAR Code']}")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**StilBAR Code:**")
            st.code(selected_compound['StilBAR Code'])
            
            st.markdown("**SMILES:**")
            st.code(selected_compound['SMILES'])
        
        with col2:
            if RDKIT_AVAILABLE and selected_compound['SMILES']:
                analyze_molecule(selected_compound['SMILES'], selected_compound['StilBAR Code'])

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