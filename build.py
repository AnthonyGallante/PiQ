#!/usr/bin/env python
"""
Build script for packaging πQ into a single executable.
This script ensures all dependencies are installed and runs PyInstaller.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Verify Python version is at least 3.7"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required to build this application.")
        sys.exit(1)

def install_dependencies():
    """Install required packages if not already installed"""
    required_packages = [
        "kivy>=2.3.0",
        "pyinstaller>=5.0",
        "pillow",  # Required for some Kivy functionality
        "kivy_deps.sdl2", 
        "kivy_deps.glew"
    ]
    
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}. Please install it manually.")
            sys.exit(1)

def create_icon():
    """Create a simple icon if none exists (using PIL)"""
    if os.path.exists("icon.ico"):
        return
    
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple blue circle with Pi symbol
        img = Image.new('RGBA', (256, 256), color=(0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        
        # Draw circle
        d.ellipse((10, 10, 246, 246), fill=(51, 153, 255))
        
        # Save as .ico for Windows, .png for other platforms
        img.save("icon.ico", format="ICO")
        img.save("icon.png", format="PNG")
        print("Created icon files: icon.ico and icon.png")
    except ImportError:
        print("PIL not available, skipping icon creation.")
    except Exception as e:
        print(f"Error creating icon: {e}")

def build_executable():
    """Run PyInstaller to build the executable"""
    print("Building executable with PyInstaller...")
    
    # Check if spec file exists, use it if it does
    if os.path.exists("piQ.spec"):
        cmd = ["pyinstaller", "--noconfirm", "piQ.spec"]
    else:
        # Build command for different platforms
        if platform.system() == "Windows":
            cmd = [
                "pyinstaller",
                "--name=piQ",
                "--onefile",
                "--windowed",
                "--icon=icon.ico" if os.path.exists("icon.ico") else "",
                "--add-data=pi_digits.txt;.",
                "--add-data=piq.kv;.",
                "main.py"
            ]
        else:  # macOS, Linux
            separator = ":" # Use : instead of ; for non-Windows
            cmd = [
                "pyinstaller",
                "--name=piQ",
                "--onefile",
                "--windowed",
                f"--icon=icon.png" if os.path.exists("icon.png") else "",
                f"--add-data=pi_digits.txt{separator}.",
                f"--add-data=piq.kv{separator}.",
                "main.py"
            ]
    
    # Remove empty strings from cmd (in case icon doesn't exist)
    cmd = [item for item in cmd if item]
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild successful! Executable is located in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        sys.exit(1)

def main():
    """Main build function"""
    print("===== Building πQ Application =====")
    
    check_python_version()
    install_dependencies()
    create_icon()
    build_executable()
    
    print("\n===== Build Complete =====")
    print(f"The executable is in the 'dist' directory: {os.path.abspath('dist')}")

if __name__ == "__main__":
    main() 