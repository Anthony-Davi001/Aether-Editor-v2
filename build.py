import argparse
import os
import shutil
import subprocess
import sys
import itertools
import time
import threading

# ANSI Styles and Colors
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"

def log_info(msg: str):
    print(f"{CYAN}{BOLD}[INFO]{RESET} {msg}")

def log_warn(msg: str):
    print(f"{YELLOW}{BOLD}[WARNING]{RESET} {msg}")

def log_success(msg: str):
    print(f"{GREEN}{BOLD}[SUCCESS]{RESET} {msg}")

def log_error(msg: str):
    print(f"{RED}{BOLD}[ERROR]{RESET} {msg}")

def clean():
    """Removes previous build directories."""
    removed = False
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            log_warn(f"Directory removed: {folder}/")
            removed = True
    if not removed:
        log_info("No previous build directories found.")


def build():
    """Executes PyInstaller with a loading spinner, showing only errors if it fails."""
    clean()

    if not shutil.which("pyinstaller"):
        log_error("PyInstaller is not installed or not found in your PATH.")
        log_info("Please install it by running: pip install pyinstaller")
        sys.exit(1)
        
    log_info("Building application using 'main.spec'...")
    
    cmd = ["pyinstaller", "main.spec"]
    
    done_event = threading.Event()
    
    def spinner():
        symbols = itertools.cycle(["/", "-", "\\", "|"])
        while not done_event.is_set():
            symbol = next(symbols)
            sys.stdout.write(f"\r{CYAN}{BOLD}[BUILDING]{RESET} Compiling... {symbol}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    t = threading.Thread(target=spinner)
    t.start()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
    finally:
        done_event.set()
        t.join()
    
    if result.returncode != 0:
        log_error("Failed to generate executable. Error details:\n")
        print(f"{RED}{result.stderr.strip()}{RESET}")
        sys.exit(result.returncode)
        
    log_success("Build completed successfully! The executable is ready in the 'dist/' directory.")

def main():
    parser = argparse.ArgumentParser(
        description="Build automation tool for Aether Editor."
    )
    parser.add_argument(
        "-c", "--clean",
        action="store_true",
        help="Only clean temporary build directories (build/ and dist/)"
    )

    args = parser.parse_args()

    if args.clean:
        clean()
    else:
        build()

if __name__ == "__main__":
    main()