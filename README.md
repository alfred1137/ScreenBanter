<!-- Based on https://github.com/othneildrew/Best-README-Template/ -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS & BUILT WITH ICONS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
  <p style="text-align: center;">
    <a href="https://github.com/alfred1137/ScreenBanter/network/members"><img src="https://img.shields.io/github/forks/alfred1137/ScreenBanter.svg?style=for-the-badge" alt="Forks"></a>
    <a href="https://github.com/alfred1137/ScreenBanter/stargazers"><img src="https://img.shields.io/github/stars/alfred1137/ScreenBanter.svg?style=for-the-badge" alt="Stargazers"></a>
    <a href="https://github.com/alfred1137/ScreenBanter/issues"><img src="https://img.shields.io/github/issues/alfred1137/ScreenBanter.svg?style=for-the-badge" alt="Issues"></a>
    <a href="https://github.com/alfred1137/ScreenBanter/blob/master/LICENSE"><img src="https://img.shields.io/github/license/alfred1137/ScreenBanter.svg?style=for-the-badge" alt="MIT License"></a>
  </p>
  <!-- Built With Icons integrated here to save space -->
  <p style="text-align: center;">
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python"></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI"></a>
    <a href="https://pytorch.org/"><img src="https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white" alt="PyTorch"></a>
    <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/badge/uv-managed-green?style=for-the-badge" alt="UV"></a>
    <a href="https://deepmind.google/technologies/gemini/"><img src="https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google%20gemini&logoColor=white" alt="Google Gemini"></a>
  </p>

> [!WARNING]
> This is an ongoing personal project currently in active development. Features are subject to change.


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/alfred1137/ScreenBanter">
    <img src="assets/icon.svg" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">ScreenBanter</h3>

  <p align="center">
    Make your screen talk back. Real-time AI desktop narration.
    <br />
    <br />
    <a href="https://github.com/alfred1137/ScreenBanter/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/alfred1137/ScreenBanter/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#overview">📖 Overview</a></li>
    <li><a href="#features">✨ Features</a></li>
    <li><a href="#technologies">📦 Technologies</a></li>
    <li>
      <a href="#installation-setup">🚀 Installation & Setup</a>
      <ul>
        <li><a href="#requirements">✅ Requirements</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">🛠️ Usage</a></li>
    <li><a href="#configuration">🔧 Configuration</a></li>
    <li><a href="#repository-structure">🗂️ Repository Structure</a></li>
    <li><a href="#flow-chart">🔗 Flow Chart</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">🤝 Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">❤️ Acknowledgements</a></li>
    <li><a href="#changelog">📝 Changelog</a></li>
  </ol>
</details>

<!-- OVERVIEW -->
<a id="overview"></a>
## 📖 Overview

ScreenBanter is an amateur project that marries **Google’s Gemini Vision** (for high-speed OCR) and the new **Gemini 2.5 Flash Preview TTS** (for cloud audio) to provide real-time desktop narration. 

**New in v0.3.0:** The application is now distributed as a lightweight **Lite Client** (~100MB) with Cloud TTS support out-of-the-box. Local neural TTS (via **Microsoft VibeVoice-0.5B**) is fully supported through a **"Bring Your Own Engine" (BYOE)** model, allowing power users to host their own inference server.

### 🌟 Key Features
*   **Cloud TTS (Default):** High-quality, low-latency narration using **Gemini 2.5 Flash Preview** (`gemini-2.5-flash-preview-tts`) with 30+ native voices. Zero local GPU load.
*   **Local TTS (BYOE):** Connect to your own local **VibeVoice** instance for private, offline, neural speech generation.
*   **Smart Vision:** Uses **Gemini 2.5 Flash Lite** (`models/gemini-flash-lite-latest`) via Gemini API for intelligent text extraction and context-aware merging of multiple screenshots.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- INSTALLATION & SETUP -->
<a id="installation-setup"></a>
## 🚀 Installation & Setup

