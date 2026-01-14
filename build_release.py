import os
import subprocess
import shutil
import sys

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
    
    # Clean previous build
    if os.path.exists(dist_dir):
        print("Cleaning previous build...")
        try:
            shutil.rmtree(dist_dir)
        except Exception as e:
            print(f"Warning: Could not clean dist directory: {e}")
    
    # Setup environment
    env = os.environ.copy()
    # Add VibeVoice to PYTHONPATH so Nuitka can find the 'vibevoice' package
    vibevoice_repo_path = os.path.join(project_root, "third_party", "VibeVoice")
    if os.path.exists(vibevoice_repo_path):
        env["PYTHONPATH"] = vibevoice_repo_path + os.pathsep + env.get("PYTHONPATH", "")
        print(f"Added to PYTHONPATH: {vibevoice_repo_path}")

    # Nuitka arguments
    nuitka_cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--assume-yes-for-downloads", # Avoid hanging in CI
        "--python-flag=no_site",      # Don't use system site-packages
        
        # Plugins
        "--enable-plugin=tk-inter",   # Required for customtkinter
        "--enable-plugin=torch",      # Highly recommended for torch-based apps
        
        # Core packages
        "--include-package=uvicorn",
        "--include-package=fastapi",
        "--include-package=pystray",
        "--include-package=PIL",
        "--include-package=numpy",
        "--include-package=torch",
        "--include-package=transformers",
        "--include-package=customtkinter",
        "--include-package=darkdetect", # Needed by customtkinter
        "--include-package=dxcam",
        "--include-package=google",
        "--include-package=huggingface_hub",
                "--include-package=accelerate",
                "--include-package=av",
                "--include-package=soundfile",
                "--include-package=pyaudio",
                
                # Application packages
        "--include-package=app",
        "--include-package=server",
        
        # Third party
        "--include-package=vibevoice",
        
        # Data files
        "--include-data-dir=assets=assets",
        # Include VibeVoice voice presets as data
        "--include-data-dir=third_party/VibeVoice/demo/voices=third_party/VibeVoice/demo/voices",
        
        # Output
        "--output-dir=dist",
        "--output-filename=ScreenBanter.exe",
        
        # Main entry point
        "app/main.py"
    ]

    # Handle Icon if it exists as .ico (Nuitka requirement)
    icon_path = os.path.join(project_root, "assets", "icon.ico")
    if os.path.exists(icon_path):
        nuitka_cmd.append(f"--windows-icon-from-ico={icon_path}")

    print("Starting Nuitka build... This may take a while (20-40 minutes).")
    run_command(nuitka_cmd, env=env)
    
    # Post-build: Copy external resources
    # Nuitka 2.x creates a folder ending in .dist
    possible_dirs = [d for d in os.listdir(dist_dir) if d.endswith(".dist")]
    if not possible_dirs:
        print("Could not locate build output directory.")
        sys.exit(1)
        
    build_output_dir = os.path.join(dist_dir, possible_dirs[0])
    print(f"Build located at: {build_output_dir}")
    
    # Copy Models
    print("Copying models...")
    src_models = os.path.join(project_root, "models")
    dst_models = os.path.join(build_output_dir, "models")
    if os.path.exists(src_models):
        if os.path.exists(dst_models):
            shutil.rmtree(dst_models)
        shutil.copytree(src_models, dst_models)
    else:
        print("WARNING: models directory not found.")

    # Copy .env example
    print("Copying configuration...")
    shutil.copy(os.path.join(project_root, ".env.example"), os.path.join(build_output_dir, ".env"))

    # Rename the folder to ScreenBanter
    final_output = os.path.join(dist_dir, "ScreenBanter_v1.0")
    if os.path.exists(final_output):
        shutil.rmtree(final_output)
    os.rename(build_output_dir, final_output)
    
    print(f"\nBuild Complete! Output available at: {final_output}")

if __name__ == "__main__":
    build()
