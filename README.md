<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/alfred1137/ScreenBanter">
    <img src="assets/icon.svg" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">ScreenBanter</h3>

  <p align="center">
    Make your screen talk back.
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
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

- *Placeholder for screenshot*

ScreenBanter is a amateur project that bridges **Google’s Gemini Vision** (for OCR) with **Microsoft’s VibeVoice-0.5B** (for local TTS) to provide desktop narration. It features instant capture-to-speech and a multi-screenshot queuing system.

<details>
<summary>Click to the story behind the project idea...</summary>
<br />
    <p>
    The idea for this project emerged when I was playing a story-heavy turn-based RPG game called <strong>Battle Brothers</strong>. As a non-native speaker of English I occasionally struggle to maintain focus on the wall of text during game play (e.g. events, encounters, quests). I tried using the Windows build-in narrator but the result was underwhelming.
    </p>
    <p>
    On a random day, I came across the <a href="https://github.com/microsoft/VibeVoice/blob/main/docs/vibevoice-realtime-0.5b.md"><strong>Microsoft’s VibeVoice-0.5B</strong></a> project. It has a colab demo that was so lightweight that you can run in a browser. Then birth this project.
    </p>
</details>

### Built With

* [![Python][Python]][Python-url]
* [![FastAPI][FastAPI]][FastAPI-url]
* [![PyTorch][PyTorch]][PyTorch-url]
* [![UV][UV]][UV-url]
* [![Google Gemini][Gemini]][Gemini-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

*   **OS:** Windows 10/11 (Required for `DXcam`).
*   **GPU:** NVIDIA GPU with CUDA support (Recommended for VibeVoice latency).
*   **Build Tools:** [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (Required for `pyaudio` and `pystray`).
*   **Package Manager:** [uv](https://github.com/astral-sh/uv) (Recommended).

### Installation

1.  **Clone the Repository**
    ```sh
    git clone https://github.com/alfred1137/ScreenBanter.git
    cd ScreenBanter
    ```

2.  **Setup Environment**
    Create a `.env` file from the example:
    ```sh
    cp .env.example .env
    ```
    Edit `.env` and add your **GEMINI_KEY**.

3.  **Install Dependencies**
    Using `uv`:
    ```sh
    uv sync
    ```
    *Note: The project pins `transformers` to 4.51.3 and uses CUDA 12.1-compatible PyTorch.*

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

**1. Start the Application**

This command starts the system tray app, which automatically launches the TTS server in the background.
```sh
uv run python -m app.main
```
*Wait for the startup announcement: "ScreenBanter is active..."*

**2. Controls**

| Hotkey | Action | Description |
| :--- | :--- | :--- |
| **`Ctrl + Alt + S`** | **Instant Capture** | Captures the current screen and narrates identified text immediately. |
| **`F10`** | **Queue Screenshot** | Captures the screen and adds it to a buffer. You will hear a confirmation beep. |
| **`F11`** | **Process Queue** | Sends all queued screenshots to Gemini, merges the text, and narrating the result. |

**3. Configuration**

Locate the tray-icon of the application (a loudspeaker). Right click on it and then click on `Settings`. You can customise the following here:

- **Custom Keyboard Shortcuts**: Define specific hotkeys for core actions (e.g., Control + Alt + S to trigger, F10 for queueing, and F11 for processing).
- **Personalized Audio Settings**: Configure the text-to-speech engine using the "en-Davis_man" voice, setting playback volume and speed to 100% (1.0).
- **Defined Capture Area**: Toggle between fullscreen narration or capture only a selected region. A GUI overlay will show when you toggle to region mode to guide you in setting it up.
- **System Behavior Preferences**: Configure application management, including minimizing the interface directly to the system tray upon launch, and enabling a startup confirmation sound (an announcement narrated by the TTS model).

**4. Logs**
- OCR results are logged to `logs/ocr.log`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Instant Narration
- [x] Batch Mode (Queueing)
- [x] Custom Region Capture
- [x] Settings GUI
- [x] Local Neural TTS (VibeVoice)
- [ ] Standalone Executable Build

See the [open issues](https://github.com/alfred1137/ScreenBanter/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

*Pull requests*, however, are not something I can manage at the moment. Me being an amateur vibe-coder is still familiarising myself with functionalities of Github...

Don't forget to give the project a ⭐star! Thanks again!

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Alfred T - [GitHub Profile](https://github.com/alfred1137)

Project Link: [https://github.com/alfred1137/ScreenBanter](https://github.com/alfred1137/ScreenBanter)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Microsoft/VibeVoice](https://github.com/microsoft/VibeVoice)
* [Google Gemini Vision](https://deepmind.google/technologies/gemini/)
* [DXcam](https://github.com/ra1nty/DXcam)
* [FastAPI](https://fastapi.tiangolo.com/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/alfred1137/ScreenBanter.svg?style=for-the-badge
[contributors-url]: https://github.com/alfred1137/ScreenBanter/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/alfred1137/ScreenBanter.svg?style=for-the-badge
[forks-url]: https://github.com/alfred1137/ScreenBanter/network/members
[stars-shield]: https://img.shields.io/github/stars/alfred1137/ScreenBanter.svg?style=for-the-badge
[stars-url]: https://github.com/alfred1137/ScreenBanter/stargazers
[issues-shield]: https://img.shields.io/github/issues/alfred1137/ScreenBanter.svg?style=for-the-badge
[issues-url]: https://github.com/alfred1137/ScreenBanter/issues
[license-shield]: https://img.shields.io/github/license/alfred1137/ScreenBanter.svg?style=for-the-badge
[license-url]: https://github.com/alfred1137/ScreenBanter/blob/master/LICENSE
[product-screenshot]: https://via.placeholder.com/800x400?text=ScreenBanter+Screenshot+Coming+Soon
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