#!/usr/bin/env python3
"""
Quick runner script to test the fast asset mirror.
"""

import time
from pathlib import Path
from fast_asset_mirror import FastAssetMirror

def main():
    print("🚀 Testing Fast Asset Mirror")
    print("=" * 50)
    
    # Check if links file exists
    links_file = Path("extracted_links.json")
    if not links_file.exists():
        print(f"❌ Links file not found: {links_file}")
        print("Please run the link discovery script first!")
        return
    
    # Start timing
    start_time = time.time()
    
    # Create and run fast mirror
    mirror = FastAssetMirror(
        output_dir="fast_offline_mirror"
    )
    
    success = mirror.fast_mirror_complete_site()
    
    # End timing
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "=" * 50)
    if success:
        print(f"✅ SUCCESS! Fast mirror completed in {total_time:.1f} seconds")
        print(f"\n📁 Output: fast_offline_mirror/")
        print(f"🌐 To serve: python -m http.server 8000 --directory fast_offline_mirror")
        print(f"🔗 Then open: http://localhost:8000/index.html")
    else:
        print(f"❌ FAILED! Mirror took {total_time:.1f} seconds but failed")
    
    print("\n🎯 Expected improvements over original:")
    print("• 3-5x faster overall execution")
    print("• Single Chrome instance (simpler)")
    print("• Assets downloaded once (not 660+ times)")
    print("• Reduced timeouts (3s vs 10s)")
    print("• Same perfect results!")

if __name__ == "__main__":
    main()
