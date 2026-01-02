# Product Context: ScreenBanter

**Problem Solved:** Traditional screen readers can be cumbersome and not ideal for quick, on-demand narration of specific on-screen text. There's a need for a lightweight, fast, and user-friendly tool to get immediate audio feedback from visual information.

**How it Should Work:**
1. User presses a predefined hotkey (e.g., Ctrl + Alt + S).
2. The system instantly captures the screen content.
3. The captured image is sent to Google Gemini Vision for precise text extraction (OCR).
4. The extracted text is then sent to a local VibeVoice-0.5B server.
5. The VibeVoice server streams audio chunks back to the client.
6. The client plays these audio chunks in real-time, providing smooth, continuous narration as it's generated.

**User Experience Goals:**
- **Instantaneous Feedback:** Near real-time audio response after hotkey activation.
- **Smooth Audio Playback:** No noticeable pauses or interruptions during narration.
- **Minimal Resource Usage:** Run efficiently in the background without significantly impacting system performance.
- **Simple Operation:** Easy to activate and minimal configuration required.
