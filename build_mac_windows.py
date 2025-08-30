#!/usr/bin/env python3
"""
Windows to Mac Build Script for GR24
This script provides multiple options for building Mac executables from Windows
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🚀 GR24 Mac Build Script")
    print("=" * 60)
    print("This script helps you build Mac executables from Windows")
    print()

def check_docker():
    """Check if Docker is available"""
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def check_git():
    """Check if Git is available"""
    try:
        result = subprocess.run(["git", "--version"], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def create_requirements():
    """Create requirements.txt"""
    requirements = """pandas>=1.5.0
PySide6>=6.4.0
pyinstaller>=5.0.0
"""
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    print("✅ Created requirements.txt")

def create_pyinstaller_spec():
    """Create a PyInstaller spec file for better control"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['mac.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GR24_Mac',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    with open("GR24_Mac.spec", "w") as f:
        f.write(spec_content)
    print("✅ Created GR24_Mac.spec")

def method_1_docker():
    """Method 1: Using Docker"""
    print("\n🔧 Method 1: Docker Build")
    print("-" * 30)
    
    if not check_docker():
        print("❌ Docker is not installed or not running")
        print("Please install Docker Desktop from: https://www.docker.com/products/docker-desktop")
        return False
    
    print("✅ Docker is available")
    
    # Create necessary files
    create_requirements()
    create_pyinstaller_spec()
    
    # Create Dockerfile
    dockerfile = """FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Set working directory
WORKDIR /app

# Copy application files
COPY mac.py /app/
COPY GR24_Mac.spec /app/

# Build the application
RUN pyinstaller GR24_Mac.spec

# The executable will be in /app/dist/
"""
    
    with open("Dockerfile.mac", "w") as f:
        f.write(dockerfile)
    print("✅ Created Dockerfile.mac")
    
    # Build with Docker
    print("\n🔄 Building with Docker...")
    commands = [
        "docker build -f Dockerfile.mac -t gr24-mac-builder .",
        "docker run --name gr24-mac-build gr24-mac-builder",
        "docker cp gr24-mac-build:/app/dist/GR24_Mac ./dist/",
        "docker rm gr24-mac-build"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
    
    print("✅ Docker build completed successfully!")
    return True

def method_2_github_actions():
    """Method 2: Using GitHub Actions"""
    print("\n☁️ Method 2: GitHub Actions (Recommended)")
    print("-" * 40)
    
    if not check_git():
        print("❌ Git is not installed")
        print("Please install Git from: https://git-scm.com/")
        return False
    
    print("✅ Git is available")
    
    # Check if this is a git repository
    if not os.path.exists(".git"):
        print("❌ This is not a Git repository")
        print("Please initialize Git and push to GitHub first")
        return False
    
    print("✅ Git repository detected")
    
    # Create GitHub Actions workflow
    os.makedirs(".github/workflows", exist_ok=True)
    
    workflow_content = """name: Build Mac Executable

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build-mac:
    runs-on: macos-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pandas PySide6 pyinstaller
        
    - name: Build executable
      run: |
        pyinstaller --onefile --windowed --name "GR24_Mac" mac.py
        
    - name: Upload artifact
      uses: actions/upload-artifact@v4
      with:
        name: GR24-Mac-Executable
        path: dist/GR24_Mac
        
    - name: Create release
      if: github.event_name == 'push'
      uses: softprops/action-gh-release@v1
      with:
        files: dist/GR24_Mac
        tag_name: v${{ github.run_number }}
        name: GR24 Mac Executable v${{ github.run_number }}
        body: |
          Mac executable for GR24 Pricing Application
          
          ## Installation Instructions:
          1. Download the GR24_Mac file
          2. Right-click and select 'Open'
          3. If prompted about security, go to System Preferences > Security & Privacy
          4. Click 'Open Anyway' to allow the application
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""
    
    with open(".github/workflows/build-mac.yml", "w") as f:
        f.write(workflow_content)
    print("✅ Created GitHub Actions workflow")
    
    print("\n📋 Next steps:")
    print("1. Push your code to GitHub:")
    print("   git add .")
    print("   git commit -m 'Add Mac build workflow'")
    print("   git push origin main")
    print("2. Go to your GitHub repository")
    print("3. Click on 'Actions' tab")
    print("4. The build will start automatically")
    print("5. Download the executable from the 'Releases' section")
    
    return True

def method_3_manual_instructions():
    """Method 3: Manual instructions"""
    print("\n📝 Method 3: Manual Build Instructions")
    print("-" * 40)
    
    print("If you have access to a Mac computer:")
    print("1. Copy your mac.py file to the Mac")
    print("2. Install Python 3.11 on the Mac")
    print("3. Run these commands:")
    print("   pip install pandas PySide6 pyinstaller")
    print("   pyinstaller --onefile --windowed --name 'GR24_Mac' mac.py")
    print("4. The executable will be in the dist/ folder")
    
    print("\nAlternative: Use a Mac virtual machine or cloud service")

def main():
    """Main function"""
    print_header()
    
    print("Available build methods:")
    print("1. Docker (requires Docker Desktop)")
    print("2. GitHub Actions (requires GitHub repository)")
    print("3. Manual instructions")
    print("4. Exit")
    
    while True:
        choice = input("\nSelect a method (1-4): ").strip()
        
        if choice == "1":
            if method_1_docker():
                print("\n🎉 Success! Mac executable created in ./dist/GR24_Mac")
            break
        elif choice == "2":
            if method_2_github_actions():
                print("\n🎉 GitHub Actions workflow created!")
            break
        elif choice == "3":
            method_3_manual_instructions()
            break
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1-4.")
    
    print("\n📋 Instructions for Mac users:")
    print("1. Copy the GR24_Mac file to their Mac")
    print("2. Right-click and select 'Open'")
    print("3. If prompted about security, go to System Preferences > Security & Privacy")
    print("4. Click 'Open Anyway' to allow the application")

if __name__ == "__main__":
    main()
