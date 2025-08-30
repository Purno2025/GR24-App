#!/bin/bash
echo "Building GR24 Application for Mac..."

# Install dependencies
pip3 install -r requirements.txt

# Build executable
pyinstaller --onefile --windowed --name "GR24" --icon=icon.icns GR24_Mac.py

echo "Build complete! Check the 'dist' folder for GR24"

