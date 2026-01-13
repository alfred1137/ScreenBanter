import os
import subprocess
import shutil
import sys

def run_command(command):
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        print(f"Error building: {e}")
        sys.exit(1)

def build():
    # Define paths
    project_root = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_root, "dist")
    output_dir = os.path.join(dist_dir, "ScreenBanter")
    
    # Clean previous build
    if os.path.exists(dist_dir):
        print("Cleaning previous build...")
        shutil.rmtree(dist_dir)
    
    # Nuitka arguments
    nuitka_cmd = [
        "uv", "run", "python", "-m", "nuitka",
        "--standalone",
        "--python-flag=no_site",  # Don't use system site-packages
        "--include-package=uvicorn",
        "--include-package=fastapi",
        "--include-package=pystray",
        "--include-package=PIL",
        "--include-package=numpy",
        "--include-package=torch",
        "--include-package=transformers",
        "--include-package=engineio.async_drivers.aiohttp", # Common uvicorn missing dependency
        
        # Data files
        "--include-data-dir=assets=assets",
        
        # GUI/Icon
        "--windows-icon-from-ico=assets/icon.png",
        
        # Output
        "--output-dir=dist",
        "--output-filename=ScreenBanter.exe",
        
        # Main entry point
        "app/main.py"
    ]

    print("Starting Nuitka build... This may take a while.")
    run_command(nuitka_cmd)
    
    # Post-build: Copy external resources that are too big or dynamic to bundle
    # The output directory for standalone is usually dist/app.main.dist or dist/ScreenBanter.dist
    # Nuitka naming can be tricky, let's find it.
    
    build_output_dir = os.path.join(dist_dir, "app.main.dist")
    if not os.path.exists(build_output_dir):
        # Fallback check
        possible_dirs = [d for d in os.listdir(dist_dir) if d.endswith(".dist")]
        if possible_dirs:
            build_output_dir = os.path.join(dist_dir, possible_dirs[0])
        else:
            print("Could not locate build output directory.")
            sys.exit(1)
            
    print(f"Build located at: {build_output_dir}")
    
    # Copy Models
    print("Copying models...")
    src_models = os.path.join(project_root, "models")
    dst_models = os.path.join(build_output_dir, "models")
    if os.path.exists(src_models):
        shutil.copytree(src_models, dst_models)
    else:
        print("WARNING: models directory not found. User will need to provide it.")

    # Copy .env example
    print("Copying configuration...")
    shutil.copy(os.path.join(project_root, ".env.example"), os.path.join(build_output_dir, ".env"))

    # Rename the folder to ScreenBanter
    final_output = os.path.join(dist_dir, "ScreenBanter_v1.0")
    os.rename(build_output_dir, final_output)
    
    print(f"\nBuild Complete! Output available at: {final_output}")
    print("Note: You may need to create a .env file in that directory with your GEMINI_API_KEY.")

if __name__ == "__main__":
    build()
