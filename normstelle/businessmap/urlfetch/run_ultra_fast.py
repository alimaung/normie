#!/usr/bin/env python3
"""
Runner for ultra-fast mirror with timing comparison.
"""

import time
from pathlib import Path
from ultra_fast_mirror import UltraFastMirror

def main():
    print("⚡ ULTRA FAST MIRROR TEST")
    print("=" * 60)
    
    # Check links file
    links_file = Path("extracted_links.json")
    if not links_file.exists():
        print(f"❌ Links file not found: {links_file}")
        return
    
    # Show optimization summary
    print("🚀 SPEED OPTIMIZATIONS:")
    print("• Headless Chrome (no GUI overhead)")
    print("• 1.5s page timeouts (vs 10s original)")
    print("• JavaScript-based content detection")
    print("• String replacement for asset fixes (vs BeautifulSoup)")
    print("• 10 concurrent asset downloads")
    print("• Zero unnecessary pauses")
    print("• Fast DOM polling (100ms intervals)")
    print("• Disabled images/plugins for speed")
    print()
    
    # Start timing
    start_time = time.time()
    
    # Run ultra-fast mirror
    mirror = UltraFastMirror(output_dir="ultra_fast_mirror")
    success = mirror.ultra_fast_mirror_complete_site()
    
    # End timing
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "=" * 60)
    if success:
        print(f"✅ SUCCESS! Ultra-fast mirror completed in {total_time:.1f} seconds")
        print(f"\n📁 Output: ultra_fast_mirror/")
        print(f"🌐 Serve: python -m http.server 8000 --directory ultra_fast_mirror")
        print(f"🔗 Open: http://localhost:8000/index.html")
        
        # Speed comparison
        print(f"\n⚡ SPEED COMPARISON:")
        print(f"• Original mirror: ~60+ minutes")
        print(f"• Fast mirror: ~15-20 minutes")
        print(f"• Ultra-fast mirror: {total_time/60:.1f} minutes")
        
        if total_time < 900:  # Less than 15 minutes
            improvement = 60 / (total_time/60)
            print(f"• Speed improvement: {improvement:.1f}x faster than original!")
        
    else:
        print(f"❌ FAILED! Ultra-fast mirror failed after {total_time:.1f} seconds")
    
    print(f"\n🎯 Target: Complete 660+ pages in under 10 minutes")
    print(f"🎯 Result: {total_time/60:.1f} minutes")

if __name__ == "__main__":
    main()
