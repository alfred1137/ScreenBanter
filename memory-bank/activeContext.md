# Active Context: ScreenBanter

**Current Work Focus:** Maintenance and user feedback. The core application is stable and fully functional.

**Recent Changes:**
- **Stability Improvements**:
    - Increased TTS client timeout to 45s to prevent disconnects during model warm-up.
    - Added comprehensive logging to `server/model_loader.py` and `app/audio_client.py`.
    - Refactored `app/main.py` to seamlessly detect and use existing TTS server instances.
    - Fixed startup sound cutoff by running it in a daemon thread.
- **Feature Completion**:
    - Validated multi-screenshot workflow (F10 to queue, F11 to process).
    - Confirmed capture sound feedback.
    - Verified OCR logging.

**Next Steps:**
1.  **Monitor Usage**: Gather feedback on the "missing tray icon" issue if it persists or becomes a blocker.
2.  **Performance Tuning**: Optionally investigate faster VibeVoice loading or keeping the model "hot" if latency becomes an issue.
3.  **Packaging**: Consider Nuitka for a standalone executable if distribution is required.

**Active Decisions and Considerations:**
- **Timeout vs. Performance**: The 45s timeout is a safety net. The underlying "slowness" is inherent to running a 0.5B model on the available hardware during the first run. Subsequent runs are faster.
- **Icon Visibility**: Deemed non-critical for now as hotkeys provide full control.

**Learnings and Project Insights:**
- **Model Warm-up**: Generative AI models (like VibeVoice) have a significant "first-token-latency" that must be accounted for in client timeouts.
- **Process Management**: Robust apps should check for existing server instances rather than blindly spawning new ones.
- **Threading**: Audio playback in UI apps (even simple tray ones) must be carefully threaded to avoid blocking the main loop or being killed prematurely.