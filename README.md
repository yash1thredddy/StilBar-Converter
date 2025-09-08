# StilBAR to SMILES Converter (Cloud Edition)

A modern, cloud-native web application for converting StilBAR (STILbenoid BARcodes) notation to SMILES strings with real-time database integration and molecular analysis.

## 🚀 Features

### Core Functionality
- **🧬 StilBAR to SMILES Conversion**: Real-time conversion with multiple lookup methods
- **🔍 Advanced Search**: Search by StilBAR code, compound name, or database hash ID
- **📊 Molecular Analysis**: RDKit-powered property calculation and visualization
- **☁️ Cloud Database**: Persistent PostgreSQL storage via Supabase
- **📦 Batch Processing**: CSV upload with validation, error handling, and duplicate detection

### Enhanced Features
- **🔄 Real-time Sync**: All changes instantly synchronized across users
- **✅ Smart Validation**: Comprehensive SMILES and data validation
- **📈 Interactive Visualizations**: 2D molecular structures and property plots  
- **🎯 Intelligent Filtering**: Filter by molecular weight, Lipinski properties
- **📱 Responsive Design**: Works seamlessly on desktop and mobile

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Supabase (PostgreSQL + REST API)
- **Chemistry**: RDKit (molecular informatics)
- **Deployment**: Streamlit Cloud ready

## 📋 Prerequisites

- Python 3.8 or higher
- Supabase account (free tier available)
- System packages for RDKit (handled automatically on Streamlit Cloud)

## 🔧 Installation & Setup

