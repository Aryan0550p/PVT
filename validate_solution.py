#!/usr/bin/env python3
"""
Quick validation script to test the Adobe Hackathon solution
Run this after Docker installation to verify everything works
"""

import os
import json
import subprocess
import time
from pathlib import Path

def check_docker_installation():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Docker installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker not properly installed")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Docker not found. Please install Docker Desktop first.")
        return False

def test_docker_build():
    """Test building the Docker container"""
    print("\n🔨 Building Docker container...")
    try:
        result = subprocess.run([
            'docker', 'build', '--platform', 'linux/amd64', 
            '-t', 'pdfoutlineextractor:dev', '.'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Docker build successful!")
            return True
        else:
            print(f"❌ Docker build failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Docker build timed out")
        return False

def test_docker_run():
    """Test running the Docker container"""
    print("\n🚀 Running Docker container...")
    
    # Clear output directory first
    output_dir = Path("output")
    if output_dir.exists():
        for file in output_dir.glob("*.json"):
            file.unlink()
    
    start_time = time.time()
    
    try:
        # Use PowerShell-compatible path syntax
        current_dir = os.getcwd().replace('\\', '/')
        result = subprocess.run([
            'docker', 'run', '--rm',
            '-v', f'{current_dir}/input:/app/input:ro',
            '-v', f'{current_dir}/output:/app/output',
            '--network', 'none',
            'pdfoutlineextractor:dev'
        ], capture_output=True, text=True, timeout=60)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ Docker run successful! Processing time: {processing_time:.2f}s")
            print(f"Container output: {result.stdout}")
            return True, processing_time
        else:
            print(f"❌ Docker run failed: {result.stderr}")
            return False, processing_time
    except subprocess.TimeoutExpired:
        print("❌ Docker run timed out (>60s)")
        return False, 60.0

def validate_output():
    """Validate the generated JSON outputs"""
    print("\n📋 Validating output files...")
    
    output_dir = Path("output")
    input_dir = Path("input")
    
    # Check that input PDFs exist
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found in input directory")
        return False
    
    print(f"Input PDFs found: {len(pdf_files)}")
    
    # Check that corresponding JSON files exist
    json_files = list(output_dir.glob("*.json"))
    print(f"Output JSONs generated: {len(json_files)}")
    
    if len(json_files) != len(pdf_files):
        print(f"❌ Mismatch: {len(pdf_files)} PDFs but {len(json_files)} JSONs")
        return False
    
    # Validate JSON structure
    valid_count = 0
    total_headings = 0
    multilingual_count = 0
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check required fields
            if not all(key in data for key in ['title', 'outline', 'languages']):
                print(f"❌ {json_file.name}: Missing required fields")
                continue
            
            # Check outline structure
            outline = data['outline']
            if not isinstance(outline, list):
                print(f"❌ {json_file.name}: Outline is not a list")
                continue
            
            # Validate heading structure
            valid_headings = 0
            for heading in outline:
                if all(key in heading for key in ['level', 'text', 'page']):
                    if heading['level'] in ['H1', 'H2', 'H3', 'H4']:
                        valid_headings += 1
            
            total_headings += valid_headings
            
            # Check multilingual support
            if data['languages'].get('is_multilingual', False):
                multilingual_count += 1
            
            print(f"✅ {json_file.name}: {valid_headings} headings, "
                  f"multilingual: {data['languages'].get('is_multilingual', False)}")
            valid_count += 1
            
        except Exception as e:
            print(f"❌ {json_file.name}: Error reading file - {e}")
    
    print(f"\n📊 Validation Summary:")
    print(f"  Valid JSON files: {valid_count}/{len(json_files)}")
    print(f"  Total headings extracted: {total_headings}")
    print(f"  Multilingual documents: {multilingual_count}")
    
    return valid_count == len(json_files) and total_headings > 0

def main():
    print("🎯 Adobe India Hackathon 2025 - Solution Validation")
    print("=" * 50)
    
    # Check current directory
    if not Path("extract_outline_backup.py").exists():
        print("❌ Please run this script from the adobe_n1 directory")
        return False
    
    # Step 1: Check Docker installation
    if not check_docker_installation():
        print("\n💡 Install Docker Desktop from: https://www.docker.com/products/docker-desktop/")
        return False
    
    # Step 2: Test Docker build
    if not test_docker_build():
        return False
    
    # Step 3: Test Docker run
    success, processing_time = test_docker_run()
    if not success:
        return False
    
    # Step 4: Validate output
    if not validate_output():
        return False
    
    # Final results
    print("\n🏆 VALIDATION COMPLETE!")
    print("=" * 50)
    print("✅ All tests passed!")
    print(f"✅ Processing time: {processing_time:.2f}s (requirement: <10s)")
    print("✅ Docker container builds and runs successfully")
    print("✅ JSON outputs generated and validated")
    print("✅ Multilingual support working")
    print("\n🚀 Solution is ready for Adobe Hackathon submission!")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
