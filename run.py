#!/usr/bin/env python
"""
Run Script for Financial Analysis Web Platform
---------------------------------------------
This script starts both the Flask backend and React frontend
"""

import os
import sys
import subprocess
import threading
import time
import shutil
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent.absolute()
API_DIR = BASE_DIR / "api"
WEB_DIR = BASE_DIR / "web"

def check_node_installed():
    """Check if Node.js is installed"""
    try:
        npm_path = shutil.which("npm")
        if npm_path is None:
            print("\nERROR: Node.js/npm not found. Please install Node.js first:")
            print("1. Download from https://nodejs.org/")
            print("2. Install and make sure 'npm' is in your PATH")
            print("3. Restart your terminal and try again\n")
            print("Alternatively, you can still use the API server without the React frontend:")
            print("    python run.py backend")
            print("Then access http://localhost:5000 in your browser.")
            return False
        return True
    except Exception:
        return False

def check_local_node():
    """Check if we have a local Node.js installation in the node directory"""
    node_dir = BASE_DIR / "node"
    node_exe = node_dir / "node.exe"
    npm_cmd = node_dir / "npm.cmd"
    
    return node_dir.exists() and node_exe.exists() and npm_cmd.exists()

def run_with_local_node(command, cwd=None):
    """Run a command using the local Node.js installation"""
    node_dir = BASE_DIR / "node"
    
    # Create environment with node directory in PATH
    env = os.environ.copy()
    env["PATH"] = str(node_dir) + os.pathsep + env.get("PATH", "")
    
    # Use appropriate working directory
    if cwd is None:
        cwd = os.getcwd()
    
    # Run the command with the modified environment
    return subprocess.run(command, env=env, cwd=cwd)

def check_python_dependencies():
    """Check if required Python packages are installed"""
    required_packages = ["flask", "flask_cors", "pandas", "plotly", "yfinance"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstalling missing Python packages: {', '.join(missing_packages)}")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages)
        print("Required packages installed successfully.")
    
    return True

def run_backend():
    """Run Flask backend API"""
    try:
        # Check Python dependencies
        check_python_dependencies()
        
        # Check if API directory exists
        if not API_DIR.exists():
            print(f"\nERROR: API directory not found at {API_DIR}")
            print("Please make sure the 'api' folder exists with the Flask application\n")
            return False
            
        print("Starting Flask backend server...")
        os.chdir(API_DIR)
        subprocess.run([sys.executable, "app.py"])
        return True
    except KeyboardInterrupt:
        print("\nBackend server stopped.")
        return True
    except Exception as e:
        print(f"\nERROR starting backend: {e}")
        return False

def run_frontend():
    """Run React frontend development server"""
    try:
        # Check if web directory exists
        if not WEB_DIR.exists():
            print(f"\nERROR: Web directory not found at {WEB_DIR}")
            print("Please make sure the 'web' folder exists with the React application\n")
            return False
        
        print("Starting React development server...")
        # Use the batch file instead of directly calling npm
        batch_file = BASE_DIR / "start_frontend.bat"
        if batch_file.exists():
            subprocess.run([str(batch_file)], shell=True)
            return True
        else:
            print(f"ERROR: Batch file {batch_file} not found")
            print("Please make sure start_frontend.bat exists in the project root")
            return False
    except KeyboardInterrupt:
        print("\nFrontend server stopped.")
        return True
    except Exception as e:
        print(f"\nERROR starting frontend: {e}")
        return False

def build_frontend():
    """Build frontend for production"""
    if not check_node_installed() and not check_local_node():
        return False
        
    try:
        # Check if web directory exists
        if not WEB_DIR.exists():
            print(f"\nERROR: Web directory not found at {WEB_DIR}")
            print("Please make sure the 'web' folder exists with the React application\n")
            return False
            
        os.chdir(WEB_DIR)
        if not (WEB_DIR / "node_modules").exists():
            print("Installing frontend dependencies (this may take a while)...")
            if check_local_node():
                run_with_local_node(["npm", "install"], cwd=WEB_DIR)
            else:
                subprocess.run(["npm", "install"])
        
        print("Building frontend for production...")
        if check_local_node():
            run_with_local_node(["npm", "run", "build"], cwd=WEB_DIR)
        else:
            subprocess.run(["npm", "run", "build"])
        print("Frontend build complete. Files are in web/build directory.")
        
        # Copy build to API static folder
        build_dir = WEB_DIR / "build"
        if build_dir.exists():
            print(f"React application successfully built!")
            print(f"You can now run 'python run.py backend' and access the app at http://localhost:5000")
        return True
    except Exception as e:
        print(f"\nERROR building frontend: {e}")
        return False

def run_both():
    """Run both backend and frontend concurrently"""
    # Check Python dependencies
    check_python_dependencies()
    
    # Check Node.js
    if not check_node_installed() and not check_local_node():
        print("\nWARNING: Node.js not found. Starting only the backend server.")
        run_backend()
        return
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Give the backend time to start
    print("Starting backend...")
    time.sleep(2)
    
    # Start frontend
    print("Starting frontend...")
    run_frontend()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nFinancial Analysis Platform Runner")
        print("==================================")
        print("Usage: python run.py [backend|frontend|build|both]")
        print("\nCommands:")
        print("  backend  - Start the Flask API server only")
        print("  frontend - Start the React development server only")
        print("  build    - Build the React frontend for production")
        print("  both     - Run both backend and frontend servers")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "backend":
        success = run_backend()
        if not success:
            sys.exit(1)
    elif command == "frontend":
        success = run_frontend()
        if not success:
            sys.exit(1)
    elif command == "build":
        success = build_frontend()
        if not success:
            sys.exit(1)
    elif command == "both":
        run_both()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python run.py [backend|frontend|build|both]")
        sys.exit(1)