### 1. Clone Repository
```bash
git clone <your-repository-url>
cd "stilBar/Part 2"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Supabase Setup
1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Run the database setup script:
```bash
python setup_supabase.py
```
3. Configure environment variables:

#### Local Development (.env file):
```env
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-anon-key
```

#### Streamlit Cloud (.streamlit/secrets.toml):
```toml
[supabase]
url = "your-project-url"
key = "your-anon-key"
```

### 4. Test Connection
```bash
python test_supabase_connection.py
```

### 5. Run Application
```bash
streamlit run stilbar_app_supabase.py
```

## 🎯 Usage Guide

### Main Converter
1. **Single Conversion**: Enter StilBAR code in the input field
2. **Results**: View SMILES string, molecular structure, and properties
3. **Analysis**: Explore molecular descriptors and drug-likeness metrics

### Compound Browser  
1. **Search**: Find compounds by name, StilBAR code, or molecular weight range
2. **Selection**: Click on compounds to view detailed information
3. **Actions**: Test conversions, find similar compounds, or delete entries

### Batch Upload
1. **CSV Format**: Use columns `compound_name`, `stilbar_code`, `smiles`
2. **Upload**: Drag and drop or select CSV file
3. **Validation**: Review categorized results (Valid/Warnings/Duplicates/Errors)
4. **Confirmation**: Upload only valid compounds, skip duplicates and errors

### Add New Compounds
1. **Single Entry**: Use the form to add individual compounds
2. **Validation**: All three fields (name, StilBAR, SMILES) are required
3. **Verification**: System checks for duplicates and validates SMILES format

## 📊 Database Schema

### Compounds Table
| Column | Type | Description |
|--------|------|-------------|
| `hash` | VARCHAR(16) | Unique identifier (MD5 hash) |
| `name` | TEXT | Compound name |
| `stilbar` | TEXT | StilBAR code |
| `smiles` | TEXT | SMILES string |
| `created_at` | TIMESTAMP | Creation timestamp |

### Features
- **Hash-based IDs**: Unique 16-character identifiers
- **Full-text Search**: Searchable compound names and StilBAR codes
- **Data Integrity**: Unique constraints and validation
- **Audit Trail**: Creation timestamps for all entries

## 🧪 StilBAR Notation Reference

### Basic Components
- **T**: trans-Resveratrol
- **H**: diH-Resveratrol (dihydro-resveratrol)  
- **C**: cis-Resveratrol
- **P**: diH-Pterostilbene

### Linkage Types
- **–** (en-dash): C-C single bond
- **|**: C-O-C ether bond
- **=**: C-C double bond

### Examples
```
H–77–H                    -> Simple dimer
T|–04r.15r–|H            -> trans-δ-Viniferin  
H|=4S8.5S7.74S=|5RhH     -> Complex structure with stereochemistry
```

## 🔍 Lookup Methods

The application uses multiple lookup strategies:

1. **StilBAR Code**: Direct match against database
2. **Compound Number**: Sequential numbering (1, 2, 3...)
3. **Hash ID**: Direct hash-based lookup
4. **Normalization**: Automatic dash conversion (- to –)

## 📁 File Structure

```
├── stilbar_app_supabase.py           # Main Streamlit application
├── supabase_smiles_generator.py      # SMILES generation logic
├── supabase_compound_manager.py      # Database management layer
├── supabase_adapter.py               # Low-level Supabase operations
├── setup_supabase.py                 # Database initialization
├── test_supabase_connection.py       # Connection testing
├── requirements.txt                  # Python dependencies
├── packages.txt                      # System packages for Streamlit Cloud
├── .streamlit/secrets.toml           # Streamlit Cloud configuration
└── .env                              # Local environment variables
```

## 🚀 Deployment

### Streamlit Cloud
1. Connect your GitHub repository
2. Add Supabase credentials to secrets
3. Deploy automatically - system packages handled by `packages.txt`

### Environment Variables Required
```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key"
```

## ✅ Testing

### Connection Test
```bash
python test_supabase_connection.py
```

### Test Coverage
- ✅ Database connection
- ✅ Compound CRUD operations  
- ✅ Search functionality
- ✅ SMILES validation
- ✅ Batch upload processing

## 🔧 Development

### Architecture
- **Clean Separation**: UI, business logic, and data access separated
- **Type Hints**: Full type annotation for better development experience  
- **Error Handling**: Comprehensive error management and user feedback
- **Performance**: Optimized queries and caching strategies

### Adding Features
1. **Database Changes**: Update `supabase_adapter.py`
2. **Business Logic**: Modify `supabase_compound_manager.py`
3. **UI Changes**: Update `stilbar_app_supabase.py`
4. **Testing**: Add tests to `test_supabase_connection.py`

## 🎨 Key Features Highlight

### Smart Batch Processing
- **Duplicate Detection**: Automatically identifies existing compounds
- **Error Categorization**: Separates missing data, duplicates, and validation errors
- **Selective Upload**: Process only valid entries, skip problematic ones
- **Clear Feedback**: Visual tabs showing different categories of results

### Advanced Search & Filtering
- **Multi-method Search**: Name, StilBAR code, or molecular weight range
- **Real-time Results**: Instant filtering as you type
- **Interactive Selection**: Click-to-view compound details
- **Property-based Filtering**: Filter by molecular weight ranges

### Molecular Analysis
- **RDKit Integration**: Professional chemical informatics toolkit
- **Visual Structures**: 2D molecular structure rendering
- **Property Calculation**: Molecular weight, LogP, Lipinski parameters
- **Drug-likeness Assessment**: Rule of Five compliance checking

## 📈 Performance

- **Database**: Optimized PostgreSQL queries via Supabase
- **Search**: Indexed full-text search for fast compound discovery
- **Caching**: Session-based caching for improved response times
- **Scalability**: Cloud-native architecture supports multiple users

## 🆘 Troubleshooting

### Common Issues
1. **Connection Failed**: Check Supabase credentials and URL
2. **RDKit Missing**: System packages will auto-install on Streamlit Cloud
3. **Upload Errors**: Verify CSV format matches expected columns
4. **Slow Performance**: Check internet connection and Supabase status

### Support
- Check connection with `test_supabase_connection.py`
- Review Streamlit Cloud logs for deployment issues  
- Verify Supabase dashboard for database status

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)  
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Contact

For questions, issues, or contributions, please use the project's GitHub issue system.

---

**Version**: 2.0.0 (Supabase Edition)  
**Last Updated**: 2025-09-08  
**Database**: PostgreSQL via Supabase  
**Deployment**: Streamlit Cloud Ready