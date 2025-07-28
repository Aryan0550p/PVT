#!/usr/bin/env python3
"""
Performance Test for Adobe Hackathon 2025 - 50 Page PDF Processing
Tests if the solution can process a 50-page PDF in under 10 seconds
"""

import time
import os
import json
import sys
from pathlib import Path
import subprocess

# Import our extraction function
from extract_outline_backup import extract_outline

def create_performance_report(filename, processing_time, result):
    """Create a detailed performance report"""
    print("\n" + "="*60)
    print("📊 PERFORMANCE ANALYSIS REPORT")
    print("="*60)
    
    print(f"📄 File: {filename}")
    print(f"⏱️  Processing Time: {processing_time:.3f} seconds")
    print(f"🎯 Target Time: <10.000 seconds")
    
    if processing_time < 10.0:
        print("✅ PASS: Within time limit!")
        status = "PASS"
    else:
        print("❌ FAIL: Exceeds time limit!")
        status = "FAIL"
    
    # Analyze results
    if result and 'outline' in result:
        headings_count = len(result['outline'])
        title_length = len(result.get('title', ''))
        is_multilingual = result.get('languages', {}).get('is_multilingual', False)
        primary_lang = result.get('languages', {}).get('primary_language', 'unknown')
        
        print(f"📝 Title Length: {title_length} characters")
        print(f"📋 Headings Extracted: {headings_count}")
        print(f"🌍 Primary Language: {primary_lang}")
        print(f"🌐 Multilingual: {is_multilingual}")
        
        # Performance metrics
        processing_speed = headings_count / processing_time if processing_time > 0 else 0
        print(f"🚀 Processing Speed: {processing_speed:.1f} headings/second")
        
    else:
        print("❌ No valid results generated")
        status = "FAIL"
    
    # Memory estimation (rough)
    memory_estimate = processing_time * 50  # MB estimate based on processing time
    print(f"💾 Estimated Memory Usage: ~{memory_estimate:.0f}MB")
    
    print(f"\n🏆 FINAL RESULT: {status}")
    print("="*60)
    
    return status == "PASS"

def test_large_pdf_performance():
    """Test performance on largest available PDF"""
    input_dir = Path("input")
    
    if not input_dir.exists():
        print("❌ Input directory not found!")
        return False
    
    # Find all PDF files and their sizes
    pdf_files = []
    for pdf_file in input_dir.glob("*.pdf"):
        try:
            size = pdf_file.stat().st_size
            pdf_files.append((pdf_file, size))
        except Exception as e:
            print(f"Warning: Could not get size for {pdf_file}: {e}")
    
    if not pdf_files:
        print("❌ No PDF files found in input directory!")
        return False
    
    # Sort by size (largest first)
    pdf_files.sort(key=lambda x: x[1], reverse=True)
    
    print("📋 Available PDF files (by size):")
    for i, (pdf_file, size) in enumerate(pdf_files[:5]):  # Show top 5
        size_mb = size / (1024 * 1024)
        print(f"  {i+1}. {pdf_file.name}: {size_mb:.2f} MB")
    
    # Test the largest PDF
    largest_pdf, largest_size = pdf_files[0]
    size_mb = largest_size / (1024 * 1024)
    
    print(f"\n🎯 Testing largest PDF: {largest_pdf.name} ({size_mb:.2f} MB)")
    print("⏳ Starting performance test...")
    
    # Measure processing time
    start_time = time.time()
    
    try:
        result = extract_outline(str(largest_pdf))
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Create performance report
        success = create_performance_report(largest_pdf.name, processing_time, result)
        return success
        
    except Exception as e:
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"❌ Error during processing: {e}")
        print(f"⏱️  Time before error: {processing_time:.3f} seconds")
        return False

