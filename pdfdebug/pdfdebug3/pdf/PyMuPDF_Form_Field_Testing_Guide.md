# PyMuPDF Form Field Testing Guide

## 🎯 Overview

This document outlines our comprehensive findings and solutions for working with PDF form fields using PyMuPDF, specifically focusing on radio buttons, checkboxes, and multi-option form controls.

## 🚨 Key Discovery: The Critical Issue

### The Problem We Solved
Initially, we encountered a major issue where **radio button values weren't being set correctly**. The widgets would appear to accept new values in Python, but when the PDF was saved and reopened, the radio buttons remained in their original state.

### Root Cause
The issue was caused by **improper handling of radio button groups** in PyMuPDF. Simply setting `widget.field_value = "/0"` or `widget.field_value = "/1"` was not sufficient.

### The Solution
We discovered the correct approach from PyMuPDF GitHub discussions and documentation:

1. **Use `widget.on_state()` method** to get the proper "on" value for each radio button
2. **Set radio buttons using `widget.field_value = widget.on_state()`** for selection
3. **Set other radio buttons to `False`** to deselect them
4. **Avoid storing widget references** to prevent "weakly-referenced object" errors

## 📋 Field Types & Solutions

### 1. Radio Button Fields (2-option)

**Example: Field "5" - Neubedarf/Bedarfsänderung**

```python
# ✅ CORRECT APPROACH
def handle_radio_button_field(doc, field_name, target_value):
    # Find all widgets for the field
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name == field_name:
                widget_on_state = widget.on_state()
                target_on_state = target_value.lstrip("/")  # Remove "/" prefix
                
                if str(widget_on_state) == target_on_state:
                    # Select this radio button
                    widget.field_value = widget.on_state()
                else:
                    # Deselect other radio buttons
                    widget.field_value = False
                
                widget.update()
```

**Values:**
- `/0` → Neubedarf (first option)
- `/1` → Bedarfsänderung (second option)

### 2. Multi-option Radio Button Fields (3+ options)

**Example: Field "26" - Umweltschutz Prüfung**

```python
# ✅ SAME APPROACH - works for any number of radio options
def handle_multi_radio_field(doc, field_name, target_value):
    target_on_state = target_value.lstrip("/")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name == field_name:
                widget_on_state = widget.on_state()
                
                if str(widget_on_state) == target_on_state:
                    widget.field_value = widget.on_state()
                else:
                    widget.field_value = False
                
                widget.update()
```

**Values:**
- `/0` → Genehmigt
- `/1` → Nicht genehmigt
- `/2` → Genehmigt mit Einschränkung

### 3. Checkbox Fields

**Example: Fields "18a", "18b", "18c", "18d"**

```python
# ✅ CORRECT APPROACH for checkboxes
def handle_checkbox_field(doc, field_name, checked):
    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            if widget.field_name == field_name:
                if checked:
                    # Check the checkbox
                    try:
                        widget.field_value = widget.on_state()
                    except:
                        widget.field_value = True
                else:
                    # Uncheck the checkbox
                    widget.field_value = False
                
                widget.update()
                break
```

**Values:**
- `True` or `widget.on_state()` → Checked
- `False` → Unchecked

## ❌ Common Mistakes to Avoid

### 1. Storing Widget References
```python
# ❌ DON'T DO THIS - causes "weakly-referenced object" errors
widgets = []
for widget in page.widgets():
    widgets.append(widget)  # This will cause issues later
```

### 2. Direct String Assignment for Radio Buttons
```python
# ❌ DON'T DO THIS - doesn't work reliably
widget.field_value = "/0"  # This often fails
widget.field_value = "1"   # This also fails
```

### 3. Using Integer Values
```python
# ❌ DON'T DO THIS - incorrect for radio buttons
widget.field_value = 0  # Wrong approach
widget.field_value = 1  # Wrong approach
```

## 🔧 Best Practices

### 1. Always Use Fresh Widget References
```python
# ✅ GOOD - get widgets fresh each time
for page_num in range(len(doc)):
    page = doc[page_num]
    for widget in page.widgets():
        # Work with widget immediately, don't store reference
```

### 2. Use on_state() Method
```python
# ✅ GOOD - use the proper PyMuPDF method
on_state = widget.on_state()
widget.field_value = on_state  # For selection
```

### 3. Handle Exceptions Gracefully
```python
# ✅ GOOD - always wrap in try/except
try:
    widget.field_value = widget.on_state()
    widget.update()
except Exception as e:
    print(f"Error setting widget: {e}")
```

## 🧪 Testing Results

Our comprehensive test script (`test_comprehensive_fields.py`) successfully generates:

### Field 5 (Radio Buttons)
- ✅ `test_field_5_neubedarf.pdf` - Shows "/0" value
- ✅ `test_field_5_bedarfsaenderung.pdf` - Shows "/1" value

### Checkboxes 18a-18d
- ✅ `test_checkbox_18a_checked.pdf` / `test_checkbox_18a_unchecked.pdf`
- ✅ `test_checkbox_18b_checked.pdf` / `test_checkbox_18b_unchecked.pdf`
- ✅ `test_checkbox_18c_checked.pdf` / `test_checkbox_18c_unchecked.pdf`
- ✅ `test_checkbox_18d_checked.pdf` / `test_checkbox_18d_unchecked.pdf`

### Field 26 (Multi-option Radio)
- ✅ `test_field_26_genehmigt.pdf` - Shows "/0" value
- ✅ `test_field_26_nicht_genehmigt.pdf` - Shows "/1" value
- ✅ `test_field_26_mit_einschraenkung.pdf` - Shows "/2" value

## 📚 Key PyMuPDF Documentation References

From PyMuPDF GitHub Issue #2333:

> **For radio buttons:**
> - To **select** a radio button: assign `True` or `field.on_state()` to the field value
> - To **deselect** a radio button: assign `False` to the field value
> - PyMuPDF doesn't support automatic group management, but it does support setting the correct value in the owning button group

### Important Methods:
- `widget.on_state()` - Returns the "on" value for the widget
- `widget.field_value = widget.on_state()` - Selects a radio button/checkbox
- `widget.field_value = False` - Deselects a radio button/checkbox
- `widget.update()` - Commits the changes to the widget

## 🎉 Success Factors

1. **Understanding PyMuPDF's radio button group behavior**
2. **Using the correct `on_state()` method**
3. **Properly managing widget references**
4. **Setting all radio buttons in a group (select one, deselect others)**
5. **Comprehensive testing with verification**

## 🔄 Workflow Summary

1. **Find all widgets** for the target field name
2. **Get the `on_state()`** for each widget to understand available values
3. **Match the target value** to the appropriate widget's `on_state()`
4. **Set the correct widget** to `widget.on_state()` (selected)
5. **Set other widgets** to `False` (deselected)
6. **Call `widget.update()`** on each modified widget
7. **Save the document** with `doc.saveIncr()`
8. **Verify the results** by reopening and checking field values

## 🚀 Final Notes

This approach works reliably across different PDF forms and PyMuPDF versions. The key insight was understanding that PyMuPDF requires explicit management of radio button groups, and that the `on_state()` method provides the correct values for form field selection.

**Generated on:** $(date)  
**PyMuPDF Version:** Latest (as of testing)  
**Test Files:** Available in same directory as this documentation 