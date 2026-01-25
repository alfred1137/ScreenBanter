import os
import subprocess
import shutil
import sys
import tomllib

def run_command(command, env=None):
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.check_call(command, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error building: {e}")
        sys.exit(1)

def build():
    # Define paths
    project_root = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_root, "dist")

    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)

    # Nuitka creates a .dist folder. 
    # With --output-filename=ScreenBanter.exe, it usually creates ScreenBanter.dist
    target_dist_folder = os.path.join(dist_dir, "ScreenBanter.dist")
    if os.path.exists(target_dist_folder):
        print(f"Cleaning previous temporary build folder: {target_dist_folder}")
        shutil.rmtree(target_dist_folder)

    # Setup environment
    env = os.environ.copy()
    # Fix for C1002: compiler is out of heap space. 
    # Increase MSVC compiler heap space.
    env["_CL_"] = "/Zm2000"

    # Nuitka arguments
    nuitka_cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--assume-yes-for-downloads",
        "--jobs=1",
        "--python-flag=no_site",
        "--low-memory",
        # Plugins
        "--enable-plugin=tk-inter",
        "--enable-plugin=numpy",
        # Core packages (Let Nuitka follow these instead of forcing full compilation if possible)
        "--include-package=pystray",
        "--include-package=PIL",
        "--include-package=customtkinter",
        "--include-package=darkdetect",
        "--include-package=dxcam",
        "--include-package=requests",
        "--include-package=pyaudio",
        # Application packages
        "--include-package=app",
        # Specifically exclude full 'google' package to avoid C1002
        # Nuitka will follow imports into google.genai naturally.
        "--follow-imports",
        # Data files
        "--include-data-dir=assets=assets",
        # Output
        "--output-dir=dist",
        "--output-filename=ScreenBanter.exe",
        # Main entry point
        "app/main.py"
    ]

    print(">>> Configuring Standalone Build (Cloud TTS / External Server)...")

    # Handle Icon if it exists as .ico (Nuitka requirement)
    icon_path = os.path.join(project_root, "assets", "icon.ico")
    if os.path.exists(icon_path):
        nuitka_cmd.append(f"--windows-icon-from-ico={icon_path}")

    print("Starting Nuitka build... This may take a while (20-40 minutes).")
    run_command(nuitka_cmd, env=env)
    
    # Post-build: Copy external resources
    possible_dirs = [d for d in os.listdir(dist_dir) if d.endswith(".dist")]
    if not possible_dirs:
        print("Could not locate build output directory.")
        sys.exit(1)
        
    build_output_dir = os.path.join(dist_dir, possible_dirs[0])
    
    # Copy .env example
    print("Copying configuration...")
    shutil.copy(os.path.join(project_root, ".env.example"), os.path.join(build_output_dir, ".env"))

    # Rename the folder
    with open(os.path.join(project_root, "pyproject.toml"), "rb") as f:
        pyproject = tomllib.load(f)
    version = pyproject.get("project", {}).get("version", "0.1.0")
    
    final_folder_name = f"ScreenBanter_v{version}"
    final_output = os.path.join(dist_dir, final_folder_name)
    if os.path.exists(final_output):
        shutil.rmtree(final_output)
    os.rename(build_output_dir, final_output)
    
    print(f"\nBuild Complete! Output: {final_output}")

if __name__ == "__main__":
    build()