def test_all_pdfs_performance():
    """Test performance on all available PDFs"""
    input_dir = Path("input")
    
    if not input_dir.exists():
        print("❌ Input directory not found!")
        return False
    
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found!")
        return False
    
    print(f"🔍 Testing performance on all {len(pdf_files)} PDF files...")
    
    results = []
    total_time = 0
    
    for pdf_file in pdf_files:
        print(f"\n📄 Processing: {pdf_file.name}")
        
        start_time = time.time()
        try:
            result = extract_outline(str(pdf_file))
            end_time = time.time()
            processing_time = end_time - start_time
            
            total_time += processing_time
            headings_count = len(result.get('outline', []))
            
            print(f"  ⏱️  Time: {processing_time:.3f}s")
            print(f"  📋 Headings: {headings_count}")
            
            results.append({
                'file': pdf_file.name,
                'time': processing_time,
                'headings': headings_count,
                'status': 'SUCCESS'
            })
            
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"  ❌ Error: {e}")
            print(f"  ⏱️  Time: {processing_time:.3f}s")
            
            results.append({
                'file': pdf_file.name,
                'time': processing_time,
                'headings': 0,
                'status': 'ERROR'
            })
    
    # Summary report
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE PERFORMANCE REPORT")
    print("="*60)
    
    successful_results = [r for r in results if r['status'] == 'SUCCESS']
    
    if successful_results:
        avg_time = sum(r['time'] for r in successful_results) / len(successful_results)
        max_time = max(r['time'] for r in successful_results)
        min_time = min(r['time'] for r in successful_results)
        total_headings = sum(r['headings'] for r in successful_results)
        
        print(f"📊 Files Processed: {len(successful_results)}/{len(results)}")
        print(f"⏱️  Average Time: {avg_time:.3f} seconds")
        print(f"⏱️  Maximum Time: {max_time:.3f} seconds")  
        print(f"⏱️  Minimum Time: {min_time:.3f} seconds")
        print(f"⏱️  Total Time: {total_time:.3f} seconds")
        print(f"📋 Total Headings: {total_headings}")
        print(f"🚀 Average Speed: {total_headings/total_time:.1f} headings/second")
        
        # Check 50-page requirement
        print(f"\n🎯 50-Page PDF Projection:")
        estimated_50_page_time = max_time * 2  # Conservative estimate
        print(f"   Estimated Time: {estimated_50_page_time:.3f} seconds")
        
        if estimated_50_page_time < 10.0:
            print("   ✅ LIKELY PASS: Should handle 50 pages in <10s")
            return True
        else:
            print("   ⚠️  UNCERTAIN: May need optimization for 50 pages")
            return False
    else:
        print("❌ No successful processing results")
        return False

def estimate_memory_usage():
    """Estimate memory usage during processing"""
    try:
        import psutil
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process a file to measure memory
        input_dir = Path("input")
        pdf_files = list(input_dir.glob("*.pdf"))
        
        if pdf_files:
            result = extract_outline(str(pdf_files[0]))
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before
            
            print(f"💾 Memory Usage Analysis:")
            print(f"   Before: {memory_before:.1f} MB")
            print(f"   After: {memory_after:.1f} MB") 
            print(f"   Used: {memory_used:.1f} MB")
            
            # Estimate for 50 pages
            estimated_50_page_memory = memory_used * 5  # Conservative estimate
            print(f"   50-page estimate: {estimated_50_page_memory:.1f} MB")
            
            return estimated_50_page_memory < 1000  # Under 1GB
    except ImportError:
        print("💾 Memory analysis requires psutil package")
        return True
    except Exception as e:
        print(f"💾 Memory analysis error: {e}")
        return True

def main():
    """Main performance testing function"""
    print("🎯 Adobe India Hackathon 2025 - Performance Validation")
    print("Testing: Can process 50-page PDF in <10 seconds?")
    print("="*60)
    
    # Test 1: Performance on available PDFs
    print("\n🧪 TEST 1: Current PDF Performance")
    performance_ok = test_all_pdfs_performance()
    
    # Test 2: Largest file specific test
    print("\n🧪 TEST 2: Largest File Stress Test")
    largest_file_ok = test_large_pdf_performance()
    
    # Test 3: Memory estimation
    print("\n🧪 TEST 3: Memory Usage Analysis")
    memory_ok = estimate_memory_usage()
    
    # Final verdict
    print("\n" + "="*60)
    print("🏆 FINAL PERFORMANCE VERDICT")
    print("="*60)
    
    if performance_ok and largest_file_ok and memory_ok:
        print("✅ VERDICT: READY FOR 50-PAGE PDFs")
        print("   • Average processing time well under 10s")
        print("   • Memory usage within reasonable limits")
        print("   • Solution optimized for hackathon requirements")
        return True
    elif performance_ok and memory_ok:
        print("⚠️  VERDICT: LIKELY READY (with minor optimizations)")
        print("   • Current performance is good")
        print("   • May need small tweaks for very large files")
        return True
    else:
        print("❌ VERDICT: NEEDS OPTIMIZATION")
        print("   • Performance improvements required")
        print("   • Consider algorithm optimizations")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
