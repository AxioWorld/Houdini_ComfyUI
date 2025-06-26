import subprocess
import os
import sys
import re
from hutil.Qt import QtCore, QtGui, QtWidgets # type: ignore

def get_python_version(executable_path):
    """
    Retrieves the full version string of a Python executable (e.g., "3.9.7").
    Returns the version string or None if it cannot be determined.
    """
    try:
        # Execute the command 'python --version' to get the version
        # Python often outputs its version to stderr for '--version'
        result = subprocess.run(
            [executable_path, "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5  # Add a timeout to prevent hanging on unresponsive executables
        )
        version_output = result.stderr.strip() or result.stdout.strip()
        
        # Extract the version number (e.g., "Python 3.9.7" -> "3.9.7")
        match = re.search(r"Python (\d+\.\d+\.\d+)", version_output)
        if match:
            return match.group(1)
        
        # Handle cases like "Python 3.10.0rc1" which might not match \d+\.\d+\.\d+
        match = re.search(r"Python (\d+\.\d+)", version_output)
        if match:
            # For versions like "3.10", add a ".0" for consistent comparison
            version_parts = match.group(1).split('.')
            if len(version_parts) == 2:
                return f"{version_parts[0]}.{version_parts[1]}.0"
            return match.group(1)

    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        # Silently ignore errors for files that are not valid Python executables or timeouts
        pass
    return None

def parse_version_string(version_str):
    """
    Parses a version string (e.g., "3.11.2") into a tuple of integers (3, 11, 2).
    Handles cases with fewer parts (e.g., "3.10" -> (3, 10, 0)).
    Returns a tuple of integers.
    """
    if not version_str:
        return (0, 0, 0) # Default for invalid/missing version
    
    parts = []
    for part in version_str.split('.'):
        try:
            parts.append(int(part))
        except ValueError:
            # Handle non-numeric parts like "3.10.0rc1" by stopping here
            break
    
    # Pad with zeros if less than 3 parts (e.g., "3.10" becomes (3, 10, 0))
    while len(parts) < 3:
        parts.append(0)
    
    return tuple(parts)

def find_global_python_executables():
    """
    Searches for global Python executables in the system's PATH.
    Returns a dictionary where keys are absolute executable paths and values are their versions (string).
    """
    found_pythons = {}
    
    path_env = os.environ.get("PATH", "")
    path_dirs = path_env.split(os.pathsep)

    print("Scanning system PATH for global Python installations...")
    
    # Common Python executable names to look for
    python_names = [
        "python", "python3", "python2", 
        "python3.13", "python3.12", "python3.11", "python3.10", 
        "python3.9", "python3.8", "python3.7", "python2.7"
    ]

    # Use a set to store real paths to avoid processing the same executable multiple times
    checked_real_paths = set() 

    for path_dir in path_dirs:
        if not os.path.isdir(path_dir):
            continue

        for py_name in python_names:
            exec_path = os.path.join(path_dir, py_name)
            
            # Handle common Windows executable extensions
            potential_paths = [exec_path]
            if sys.platform == 'win32':
                potential_paths.append(exec_path + '.exe')
                potential_paths.append(exec_path + '.cmd') # For some launchers

            for potential_path in potential_paths:
                if os.path.isfile(potential_path) and os.access(potential_path, os.X_OK):
                    # Resolve real path to handle symbolic links (common on macOS/Linux)
                    real_path = os.path.realpath(potential_path)
                    
                    if real_path not in checked_real_paths:
                        version = get_python_version(real_path)
                        if version:
                            found_pythons[real_path] = version
                            checked_real_paths.add(real_path)
                            # print(f"  Found: {real_path} (v{version})") # Uncomment for detailed scan output
                        else:
                            # Add to checked_real_paths even if version couldn't be determined
                            # to avoid re-checking the same non-Python executable
                            checked_real_paths.add(real_path)
    
    return found_pythons

def find_latest_python_executable():
    global_pythons = find_global_python_executables()
    
    if not global_pythons:
        print("\nNo global Python installations were found in your system's PATH.")
        print("Please ensure Python is installed and its directory is added to your PATH.")
        return None

    print("\n--- Found Global Python Installations ---")
    for path, version in global_pythons.items():
        print(f"  - {path} (Version: {version})")

    latest_stable_version_str = None
    latest_stable_version_tuple = (0, 0, 0)
    latest_stable_path = None

    # Filter for stable versions (no 'a', 'b', 'rc' in the version string)
    # And find the numerically highest among them
    for path, version_str in global_pythons.items():
        # Check if the version string contains any pre-release indicators
        if any(char in version_str for char in ['a', 'b', 'rc', 'dev']):
            # print(f"  Skipping pre-release/development version: {version_str}") # Uncomment to see skipped versions
            continue
        
        if "Houdini" in path:
            continue

        current_version_tuple = parse_version_string(version_str)
        
        if current_version_tuple > latest_stable_version_tuple:
            latest_stable_version_tuple = current_version_tuple
            latest_stable_version_str = version_str
            latest_stable_path = path

    print("\n--- Latest Stable Global Python Version ---")
    if latest_stable_version_str:
        print(f"The latest stable Python version found globally is:")
        print(f"  Version: {latest_stable_version_str}")
        print(f"  Path:    {latest_stable_path}")
        return latest_stable_path
    else:
        print("No stable Python versions were found in your global installations.")
        print("This might mean only pre-release or development versions are installed,")
        print("or no Python versions are found at all.")
        return None
    
import subprocess
import sys
import os

def find_suitable_python():
    """
    Attempts to find a suitable Python executable for creating virtual environments,
    prioritizing official python.org installations.
    """
    print("Searching for Python executables suitable for venv creation...\n")
    potential_paths = []

    # 1. Check current running Python
    current_python = sys.executable
    if "WindowsApps" not in current_python and "Houdini" not in current_python:
        potential_paths.append(("Current Python (likely good)", current_python))
    else:
        print(f"Warning: Current Python '{current_python}' is in a restricted or specific environment (WindowsApps/Houdini).")
        print("         It might not be ideal for creating virtual environments.\n")

    # 2. Check Python in PATH using 'where python' (Windows)
    try:
        result = subprocess.run(["where", "python"], capture_output=True, text=True, check=False, shell=True)
        if result.returncode == 0:
            found_paths = result.stdout.strip().split('\n')
            for path in found_paths:
                path = path.strip()
                if path:
                    if "WindowsApps" not in path and "Houdini" not in path:
                        potential_paths.append(("PATH (general)", path))
                    else:
                        print(f"Ignored: '{path}' (from WindowsApps or Houdini - likely problematic)")
        else:
            print("Could not run 'where python' or no Python found in PATH.")
    except FileNotFoundError:
        print("'where' command not found (this script is for Windows).")

    # 3. Common installation paths (explicit checks)
    common_install_bases = [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Python'),
        "C:\\Python", # common root for manual installs
        "C:\\Anaconda3", # Anaconda base
        "C:\\Miniconda3" # Miniconda base
    ]

    for base in common_install_bases:
        if os.path.exists(base):
            for item in os.listdir(base):
                full_path = os.path.join(base, item)
                if os.path.isdir(full_path):
                    python_exe = os.path.join(full_path, "python.exe")
                    if os.path.exists(python_exe):
                        if "WindowsApps" not in python_exe and "Houdini" not in python_exe:
                            potential_paths.append((f"Common Install ({os.path.basename(full_path)})", python_exe))
                        else:
                            print(f"Ignored: '{python_exe}' (from WindowsApps or Houdini directory)")

    # Filter for unique and sort for consistent output
    unique_paths = {}
    for desc, path in potential_paths:
        if path not in unique_paths:
            unique_paths[path] = desc
    
    sorted_unique_paths = sorted([(v, k) for k, v in unique_paths.items()])

    if not sorted_unique_paths:
        print("\nNo suitable Python executable found. Please install Python from python.org.")
        print("Ensure 'Add Python to PATH' is checked during installation.")
        return None

    print("\n--- Found Python Executables (prioritized for venv) ---")
    recommendation = None
    for desc, path in sorted_unique_paths:
        print(f"[{desc}]: {path}")
        # Prioritize non-Houdini/non-WindowsApps paths
        if "WindowsApps" not in path and "Houdini" not in path:
            if recommendation is None: # Take the first good one as recommendation
                recommendation = path

    if recommendation:
        print(f"\n--- Recommendation ---")
        print(f"Use this Python executable for creating your virtual environment:")
        print(f"'{recommendation}'")
        print("\nExample command to create a venv named 'myenv':")
        print(f'"{recommendation}" -m venv myenv')
    else:
        print("\nCould not find a clearly suitable Python. Consider installing Python from python.org.")
        print("Ensure 'Add Python to PATH' is checked during installation.")

    return recommendation