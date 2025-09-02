# StilBAR to SMILES Converter

A comprehensive tool for converting StilBAR (STILbenoid BARcodes) notation to SMILES strings with molecular visualization and analysis.

## Features

### Core Functionality
- **StilBAR Parsing**: Decode StilBAR notation into molecular components
- **SMILES Generation**: Convert StilBAR codes to SMILES strings
- **2D Visualization**: Display molecular structures using RDKit
- **Property Calculation**: Compute molecular descriptors and drug-likeness
- **Database Integration**: 62+ known stilbenoid compounds from research literature

### Enhanced Features
- **Confidence Scoring**: Reliability assessment for conversions
- **Similarity Search**: Find structurally similar compounds
- **Batch Processing**: Convert multiple compounds at once
- **Validation Tools**: Multiple methods to verify results
- **Database Explorer**: Browse and analyze known compounds

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone or download this repository
2. Install required packages:
```bash
pip install -r requirements.txt
```

### Package Requirements
- **streamlit**: Web interface framework
- **rdkit**: Chemical informatics toolkit
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualizations
- **numpy**: Numerical computations
- **matplotlib**: Plotting library

## Usage

### Basic Streamlit Application
Run the basic application:
```bash
streamlit run stilbar_app.py
```

### Enhanced Application
Run the enhanced version with database integration:
```bash
streamlit run enhanced_stilbar_app.py
```

### Command Line Testing
Run basic tests without RDKit:
```bash
python run_tests.py
```

Run comprehensive test suite (requires RDKit):
```bash
python test_stilbar_converter.py
```

## StilBAR Notation Guide

### Monomers (Basic Units)
- **T**: trans-Resveratrol
- **H**: diH-Resveratrol (dihydro-resveratrol)
- **C**: cis-Resveratrol
- **P**: diH-Pterostilbene
- **M**: 0-Methoxy-diH-Resveratrol
- **X**: 8-Methoxy-diH-Resveratrol

### Linkage Types
- **|**: C-O-C ether bond
- **–** or **-**: C-C single bond
- **=**: C-C double bond
- **≡**: C-C triple bond

### Connection Sites
- Numbers represent carbon atom positions (0-9)
- Stereochemistry indicated by R/S after numbers
- Multiple connections separated by periods

### Substituents
- **m**: methoxy group (-OCH₃)
- **h**: hydroxy group (-OH)
- **i**: isopropoxy group
- Position and stereochemistry specified with numbers and R/S

## Examples

### Simple Monomers
```
T     -> trans-Resveratrol
H     -> diH-Resveratrol
P     -> diH-Pterostilbene
```

### Complex Structures
```
T|–04r.15r–|H              -> trans-δ-Viniferin
H|=4S8.5S7.74S=|5RhH       -> Ampelopsin A
H≡4r7.5r5r.74r≡H           -> Pallidol
T|05S|4SmH                 -> resAgOAcMeOH1h5a
```

## Database

The application includes a comprehensive database of known stilbenoid compounds:

- **62 validated compounds** from research literature
- **SMILES strings** verified against published structures
- **Metadata** including compound names and sources
- **Search functionality** by name or StilBAR code

### Database Sources
- Wolfender et al. publications (various years)
- Peer-reviewed stilbenoid research
- Validated chemical structures

## Application Interface

### Pages Available

1. **StilBAR Converter**: Main conversion tool
   - Input StilBAR codes
   - Generate SMILES strings
   - View 2D structures
   - Calculate molecular properties

2. **Database Explorer**: Browse known compounds
   - Search by name or code
   - Detailed compound analysis
   - Property comparisons

3. **Similarity Search**: Find similar structures
   - Input SMILES or select reference
   - Tanimoto similarity scoring
   - Visual structure comparison

4. **Batch Processing**: Handle multiple compounds
   - File upload or manual input
   - Progress tracking
   - Results export

5. **Validation**: Verify results
   - Database consistency checks
   - Custom validation pairs
   - Reverse lookup testing

## Testing

### Test Coverage
- Basic StilBAR parsing functionality
- SMILES generation validation
- Database consistency checks
- Property calculation verification
- Known compound validation

### Running Tests
Basic tests (no external dependencies):
```bash
python run_tests.py
```

Full test suite (requires RDKit):
```bash
python test_stilbar_converter.py
```

### Test Results
The test suite validates against known compounds and provides:
- Parsing accuracy assessment
- SMILES generation success rates
- Database consistency verification
- Performance benchmarks

## Technical Architecture

### Core Components

1. **StilBARParser**: Decodes notation into components
   - Regex-based pattern matching
   - Component extraction and validation
   - Error handling and reporting

2. **SMILESGenerator**: Converts parsed data to SMILES
   - Database lookup prioritization
   - Component-based construction
   - Validation and verification

3. **MolecularAnalyzer**: Computes properties and visualizations
   - RDKit integration
   - Property calculation
   - 2D structure rendering

4. **Database**: Manages compound information
   - CSV-based storage
   - Search and retrieval
   - Validation utilities

### Performance Characteristics
- **Parsing speed**: ~100-1000 codes/second
- **Database lookup**: O(1) for exact matches
- **SMILES generation**: Database-first approach
- **Memory usage**: Minimal for typical use cases

## Limitations and Future Work

### Current Limitations
- Complex stereochemistry handling
- Limited reaction template library
- Database coverage gaps
- 2D visualization only

### Planned Enhancements
- Machine learning-based SMILES generation
- 3D molecular visualization
- Extended reaction templates
- Bioactivity prediction models
- API endpoints for integration

## Contributing

### Development Setup
1. Fork the repository
2. Install development dependencies
3. Run tests to ensure functionality
4. Submit pull requests with improvements

### Code Style
- Follow PEP 8 guidelines
- Include docstrings for functions
- Add tests for new functionality
- Update documentation as needed

## License

This project is for research and educational purposes. Please cite appropriate sources when using the database or methodology.

## References

- StilBAR nomenclature system documentation
- Wolfender, J.-L. et al. research publications
- RDKit: Open-source cheminformatics toolkit
- Various stilbenoid research papers

## Contact

For questions, issues, or contributions, please use the project's issue tracking system.

---

**Last Updated**: 2025-01-29
**Version**: 1.0.0