# ASU DSL Maya Extensions

A Maya toolkit that provides a custom shelf with export functionality for character rigs and animations.

## Features
- Custom Maya shelf with export tools
- FBX and ASCII export capabilities
- Automatic rig detection and selection
- Configurable export naming conventions

## Installation
1. Download or clone this repository
2. Right-click `install_tool.bat` and select "Run as administrator"
3. Follow the prompts to install for your Maya version(s)
   - The installer will automatically detect Maya installations
   - You can choose to install for specific versions or all versions
   - If no Maya installations are found, you can manually specify the path

## Requirements
- Autodesk Maya (2023 or 2024)
- Windows OS
- Either:
  - Python installed and added to PATH, or
  - Anaconda/Miniconda installed, or
  - Maya's internal Python

## Usage
After installation, the "ASU DSL Shelf" will appear in Maya with an export button. Click it to:
1. Configure export settings
2. Select export location
3. Export your rig/animation in FBX or ASCII format

The tool will automatically detect and select rigs in your scene if none are selected.
