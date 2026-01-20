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

    # Parse arguments

    is_lite = "--lite" in sys.argv

    version_suffix = "Lite" if is_lite else "Full"

    

    # Define paths

    project_root = os.path.dirname(os.path.abspath(__file__))

    dist_dir = os.path.join(project_root, "dist")

    

            # Clean previous build (Specific to this version)

    

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

    vibevoice_repo_path = os.path.join(project_root, "third_party", "VibeVoice")

    if os.path.exists(vibevoice_repo_path) and not is_lite:

        env["PYTHONPATH"] = vibevoice_repo_path + os.pathsep + env.get("PYTHONPATH", "")

        print(f"Added to PYTHONPATH: {vibevoice_repo_path}")



    # Nuitka arguments

    nuitka_cmd = [

        sys.executable, "-m", "nuitka",

        "--standalone",

        "--assume-yes-for-downloads",

        "--jobs=1",

        "--python-flag=no_site",

        

        # Plugins

        "--enable-plugin=tk-inter",

        

                # Core packages (Always included)

        

                "--include-package=pystray",

        

                "--include-package=PIL",

        

                "--include-package=numpy",

        

                "--include-package=customtkinter",

        

                "--include-package=darkdetect",

        

                "--include-package=dxcam",

        

                "--include-package=google",

        

                "--include-package=requests",

        

                "--include-package=pyaudio",

        

        # Application packages

        "--include-package=app",

        

        # Data files

        "--include-data-dir=assets=assets",

        

        # Output

        "--output-dir=dist",

        "--output-filename=ScreenBanter.exe",

        

        # Main entry point

        "app/main.py"

    ]



        # Add Heavy Dependencies ONLY for Full version



        if not is_lite:



            print(">>> Configuring FULL build with Local TTS support...")



            nuitka_cmd.extend([



                "--include-package=uvicorn",



                "--include-package=fastapi",



                "--enable-plugin=torch",



                "--include-package=torch",



                "--include-package=transformers",



                "--include-package=huggingface_hub",



                "--include-package=accelerate",



                "--include-package=av",



                "--include-package=soundfile",



                "--include-package=server", # Only need server in Full



                "--include-package=vibevoice",



                # Include VibeVoice voice presets



                "--include-data-dir=third_party/VibeVoice/demo/voices=third_party/VibeVoice/demo/voices",



            ])

    else:

        print(">>> Configuring LITE build (Cloud TTS only)...")



    # Handle Icon

 if it exists as .ico (Nuitka requirement)
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
    
    # Copy Models (ONLY for Full)
    if not is_lite:
        print("Copying local models...")
        src_models = os.path.join(project_root, "models")
        dst_models = os.path.join(build_output_dir, "models")
        if os.path.exists(src_models):
            if os.path.exists(dst_models):
                shutil.rmtree(dst_models)
            shutil.copytree(src_models, dst_models)
    
    # Copy .env example
    print("Copying configuration...")
    shutil.copy(os.path.join(project_root, ".env.example"), os.path.join(build_output_dir, ".env"))

    # Rename the folder
    import tomllib
    with open(os.path.join(project_root, "pyproject.toml"), "rb") as f:
        pyproject = tomllib.load(f)
    version = pyproject.get("project", {}).get("version", "0.1.0")
    
    final_folder_name = f"ScreenBanter_{version_suffix}_v{version}"
    final_output = os.path.join(dist_dir, final_folder_name)
    if os.path.exists(final_output):
        shutil.rmtree(final_output)
    os.rename(build_output_dir, final_output)
    
    print(f"\n{version_suffix} Build Complete! Output: {final_output}")

if __name__ == "__main__":
    build()
