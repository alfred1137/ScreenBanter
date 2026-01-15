# Active Context: ScreenBanter

**Current Work Focus:** Optimizing TTS performance for high-load gaming environments. Addressing audio throttling issues through quantization and process prioritization.

**Recent Changes:**
- **Standalone Build Automation**: Implemented GitHub Actions workflow (`.github/workflows/build.yml`) for automated Windows `.exe` generation.
- **Build Script Optimization**: Refactored `build_release.py` to use `sys.executable`, include `customtkinter` dependencies, and handle CI environments (added `--assume-yes-for-downloads`).
- **CI/CD Integration**: Configured workflow to run on tags (`v*`) or manual dispatch, uploading a portable ZIP artifact.
- **Packaging Documentation**: Added instructions for local and CI-based builds to the README and Memory Bank.

**Next Steps:**
1.  **Dependency Update**: Add `bitsandbytes` to support 4-bit quantization.
2.  **Model Optimization**: Update `model_loader.py` to support `load_in_4bit=True` and FP16 loading for efficient RTX usage.
3.  **Process Priority**: Implement startup logic in `tts_server.py` to set Windows process priority to `HIGH_PRIORITY_CLASS`.
4.  **Verification**: Benchmark startup and audio stability under load.

**Active Decisions and Considerations:**
- **Quantization Strategy**: Adopting 4-bit quantization (via `bitsandbytes`) to drastically reduce VRAM usage (<500MB), preventing contention with VRAM-heavy games.
- **Priority Boosting**: Using OS-level priority boosts to prevent the Windows Scheduler from throttling the background TTS process during full-screen gaming.
- **Portable Folder vs. Onefile**: Decided to stick with a portable folder (standalone) zipped into an archive. This avoids the massive startup delay (20s+) associated with extracting a 2GB `onefile` executable containing `torch`.
- **Model Inclusion**: The build script copies the `models/` directory into the final bundle. Since models are currently tracked in Git, the CI build will include them automatically.
- **Environment Isolation**: Used `sys.executable` in the build script to ensure Nuitka uses the same `uv` virtual environment it was launched from.
