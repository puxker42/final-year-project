import subprocess
import sys
import os

def check_assets():
    """Ensures necessary Flask folders exist."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    required_dirs = ["templates", "static"]
    required_files = ["yolov8n.pt", "ui_server.py"]
    
    for folder in required_dirs:
        path = os.path.join(base_dir, folder)
        if not os.path.exists(path):
            print(f"[WARNING] Folder '{folder}' not found. UI might not load correctly.")
            
    for filename in required_files:
        path = os.path.join(base_dir, filename)
        if not os.path.exists(path) and filename != "yolov8n.pt":
            print(f"[ERROR] Required file '{filename}' missing from {base_dir}")
            sys.exit(1)
        elif not os.path.exists(path) and filename == "yolov8n.pt":
            print(f"[INFO] 'yolov8n.pt' not found locally. It will be downloaded automatically on first run.")

def ensure_pip():
    """Ensures pip is installed. If not, installs it."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        print("[SYSTEM] pip not found. Attempting to install pip using ensurepip...")
        try:
            subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)
            print("[SYSTEM] pip installed successfully.")
        except Exception as e:
            print(f"[WARNING] ensurepip failed: {e}. Attempting fallback (get-pip.py)...")
            try:
                import urllib.request
                import tempfile
                get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tf:
                    get_pip_path = tf.name
                
                print("[SYSTEM] Downloading get-pip.py...")
                urllib.request.urlretrieve(get_pip_url, get_pip_path)
                
                print("[SYSTEM] Installing pip...")
                subprocess.run([sys.executable, get_pip_path], check=True)
                os.remove(get_pip_path)
                
                print("[SYSTEM] pip installed successfully via get-pip.py.")
            except Exception as e2:
                print(f"[ERROR] Failed to install pip automatically: {e2}")
                sys.exit(1)

def install_dependencies():
    """Installs dependencies from requirements.txt if anything is missing."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    req_file = os.path.join(base_dir, "requirements.txt")
    
    # Quick check to see if we need to install
    needed = False
    try:
        import flask
        import cv2
        import ultralytics
    except ImportError:
        needed = True

    if needed:
        print("[SYSTEM] Missing dependencies detected. Installing from requirements.txt...")
        if not os.path.exists(req_file):
            print("[ERROR] requirements.txt not found! Cannot install dependencies.")
            sys.exit(1)
            
        ensure_pip()
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
            print("[SYSTEM] Dependencies installed successfully.")
        except Exception as e:
            print(f"[ERROR] Installation failed: {e}")
            sys.exit(1)
    else:
        print("[SYSTEM] All dependencies are already met.")

def start_ui_server():
    """Starts the UI server script."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, "ui_server.py")
    
    if not os.path.exists(script_path):
        print(f"[ERROR] ui_server.py not found in {base_dir}")
        sys.exit(1)
        
    print(f"\n[SYSTEM] Launching UI Server...")
    print(f"[INFO] Access the UI at: http://localhost:8080")
    print("========================================\n")
    
    try:
        # Using subprocess.run to execute the server
        subprocess.run([sys.executable, script_path], check=True)
    except KeyboardInterrupt:
        print("\n[SYSTEM] Operator Client stopped by user.")
    except Exception as e:
        print(f"[ERROR] UI Server crashed: {e}")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print("========================================")
    print("   Rover Operator Client Auto-Starter   ")
    print("========================================")
    
    # 1. Verify environment
    check_assets()
    
    # 2. Install dependencies
    install_dependencies()
    
    # 3. Start server
    start_ui_server()