### 📥 Download (Lite Client)
The easiest way to use ScreenBanter is to download the latest pre-compiled build:
1. Go to the **[GitHub Actions](https://github.com/alfred1137/ScreenBanter/actions)** tab.
2. Select the latest successful **"Build Windows Executable"** run.
3. Scroll down to **Artifacts** and download `ScreenBanter_Windows_Executable`.
4. Extract the ZIP, create a `.env` file with your `GEMINI_KEY`, and run `ScreenBanter.exe`.

### ✅ Requirements

**Lite Client (Cloud Only)**
*   **OS:** Windows 10/11 (Required for `DXcam` and Win32 tray integration).
*   **Internet:** Active connection for Gemini API.

**Local TTS Engine (Optional)**
*   **GPU:** NVIDIA GPU with CUDA 12.1 support (RTX 3060+ recommended).
*   **Python:** 3.10+ installed.
*   **Git:** Installed.

### Installation (Source)

1.  **Clone the Repository**
    ```sh
    git clone https://github.com/alfred1137/ScreenBanter.git
    cd ScreenBanter
    ```

2.  **Setup Environment Variables**
    Create a `.env` file from the example:
    ```sh
    cp .env.example .env
    ```
    Edit `.env` and add your **GEMINI_KEY** from [Google AI Studio](https://aistudio.google.com/).

3.  **Install Dependencies (Lite)**
    Using `uv`:
    ```sh
    uv sync
    ```

4.  **Optional: Setup Local TTS**
    To use VibeVoice locally, follow the **[Local TTS Setup Guide](docs/setup_local_tts.md)**.
    
    *If developing locally:*
    ```sh
    uv sync --extra local-tts
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->
<a id="usage"></a>
## 🛠️ Usage

**1. Launch the Application**
Starts the system tray app.
```sh
uv run python -m app.main
```
*Wait for the announcement: "ScreenBanter is active."*

**2. Controls (Default Hotkeys)**

| Hotkey | Action | Description |
| :--- | :--- | :--- |
| **`Ctrl + Alt + S`** | **Instant Capture** | Narrates the current screen/region immediately. |
| **`F10`** | **Queue Screenshot** | Adds current view to buffer (confirmed by a beep). |
| **`F11`** | **Process Queue** | Merges all queued captures and narrating the result. |

**3. Banter HUD**
ScreenBanter features a non-intrusive **HUD** that appears automatically during operation:
- **Scanning:** Indicates Gemini is analyzing the screen.
- **Thinking:** Displays the extracted text for verification.
- **Speaking:** Shows playback status.
*The HUD is "click-through" and will not steal focus from your active game.*

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONFIGURATION -->
<a id="configuration"></a>
## 🔧 Configuration

Access settings by right-clicking the **Loudspeaker icon** in the system tray.

*   **Hotkeys:** Rebind any action to your preferred key combinations.
*   **Audio:** 
    *   **Cloud:** Select Gemini Model and Voice (e.g., `Puck`, `Kore`).
    *   **Local:** Configure external engine path and select VibeVoice presets.
*   **Capture Mode:** Toggle between `Fullscreen` and `Region`. In Region mode, use the interactive selector to define your capture area.
*   **HUD / UI:** Toggle the Banter HUD, adjust opacity, and configure focus behavior (Immersive vs. Focus mode).
*   **Performance:** Configure "Process Priority" and "Playback Buffer" to optimize for your hardware.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- REPOSITORY STRUCTURE -->
<a id="repository-structure"></a>
## 🗂️ Repository Structure

```
ScreenBanter/
├── app/                  # Frontend Daemon & GUI
│   ├── main.py           # Application entry & Tray management
│   ├── capture.py        # DXcam screen capture logic
│   ├── vision.py         # Gemini API integration
│   ├── audio_client.py   # Threaded PyAudio playback
│   ├── settings.py       # Configuration management
│   ├── settings_window.py# CustomTkinter Settings GUI
│   └── region_selector.py# Transparent overlay for region selection
├── server/               # Local Inference Server Logic
│   ├── tts_server.py     # FastAPI application (for local dev/BYOE)
│   └── model_loader.py   # VibeVoice initialization
├── docs/                 # Documentation
│   └── setup_local_tts.md# Guide for external engine setup
├── third_party/          # VibeVoice source code (submodule)
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- FLOW CHART -->
<a id="flow-chart"></a>
## 🔗 Flow Chart

```mermaid
graph TD
    User[User] -->|Hotkey| Trigger[Capture Trigger]
    Trigger -->|DXcam| Capture[Screen/Region Capture]
    Capture -->|Image Data| Vision[Gemini Vision Engine]
    Vision -->|Extracted Text| Client[Audio Client]
    
    Client -->|Option A: API| Cloud[Gemini Cloud TTS]
    Client -->|Option B: Subprocess| Local[External VibeVoice Server]
    
    Cloud -->|Audio Bytes| Playback[PyAudio Stream]
    Local -->|Audio Bytes| Playback
    
    Playback -->|Sound| Speakers[User Speakers]
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
<a id="roadmap"></a>
## Roadmap

- [x] Instant Narration
- [x] Batch Mode (Queueing)
- [x] Custom Region Capture
- [x] Settings GUI (Modern UI)
- [x] Local Neural TTS Integration (BYOE)
- [x] Cloud TTS (Gemini) Integration
- [x] Dynamic Voice/Device Selection
- [x] Standalone "Lite" Client Build

See the [open issues](https://github.com/alfred1137/ScreenBanter/issues) for a full list of proposed features.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
<a id="contributing"></a>
## 🤝 Contributing

Contributions are welcome! If you have suggestions or bug fixes:

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

*Note: As an amateur project, PR reviews might take some time!*

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
<a id="license"></a>
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
<a id="contact"></a>
## Contact

Alfred T - [GitHub Profile](https://github.com/alfred1137)

Project Link: [https://github.com/alfred1137/ScreenBanter](https://github.com/alfred1137/ScreenBanter)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
<a id="acknowledgments"></a>
## ❤️ Acknowledgements

* [Microsoft/VibeVoice](https://github.com/microsoft/VibeVoice) - Exceptional local TTS.
* [Google Gemini Vision](https://deepmind.google/technologies/gemini/) - High-speed multi-modal OCR.
* [DXcam](https://github.com/ra1nty/DXcam) - Ultra-fast Windows screen capture.
* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modernizing Python GUIs.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CHANGELOG -->
<a id="changelog"></a>
## 📝 Changelog

*   **2026-01-25**: Fixed build dependencies and migrated to **PyInstaller** for CI stability. (v0.3.5)
*   **2026-01-24**: Refactored to **Lite Client** architecture (v0.3.0).
*   **2026-01-20**: Verified full integration workflow (HUD, 4-bit TTS, Region Capture) on Windows 11 with CUDA 12.1.
*   **2026-01-16**: Added **Performance Mode** (4-bit quantization, priority boosting) and **Banter HUD** for seamless gaming integration.
*   **2026-01-14**: Enhanced documentation, added Region Capture and Settings GUI polish.
*   **2026-01-10**: Implemented Settings GUI and dynamic configuration infrastructure.
*   **2026-01-05**: Initial MVP release with Gemini OCR and VibeVoice TTS integration.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[forks-shield]: https://img.shields.io/github/forks/alfred1137/ScreenBanter.svg?style=for-the-badge
[forks-url]: https://github.com/alfred1137/ScreenBanter/network/members
[stars-shield]: https://img.shields.io/github/stars/alfred1137/ScreenBanter.svg?style=for-the-badge
[stars-url]: https://github.com/alfred1137/ScreenBanter/stargazers
[issues-shield]: https://img.shields.io/github/issues/alfred1137/ScreenBanter.svg?style=for-the-badge
[issues-url]: https://github.com/alfred1137/ScreenBanter/issues
[license-shield]: https://img.shields.io/github/license/alfred1137/ScreenBanter.svg?style=for-the-badge
[license-url]: https://github.com/alfred1137/ScreenBanter/blob/master/LICENSE
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
[FastAPI]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/
[PyTorch]: https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white
[PyTorch-url]: https://pytorch.org/
[UV]: https://img.shields.io/badge/uv-managed-green?style=for-the-badge
[UV-url]: https://github.com/astral-sh/uv
[Gemini]: https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google%20gemini&logoColor=white
[Gemini-url]: https://deepmind.google/technologies/gemini/
