# Setting Up Local TTS (VibeVoice)

ScreenBanter v0.3.0+ adopts a "Bring Your Own Engine" (BYOE) model for local text-to-speech. This allows the main application to remain lightweight while giving power users the flexibility to host the high-quality VibeVoice model locally.

## Prerequisites

- **NVIDIA GPU**: RTX 3060 or better recommended (4GB+ VRAM).
- **Python 3.10+**: Installed and added to PATH.
- **Git**: Installed.

## Step 1: Get the Engine

You can either clone the ScreenBanter repository recursively or set up a standalone environment.

### Option A: Clone the Repository (Recommended for Developers)

```bash
git clone --recursive https://github.com/alfred1137/ScreenBanter.git
cd ScreenBanter
```

### Option B: Manual Setup

1. Create a folder named `ScreenBanterEngine`.
2. Clone the VibeVoice repository into `third_party/VibeVoice`.
3. Download the model weights.

## Step 2: Install Dependencies

We recommend using `uv` for fast environment management, but `pip` works too.

```bash
# Install uv (optional)
pip install uv

# Create a virtual environment
uv venv
# OR: python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install Server Dependencies
# (You can copy requirements from the ScreenBanter repo or install manually)
pip install fastapi uvicorn torch transformers accelerate soundfile librosa termcolor
# Install VibeVoice dependencies (check third_party/VibeVoice/requirements.txt if available)
```

## Step 3: Configure ScreenBanter

1. Open **ScreenBanter**.
2. Go to **Settings > Audio**.
3. Set **TTS Provider** to `Local`.
4. In the **External Engine Path** field, click **Browse**.
5. Select the `python.exe` inside your virtual environment (e.g., `C:\Path\To\ScreenBanter\.venv\Scripts\python.exe`).
   - *Alternatively, you can select a `.bat` script that launches the server.*

## Step 4: Verify

1. Restart ScreenBanter (or just the backend initialization happens automatically).
2. The HUD should show "TTS Server ready!" in the console logs (if visible) or the application status.
3. If successful, you will see your local voices populated in the "Local Voice Preset" dropdown.

## Troubleshooting

- **Server fails to start**: Check `logs/server_stderr.log` in your ScreenBanter folder.
- **Missing Dependencies**: Ensure you installed `fastapi` and `uvicorn` in the selected environment.
- **GPU Issues**: Ensure you have the correct CUDA version of PyTorch installed for your GPU.
