# PDF SDK - Signature-Preserving PDF Field Editor

A comprehensive toolkit for editing PDF form fields while preserving digital signature validity. This SDK provides multiple approaches to handle different field types and signature preservation requirements.

## Features

- **Signature Preservation**: Maintains digital signature validity through incremental PDF updates
- **Multiple Field Types**: Handles text fields, checkboxes, radio buttons, and more
- **Incremental Updates**: Uses PDF spec-compliant incremental saves
- **Field Type Strategies**: Different approaches for different field types based on signature impact
- **Comprehensive Testing**: Built-in test suite to validate signature preservation

## Quick Start

### Basic Usage

```python
from pdf_sdk import save_pdf_with_signature_preservation

# Update PDF fields while preserving signatures
field_data = {
    "text_field_1": "New text value",
    "checkbox_1": True,
    "radio_button_1": "Option A"
}

result_path = save_pdf_with_signature_preservation("input.pdf", field_data)
print(f"Updated PDF saved to: {result_path}")
```

### Advanced Usage

```python
from pdf_sdk import SignaturePreservingPDFEditor

# Use the editor class for more control
with SignaturePreservingPDFEditor("input.pdf") as editor:
    # Analyze the PDF structure
    fields = editor.get_field_info()
    print(f"Found {len(fields)} form fields")
    
    # Update fields individually
    editor.update_field("field_name", "new_value")
    
    # Save with incremental update
    output_path = editor.save_incremental()
```

## Field Type Handling

The SDK uses different strategies for different field types based on their impact on signature validity:

### Text Fields ✅
- **Status**: Generally safe to update
- **Method**: Direct value update with incremental save
- **Signature Impact**: Low risk

### Checkboxes ⚠️
- **Status**: Requires special handling
- **Method**: Boolean value conversion with appearance preservation
- **Signature Impact**: Medium risk

### Radio Buttons ⚠️
- **Status**: Most sensitive to signature corruption
- **Method**: Minimal appearance stream modification
- **Signature Impact**: High risk

### Signature Fields 🔒
- **Status**: Always skipped
- **Method**: No modification
- **Signature Impact**: Critical - never modified

## Testing Framework

The SDK includes a comprehensive testing framework to validate signature preservation:

### Run Field Type Tests

```bash
cd pdfdebug
python test_field_types.py
```

This will test each field type separately to isolate signature corruption issues.

### Run Signature Preservation Tests

```bash
cd pdfdebug
python test_signature_preservation.py
```

This uses the new SDK to test signature preservation with different field types.

### Run Comprehensive Test Suite

```bash
cd pdfdebug
python run_all_signature_tests.py
```

This runs all available methods and compares their signature preservation capabilities.

## Installation Requirements

```bash
pip install PyMuPDF
```

## File Structure

```
pdfy/
├── pdf-sdk.py                    # Main SDK with signature preservation
├── low_level_pdf_editor.py       # Low-level PDF manipulation
└── README.md                     # This file

pdfdebug/
├── test_field_types.py           # Field type isolation tests
├── test_signature_preservation.py # SDK signature tests
├── run_all_signature_tests.py    # Comprehensive test suite
├── pdf_service_simple.py         # Original implementation
└── frontend_data_*.json          # Test data files
```

## API Reference

### SignaturePreservingPDFEditor

Main class for signature-preserving PDF editing.

#### Methods

- `__init__(pdf_path: str)`: Initialize with PDF file path
- `update_field(field_name: str, new_value: Any) -> bool`: Update single field
- `update_fields(field_data: Dict[str, Any]) -> Dict[str, bool]`: Update multiple fields
- `save_incremental() -> str`: Save with incremental update
- `get_field_info() -> List[Dict[str, Any]]`: Get field information

### Convenience Functions

- `save_pdf_with_signature_preservation(pdf_path, field_data)`: One-line field update
- `analyze_pdf_fields(pdf_path)`: Analyze PDF field structure

## Best Practices

1. **Always Test Signature Validity**: Use Adobe Acrobat to verify signatures after updates
2. **Use Incremental Saves**: Never use full saves on signed PDFs
3. **Field Type Awareness**: Understand the signature impact of different field types
4. **Create Backups**: Always backup original PDFs before modification
5. **Validate Results**: Use the built-in validation methods

## Troubleshooting

### Signature Corruption Issues

If signatures are being corrupted:

1. **Identify Problematic Fields**: Use `test_field_types.py` to isolate issues
2. **Try Low-Level Editor**: Use `low_level_pdf_editor.py` for maximum preservation
3. **Check Field Types**: Radio buttons and checkboxes are most problematic
4. **Validate PDF Structure**: Ensure the PDF isn't already corrupted

### Common Issues

- **PyMuPDF Import Error**: Install with `pip install PyMuPDF`
- **Field Not Found**: Check field names with `get_field_info()`
- **Permission Errors**: Ensure PDF is not password-protected or read-only
- **Signature Validation**: Use Adobe Acrobat, not PDF viewers

## Contributing

When contributing to this SDK:

1. Add tests for new field types or preservation methods
2. Validate signature preservation with real signed PDFs
3. Document any new field type behaviors
4. Update the test suite with new scenarios

## License

This SDK is designed for signature preservation research and development. Test thoroughly with your specific PDF documents and signature requirements. 