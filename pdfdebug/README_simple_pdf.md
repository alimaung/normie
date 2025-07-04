# Simple PDF Service - Signature Preserving Implementation

This directory contains a simplified PDF service implementation that preserves digital signatures when updating form fields.

## Files

- `pdf_service_simple.py` - Simplified PDF service with minimal field processing
- `test_simple_update.py` - Test script to update a PDF with frontend data
- `frontend_data.json` - Sample form data (provided by user)
- `README_simple_pdf.md` - This documentation

## Key Differences from Production System

### Working Approach (This Implementation)
- **Minimal field processing**: Direct field value assignment without complex translation
- **Simple type handling**: Basic string/boolean conversion only
- **Pure incremental save**: Uses `doc.saveIncr()` without additional processing
- **Signature preservation**: Completely skips signature fields

### Production System Issues
- **Complex field processing**: German display value translation
- **Multiple field type handling**: Complex value conversion logic
- **Additional PDF operations**: NeedAppearances flag, appearance stream removal
- **Signature corruption**: Complex processing breaks signature integrity

## How to Use

### 1. Prepare Files
Ensure you have:
- `pdf.pdf` - Your PDF file with form fields and signatures
- `frontend_data.json` - JSON file with field data in format: `{"field_id": "value"}`

### 2. Run the Test
```bash
cd pdfdebug
python test_simple_update.py
```

### 3. Check Results
- The script will create a backup of your original PDF
- Update the PDF with the provided data
- Show verification of key fields
- Preserve digital signatures

## Expected Behavior

### Signature Preservation
- Signatures should show "validity unknown" instead of "invalid"
- Signature timestamps should remain unchanged
- Signed fields should not be modified

### Field Updates
- Text fields: Updated with string values
- Checkboxes: Converted from string to boolean
- Radio buttons: Updated with string values
- Signature fields: Completely skipped

## Technical Details

### Core Function
```python
def save_pdf_changes_simple(template_path, frontend_data):
    """
    Simple PDF field update that preserves signatures.
    Uses minimal approach from working test script.
    """
```

### Key Features
1. **Signature Detection**: `if widget.field_type_string == 'Signature':`
2. **Minimal Processing**: Direct field value assignment
3. **Incremental Save**: `doc.saveIncr()` preserves existing structure
4. **Error Handling**: Graceful handling of field update errors

### Comparison with Production
| Feature | Simple Implementation | Production System |
|---------|----------------------|-------------------|
| Field Translation | None | German ↔ PDF values |
| Value Processing | Minimal | Complex conversion |
| Signature Handling | Skip completely | Process with filtering |
| PDF Operations | saveIncr() only | Multiple operations |
| Compatibility | Signature preserving | Signature corrupting |

## Testing Results

The simple implementation should:
- ✅ Preserve signature validity ("unknown" status)
- ✅ Update form fields correctly
- ✅ Maintain PDF structure integrity
- ✅ Work with Adobe Acrobat and other viewers

## Next Steps

If this implementation works:
1. Compare with production system behavior
2. Identify specific operations that corrupt signatures
3. Implement minimal necessary processing in production
4. Remove unnecessary PDF operations that break signatures

## Troubleshooting

### Common Issues
1. **PyMuPDF not installed**: `pip install PyMuPDF`
2. **File not found**: Ensure `pdf.pdf` and `frontend_data.json` are in directory
3. **Permission errors**: Check file write permissions

### Debug Output
The script provides detailed output:
- Field extraction results
- Update progress for each field
- Verification of key fields
- Error messages for failed operations 