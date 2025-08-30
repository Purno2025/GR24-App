#!/usr/bin/env python3
"""
Cross-platform build script for Mac executable from Windows
Uses Docker to create a Mac-compatible build environment
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True

def create_dockerfile():
    """Create a Dockerfile for Mac build environment"""
    dockerfile_content = """
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install pyinstaller pandas PySide6

# Set working directory
WORKDIR /app

# Copy application files
COPY mac.py /app/
COPY requirements.txt /app/

# Build the application
RUN pyinstaller --onefile --windowed --name "GR24_Mac" mac.py

# The executable will be in /app/dist/
"""
    
    with open("Dockerfile.mac", "w") as f:
        f.write(dockerfile_content)
    print("Created Dockerfile.mac")

def create_requirements():
    """Create requirements.txt if it doesn't exist"""
    if not os.path.exists("requirements.txt"):
        requirements_content = """pandas
PySide6
pyinstaller
"""
        with open("requirements.txt", "w") as f:
            f.write(requirements_content)
        print("Created requirements.txt")

def build_with_docker():
    """Build Mac executable using Docker"""
    print("=== Building Mac Executable with Docker ===")
    
    # Create necessary files
    create_requirements()
    create_dockerfile()
    
    # Build Docker image
    if not run_command("docker build -f Dockerfile.mac -t gr24-mac-builder ."):
        print("Failed to build Docker image")
        return False
    
    # Run container and copy executable
    container_name = "gr24-mac-build"
    
    # Remove existing container if it exists
    run_command(f"docker rm -f {container_name}", cwd=None)
    
    # Run container
    if not run_command(f"docker run --name {container_name} gr24-mac-builder"):
        print("Failed to run Docker container")
        return False
    
    # Create dist directory if it doesn't exist
    os.makedirs("dist", exist_ok=True)
    
    # Copy executable from container
    if not run_command(f"docker cp {container_name}:/app/dist/GR24_Mac ./dist/"):
        print("Failed to copy executable from container")
        return False
    
    # Clean up container
    run_command(f"docker rm -f {container_name}", cwd=None)
    
    print("=== Build Complete ===")
    print("Mac executable is available in: ./dist/GR24_Mac")
    return True

def main():
    """Main function"""
    print("GR24 Mac Build Script")
    print("This script will build a Mac executable from Windows using Docker")
    
    # Check if Docker is installed
    if not run_command("docker --version"):
        print("Error: Docker is not installed or not running")
        print("Please install Docker Desktop from: https://www.docker.com/products/docker-desktop")
        return
    
    # Build the application
    if build_with_docker():
        print("\n✅ Success! Mac executable created.")
        print("📁 Location: ./dist/GR24_Mac")
        print("📋 Instructions for Mac users:")
        print("   1. Copy the GR24_Mac file to their Mac")
        print("   2. Right-click and select 'Open'")
        print("   3. If prompted about security, go to System Preferences > Security & Privacy")
        print("   4. Click 'Open Anyway' to allow the application")
    else:
        print("\n❌ Build failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
