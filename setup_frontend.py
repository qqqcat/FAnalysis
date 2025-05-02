#!/usr/bin/env python
"""
Node.js Frontend Setup Helper
----------------------------
This script helps check Node.js installation and download it if needed.
"""

import os
import sys
import subprocess
import platform
import zipfile
import shutil
import tempfile
from pathlib import Path
import urllib.request

# Define paths
BASE_DIR = Path(__file__).parent.absolute()
WEB_DIR = BASE_DIR / "web"
NODE_DIR = BASE_DIR / "node"

def is_node_installed():
    """Check if Node.js is already available in PATH"""
    try:
        # Try to run node --version using subprocess in a more reliable way
        node_result = subprocess.run(
            ["node", "--version"], 
            capture_output=True, 
            text=True,
            shell=True,
            check=False  # Don't raise an exception on non-zero return
        )
        
        npm_result = subprocess.run(
            ["npm", "--version"], 
            capture_output=True, 
            text=True,
            shell=True,
            check=False  # Don't raise an exception on non-zero return
        )
        
        print(f"Node.js check result: {node_result.returncode}")
        print(f"Node.js version output: {node_result.stdout.strip() if node_result.stdout else 'None'}")
        print(f"npm check result: {npm_result.returncode}")
        print(f"npm version output: {npm_result.stdout.strip() if npm_result.stdout else 'None'}")
        
        return node_result.returncode == 0 and npm_result.returncode == 0
    except Exception as e:
        print(f"Error checking Node.js: {e}")
        return False

def get_node_download_url():
    """Get the appropriate Node.js download URL based on OS"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Using Node.js 18.x LTS as it's stable for React development
    if system == "windows":
        if "64" in machine:
            if "arm" in machine or "aarch" in machine:
                return "https://nodejs.org/dist/v18.16.1/node-v18.16.1-win-arm64.zip"
            else:
                return "https://nodejs.org/dist/v18.16.1/node-v18.16.1-win-x64.zip"
        else:
            return "https://nodejs.org/dist/v18.16.1/node-v18.16.1-win-x86.zip"
    
    # Default to 64-bit Windows URL if we can't determine
    return "https://nodejs.org/dist/v18.16.1/node-v18.16.1-win-x64.zip"

def download_and_setup_node():
    """Download and set up a local Node.js installation"""
    print("Downloading and setting up a local Node.js installation...")
    
    # Get the appropriate download URL
    download_url = get_node_download_url()
    node_filename = download_url.split("/")[-1]
    
    # Create a temporary directory for the download
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = temp_path / node_filename
        
        # Download Node.js
        print(f"Downloading Node.js from {download_url}...")
        urllib.request.urlretrieve(download_url, zip_path)
        
        # Extract the zip file
        print("Extracting Node.js...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_path)
        
        # Find the extracted directory
        extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir() and d.name.startswith("node")]
        if not extracted_dirs:
            print("Error: Could not find extracted Node.js directory")
            return False
        
        node_extracted = extracted_dirs[0]
        
        # Remove existing Node.js directory if it exists
        if NODE_DIR.exists():
            shutil.rmtree(NODE_DIR)
        
        # Move the extracted directory to our Node.js directory
        shutil.move(str(node_extracted), str(NODE_DIR))
        
        print(f"Node.js has been set up at {NODE_DIR}")
        return True

def setup_package_json():
    """Create a basic package.json if it doesn't exist"""
    package_json_path = WEB_DIR / "package.json"
    
    if not package_json_path.exists():
        print("Creating basic package.json file...")
        
        package_json = {
            "name": "financial-analysis-platform",
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "@testing-library/jest-dom": "^5.16.5",
                "@testing-library/react": "^13.4.0",
                "@testing-library/user-event": "^13.5.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1",
                "web-vitals": "^2.1.4",
                "antd": "^5.4.0",
                "axios": "^1.3.5",
                "i18next": "^22.4.14",
                "i18next-browser-languagedetector": "^7.0.1",
                "react-i18next": "^12.2.0",
                "react-router-dom": "^6.10.0",
                "plotly.js": "^2.20.0",
                "react-plotly.js": "^2.6.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "eslintConfig": {
                "extends": [
                    "react-app",
                    "react-app/jest"
                ]
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        }
        
        # Save the package.json file
        with open(package_json_path, 'w') as f:
            import json
            json.dump(package_json, f, indent=2)
        
        print("package.json created successfully!")

def run_npm_install():
    """Run npm install to install frontend dependencies"""
    print("Installing frontend dependencies...")
    
    node_path = NODE_DIR / "node.exe"
    npm_path = NODE_DIR / "npm.cmd"
    
    if not node_path.exists() or not npm_path.exists():
        print(f"Error: Node.js installation files not found at {NODE_DIR}")
        return False
    
    # Create a PATH environment with Node.js directory added
    env = os.environ.copy()
    env["PATH"] = str(NODE_DIR) + os.pathsep + env.get("PATH", "")
    
    try:
        os.chdir(WEB_DIR)
        subprocess.run([str(npm_path), "install"], env=env, check=True)
        print("Frontend dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running npm install: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    """Main function to handle setup"""
    print(f"\nFinancial Analysis Platform Frontend Setup")
    print(f"=========================================")
    
    # Check if web directory exists
    if not WEB_DIR.exists():
        print(f"ERROR: Web directory not found at {WEB_DIR}")
        print("Please make sure the 'web' folder exists")
        return False
    
    # Check if Node.js is already installed
    if is_node_installed():
        print("Node.js is already installed and available in your PATH.")
        print("You can run 'python run.py frontend' to start the frontend development server.")
        return True
    
    # Download and set up Node.js locally
    print("Node.js is not installed or not in your PATH.")
    print("This script will download and set up a local Node.js installation.")
    
    # Ask for confirmation
    if input("Proceed? (y/n): ").lower() != 'y':
        print("Setup cancelled.")
        return False
    
    if not download_and_setup_node():
        print("Failed to set up Node.js.")
        return False
    
    # Set up package.json if needed
    setup_package_json()
    
    # Run npm install
    if not run_npm_install():
        print("Failed to install frontend dependencies.")
        return False
    
    print("\nSetup completed successfully!")
    print("You can now run 'python run.py frontend' to start the frontend development server.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)