# ASU DSL Maya Extensions
A Maya toolkit that provides a custom shelf with export functionality for character rigs and animations.

## Features
- Custom Maya shelf with export tools
- FBX and ASCII export capabilities
- Automatic rig detection and selection
- Configurable export naming conventions
- Playblast creation with custom settings

## Creating New Tool Extensions
To add your own tool to the shelf:
1. Create a new directory at the root level (e.g., `mytool/`)
2. Add a `tool_config.py` with your tool's configuration:
```python
TOOL_CONFIG = {
    'label': 'My Tool',
    'command': 'from mytool.ui.gui import show_gui; show_gui()',
    'icon': 'ui/buttons/icon.png',
    'annotation': 'Tool Description'
}
```
3. Organize your tool's code following this structure:
```
mytool/
    ├── __init__.py
    ├── tool_config.py
    ├── core/
    │   ├── __init__.py
    │   └── your_core_logic.py
    ├── ui/
    │   ├── __init__.py
    │   ├── gui.py
    │   └── buttons/
    └── config/
        ├── __init__.py
        └── settings.py
```
The tool will be automatically discovered and added to the shelf on Maya startup.

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

## Available Tools

### Export Tool
After installation, use the Export Tool to:
1. Configure export settings
2. Select export location
3. Export your rig/animation in FBX or ASCII format

The tool will automatically detect and select rigs in your scene if none are selected.

### Playblast Tool
Create high-quality playblasts with:
- Custom resolution settings
- Camera selection
- View settings (HUD, grid visibility)
- Output path management
- Quality control

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
