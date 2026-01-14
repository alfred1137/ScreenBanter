# Active Context: ScreenBanter

**Current Work Focus:** Completed standalone packaging infrastructure and CI/CD automation. The project is now ready for distribution via GitHub Actions.

**Recent Changes:**
- **Standalone Build Automation**: Implemented GitHub Actions workflow (`.github/workflows/build.yml`) for automated Windows `.exe` generation.
- **Build Script Optimization**: Refactored `build_release.py` to use `sys.executable`, include `customtkinter` dependencies, and handle CI environments (added `--assume-yes-for-downloads`).
- **CI/CD Integration**: Configured workflow to run on tags (`v*`) or manual dispatch, uploading a portable ZIP artifact.
- **Packaging Documentation**: Added instructions for local and CI-based builds to the README and Memory Bank.

**Next Steps:**
1.  **Tag and Release**: Create a Git tag (e.g., `v1.0.0`) to trigger the first automated production build.
2.  **User Acceptance**: Download the CI artifact and verify functionality on a fresh machine (ensure `.env` setup is clear).

**Active Decisions and Considerations:**
- **Portable Folder vs. Onefile**: Decided to stick with a portable folder (standalone) zipped into an archive. This avoids the massive startup delay (20s+) associated with extracting a 2GB `onefile` executable containing `torch`.
- **Model Inclusion**: The build script copies the `models/` directory into the final bundle. Since models are currently tracked in Git, the CI build will include them automatically.
- **Environment Isolation**: Used `sys.executable` in the build script to ensure Nuitka uses the same `uv` virtual environment it was launched from.
