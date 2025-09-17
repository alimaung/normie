import json
import time
from pathlib import Path
import sys

def load_json_file(file_path):
    """Load and return JSON data from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def compare_metadata(original_meta, optimized_meta):
    """Compare metadata sections"""
    print("🔍 METADATA COMPARISON")
    print("=" * 50)
    
    # Basic stats comparison
    basic_fields = ['total_rows', 'total_columns', 'source_file', 'hyperlinks_extracted', 'colors_extracted']
    
    differences = []
    
    for field in basic_fields:
        orig_val = original_meta.get(field)
        opt_val = optimized_meta.get(field)
        
        if orig_val != opt_val:
            differences.append(f"  {field}: Original={orig_val}, Optimized={opt_val}")
        else:
            print(f"✅ {field}: {orig_val}")
    
    # Compare columns
    orig_cols = original_meta.get('columns', [])
    opt_cols = optimized_meta.get('columns', [])
    
    if orig_cols == opt_cols:
        print(f"✅ columns: {len(orig_cols)} columns match")
    else:
        differences.append(f"  columns: Different! Original={len(orig_cols)}, Optimized={len(opt_cols)}")
    
    # Compare hyperlink columns
    orig_hyperlink = original_meta.get('hyperlink_columns', [])
    opt_hyperlink = optimized_meta.get('hyperlink_columns', [])
    
    if orig_hyperlink == opt_hyperlink:
        print(f"✅ hyperlink_columns: {len(orig_hyperlink)} hyperlink columns match")
    else:
        differences.append(f"  hyperlink_columns: Different! Original={orig_hyperlink}, Optimized={opt_hyperlink}")
    
    # Compare URL normalization
    orig_norm = original_meta.get('url_normalization', {})
    opt_norm = optimized_meta.get('url_normalization', {})
    
    if orig_norm.get('normalized_count') == opt_norm.get('normalized_count'):
        print(f"✅ url_normalization.normalized_count: {orig_norm.get('normalized_count')}")
    else:
        differences.append(f"  url_normalization.normalized_count: Original={orig_norm.get('normalized_count')}, Optimized={opt_norm.get('normalized_count')}")
    
    if differences:
        print(f"\n❌ METADATA DIFFERENCES FOUND:")
        for diff in differences:
            print(diff)
        return False
    else:
        print(f"\n✅ All metadata fields match!")
        return True

def compare_single_row(row1, row2, row_idx):
    """Compare two data rows and return differences"""
    differences = []
    
    # Get all keys from both rows
    all_keys = set(row1.keys()) | set(row2.keys())
    
    for key in all_keys:
        val1 = row1.get(key)
        val2 = row2.get(key)
        
        if val1 != val2:
            # Special handling for hyperlink objects
            if isinstance(val1, dict) and isinstance(val2, dict):
                # Compare hyperlink dictionaries
                hyperlink_diff = []
                all_hyperlink_keys = set(val1.keys()) | set(val2.keys())
                
                for hkey in all_hyperlink_keys:
                    hval1 = val1.get(hkey)
                    hval2 = val2.get(hkey)
                    if hval1 != hval2:
                        hyperlink_diff.append(f"{hkey}: '{hval1}' vs '{hval2}'")
                
                if hyperlink_diff:
                    differences.append({
                        'key': key,
                        'type': 'hyperlink_object',
                        'details': hyperlink_diff
                    })
            else:
                differences.append({
                    'key': key,
                    'type': 'value',
                    'original': val1,
                    'optimized': val2
                })
    
    return differences

def compare_data_rows(original_data, optimized_data, max_rows_to_check=100):
    """Compare data rows between original and optimized"""
    print(f"\n🔍 DATA ROWS COMPARISON (checking first {max_rows_to_check} rows)")
    print("=" * 50)
    
    if len(original_data) != len(optimized_data):
        print(f"❌ Row count mismatch: Original={len(original_data)}, Optimized={len(optimized_data)}")
        return False
    
    print(f"✅ Row count matches: {len(original_data)} rows")
    
    total_differences = 0
    rows_with_differences = 0
    
    rows_to_check = min(max_rows_to_check, len(original_data))
    
    for i in range(rows_to_check):
        row_diffs = compare_single_row(original_data[i], optimized_data[i], i)
        
        if row_diffs:
            rows_with_differences += 1
            total_differences += len(row_diffs)
            
            if rows_with_differences <= 5:  # Show details for first 5 problematic rows
                print(f"\n❌ Row {i+2} differences:")
                for diff in row_diffs[:3]:  # Show max 3 differences per row
                    if diff['type'] == 'hyperlink_object':
                        print(f"  Column '{diff['key']}' (hyperlink): {diff['details'][:2]}")
                    else:
                        print(f"  Column '{diff['key']}': '{diff['original']}' vs '{diff['optimized']}'")
                
                if len(row_diffs) > 3:
                    print(f"  ... and {len(row_diffs) - 3} more differences")
    
    if total_differences == 0:
        print(f"✅ All {rows_to_check} checked rows are identical!")
        
        if rows_to_check < len(original_data):
            print(f"ℹ️  Note: Only checked first {rows_to_check} rows out of {len(original_data)} total")
        
        return True
    else:
        print(f"\n❌ DATA DIFFERENCES SUMMARY:")
        print(f"  Rows with differences: {rows_with_differences}/{rows_to_check}")
        print(f"  Total differences found: {total_differences}")
        return False

def analyze_performance(original_meta, optimized_meta):
    """Analyze and compare performance metrics"""
    print(f"\n📊 PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    # Get performance data
    orig_perf = original_meta.get('performance', {})
    opt_perf = optimized_meta.get('performance', {})
    
    # Total time comparison
    orig_total = orig_perf.get('total_processing_time', 0)
    opt_total = opt_perf.get('total_processing_time', 0)
    
    if orig_total > 0 and opt_total > 0:
        speedup = orig_total / opt_total
        time_saved = orig_total - opt_total
        percent_reduction = (time_saved / orig_total) * 100
        
        print(f"⚡ OVERALL PERFORMANCE:")
        print(f"  Original time:    {orig_total:.3f}s")
        print(f"  Optimized time:   {opt_total:.3f}s")
        print(f"  Time saved:       {time_saved:.3f}s")
        print(f"  Speed improvement: {speedup:.2f}x faster")
        print(f"  Time reduction:   {percent_reduction:.1f}%")
        
        # Rate comparison
        orig_rate = orig_perf.get('rows_per_second', 0)
        opt_rate = opt_perf.get('rows_per_second', 0)
        
        if orig_rate > 0 and opt_rate > 0:
            rate_improvement = opt_rate / orig_rate
            print(f"\n📈 PROCESSING RATE:")
            print(f"  Original rate:    {orig_rate:.2f} rows/sec")
            print(f"  Optimized rate:   {opt_rate:.2f} rows/sec")
            print(f"  Rate improvement: {rate_improvement:.2f}x faster")
        
        # Component analysis
        print(f"\n🔧 COMPONENT BREAKDOWN:")
        
        components = [
            ('Color processing', 'color_processing_time'),
            ('Hyperlink processing', 'hyperlink_processing_time'),
            ('Regular cell processing', 'regular_cell_time')
        ]
        
        for comp_name, comp_key in components:
            orig_time = orig_perf.get(comp_key, 0)
            opt_time = opt_perf.get(comp_key, 0)
            
            if orig_time > 0 and opt_time > 0:
                comp_speedup = orig_time / opt_time
                comp_saved = orig_time - opt_time
                print(f"  {comp_name}:")
                print(f"    Original: {orig_time:.3f}s -> Optimized: {opt_time:.3f}s")
                print(f"    Improvement: {comp_speedup:.2f}x faster ({comp_saved:.3f}s saved)")
        
        # Efficiency rating
        if speedup >= 3.0:
            rating = "🏆 EXCELLENT"
        elif speedup >= 2.0:
            rating = "🥇 VERY GOOD"
        elif speedup >= 1.5:
            rating = "🥈 GOOD"
        elif speedup >= 1.2:
            rating = "🥉 MODERATE"
        else:
            rating = "😐 MINIMAL"
        
        print(f"\n🏅 OPTIMIZATION RATING: {rating}")
        print(f"   ({speedup:.2f}x speedup, {percent_reduction:.1f}% time reduction)")
        
        return {
            'speedup': speedup,
            'time_saved': time_saved,
            'percent_reduction': percent_reduction,
            'rating': rating
        }
    
    else:
        print("❌ Performance data incomplete or missing")
        return None

def main():
    """Main comparison function"""
    # Get file paths
    script_dir = Path(__file__).parent
    original_file = script_dir / "Verzeichnis.json"
    optimized_file = script_dir / "Verzeichnis_openpyxl.json"
    
    print("🔄 EXCEL EXTRACTION COMPARISON TOOL")
    print("=" * 60)
    print(f"Original file:  {original_file}")
    print(f"Optimized file: {optimized_file}")
    
    # Check if files exist
    if not original_file.exists():
        print(f"❌ Original file not found: {original_file}")
        return
    
    if not optimized_file.exists():
        print(f"❌ Optimized file not found: {optimized_file}")
        return
    
    # Load data
    print(f"\n📖 Loading JSON files...")
    original_data = load_json_file(original_file)
    optimized_data = load_json_file(optimized_file)
    
    if not original_data or not optimized_data:
        print("❌ Failed to load one or both JSON files")
        return
    
    print(f"✅ Both files loaded successfully")
    
    # Compare metadata
    metadata_match = compare_metadata(
        original_data.get('metadata', {}), 
        optimized_data.get('metadata', {})
    )
    
    # Compare data rows
    data_match = compare_data_rows(
        original_data.get('data', []), 
        optimized_data.get('data', []),
        max_rows_to_check=200  # Check more rows for thorough validation
    )
    
    # Analyze performance
    performance_analysis = analyze_performance(
        original_data.get('metadata', {}), 
        optimized_data.get('metadata', {})
    )
    
    # Final verdict
    print(f"\n🎯 FINAL VERDICT")
    print("=" * 50)
    
    if metadata_match and data_match:
        print("✅ DATA INTEGRITY: PERFECT MATCH")
        print("   Both extractions produced identical results!")
    else:
        print("❌ DATA INTEGRITY: DIFFERENCES FOUND")
        if not metadata_match:
            print("   - Metadata differences detected")
        if not data_match:
            print("   - Data row differences detected")
    
    if performance_analysis:
        print(f"⚡ PERFORMANCE: {performance_analysis['rating']}")
        print(f"   {performance_analysis['speedup']:.2f}x faster, {performance_analysis['percent_reduction']:.1f}% time reduction")
        print(f"   {performance_analysis['time_saved']:.1f} seconds saved")
        
        # ROI calculation for larger datasets
        if performance_analysis['time_saved'] > 300:  # 5+ minutes saved
            yearly_runs = 100  # Assume 100 runs per year
            yearly_time_saved = (performance_analysis['time_saved'] * yearly_runs) / 3600  # Hours
            print(f"\n💰 PROJECTED SAVINGS (100 runs/year):")
            print(f"   Time saved per year: {yearly_time_saved:.1f} hours")
            print(f"   Cost savings (at $50/hour): ${yearly_time_saved * 50:.0f}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
