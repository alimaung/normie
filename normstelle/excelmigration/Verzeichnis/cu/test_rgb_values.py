#!/usr/bin/env python3
"""
Test script to find actual RGB values from Win32 COM for Excel colors
This will help us determine the correct color mappings.
"""

def old_rgb_to_hex(rgb_value):
    """Original working function from excel_extraction_old.py"""
    if rgb_value is None:
        return None
    
    try:
        # Convert to integer if it's a float
        rgb_int = int(rgb_value)
        
        # Extract RGB components from the integer
        red = rgb_int & 255
        green = (rgb_int >> 8) & 255
        blue = (rgb_int >> 16) & 255
        
        return f"#{red:02X}{green:02X}{blue:02X}"
    
    except (ValueError, TypeError) as e:
        print(f"Warning: Could not convert RGB value {rgb_value} to hex: {e}")
        return None

def test_known_excel_colors():
    """Test known Excel indexed colors to see what RGB integers they produce"""
    print("Testing Excel indexed color RGB values...")
    print("=" * 50)
    
    # These are the typical Excel indexed colors for approval status
    # Let's see what RGB integers Win32 COM actually returns for them
    test_cases = [
        # Expected indexed colors based on Excel color palette
        (13434828, "Light green (might be approved)"),
        (10079487, "Should be #FFCC99 (not approved)"),
        (10079164, "Different orange"),
        (16777215, "White (processing)"),
        
        # CRITICAL: Test the RGB that should produce #CCFF99
        (10092492, "SHOULD BE #CCFF99 (approved for first order)"),
        
        # Let's also test some other common Excel colors
        (65535, "Yellow"),
        (255, "Red"),
        (65280, "Green"),
        (16711680, "Blue"),
    ]
    
    print("RGB Integer -> Hex Color -> Status")
    print("-" * 50)
    
    for rgb_int, description in test_cases:
        hex_color = old_rgb_to_hex(rgb_int)
        print(f"{rgb_int:>10} -> {hex_color} -> {description}")
    
    print("\n" + "=" * 50)
    print("Compare these results with what you see in the actual Excel file!")
    print("The correct mappings should be used in continuous_updater.py")

if __name__ == "__main__":
    test_known_excel_colors()
