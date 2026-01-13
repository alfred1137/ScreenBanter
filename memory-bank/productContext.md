# Product Context: ScreenBanter

**Problem Solved:** Traditional screen readers can be cumbersome and not ideal for quick, on-demand narration of specific on-screen text. There's a need for a lightweight, fast, and user-friendly tool to get immediate audio feedback from visual information.

**How it Should Work:**
1.  **Instant Mode:**
    - User presses `Ctrl + Alt + S`.
    - System instantly captures the screen, performs OCR via Gemini, and streams narration via VibeVoice.
2.  **Queue Mode (Multi-Page/Window):**
    - User presses `F10` to capture the current view. A short beep confirms the capture.
    - User navigates to the next page or window and presses `F10` again.
    - User presses `F11` to process the queue.
    - System sends all captured images to Gemini, which intelligently merges the text into a cohesive narrative, then streams the audio.

**User Experience Goals:**
- **Instantaneous Feedback:** Near real-time audio response after hotkey activation.
- **Smooth Audio Playback:** No noticeable pauses or interruptions during narration.
- **Minimal Resource Usage:** Run efficiently in the background without significantly impacting system performance.
- **Simple Operation:** Easy to activate and minimal configuration required.
- **Feedback:** Audio cues (beeps/speech) confirm actions to the user without needing visual checks.