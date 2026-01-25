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

    # Setup environment
    env = os.environ.copy()

    print(">>> Configuring Standalone Build (PyInstaller)...")
    
    # Run PyInstaller
    pyi_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "ScreenBanter.spec"
    ]
    
    print("Starting PyInstaller build...")
    run_command(pyi_cmd, env=env)
    
    # Post-build: Management
    build_output_dir = os.path.join(dist_dir, "ScreenBanter")
    if not os.path.exists(build_output_dir):
        print(f"Could not locate build output directory: {build_output_dir}")
        sys.exit(1)
        
    # Copy .env example if not already handled by spec datas (spec handles it but let's be sure)
    env_target = os.path.join(build_output_dir, ".env")
    if not os.path.exists(env_target):
        print("Copying configuration...")
        shutil.copy(os.path.join(project_root, ".env.example"), env_target)

    # Rename the folder to include version
    with open(os.path.join(project_root, "pyproject.toml"), "rb") as f:
        pyproject = tomllib.load(f)
    version = pyproject.get("project", {}).get("version", "0.1.0")
    
    final_folder_name = f"ScreenBanter_v{version}"
    final_output = os.path.join(dist_dir, final_folder_name)
    
    if os.path.exists(final_output):
        print(f"Cleaning existing final output folder: {final_output}")
        shutil.rmtree(final_output)
        
    print(f"Renaming {build_output_dir} to {final_output}")
    os.rename(build_output_dir, final_output)
    
    print(f"\nBuild Complete! Output: {final_output}")

if __name__ == "__main__":
    build()
