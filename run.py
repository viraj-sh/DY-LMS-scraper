import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent / "src"
DATA_DIR = Path(__file__).parent / "data"

scripts = {
    "1": ("Generate Login Token", ["generate_session.py"]),
    "2": ("Scrape All Data", [
        "fetch_dashboard.py",
        "parse_dashboard.py",
        "fetch_subject.py",
        "parse_subject.py",
        "fetch_document.py",
        "parse_document.py",
        "ultimate_json.py"
    ]),
    "3": ("Download Resources", ["output.py"]),
    "0": ("Exit", None)
}

def run_script(script_name):
    """Run a single script with real-time output"""
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"Error: Script {script_name} not found!")
        return False
    
    # Create data/ only for generate_session.py
    if script_name == "generate_session.py":
        DATA_DIR.mkdir(exist_ok=True)
    
    print(f"\n{'='*40}\nRunning {script_name}\n{'='*40}")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=SCRIPTS_DIR.parent
    )
    return result.returncode == 0

def main_menu():
    while True:
        print("\nMain Menu:")
        for key in sorted(scripts.keys()):
            if key == "0":
                continue
            print(f"{key}. {scripts[key][0]}")
        print("0. Exit")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "0":
            print("Exiting...")
            break
            
        if choice in scripts:
            _, scripts_to_run = scripts[choice]
            if scripts_to_run is None:
                continue
                
            success = True
            for script in scripts_to_run:
                if not run_script(script):
                    print(f"\n⚠️ Failed to execute {script}. Stopping pipeline.")
                    success = False
                    break
            
            if success:
                print("\n✅ Operation completed successfully")
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main_menu()