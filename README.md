# 🐉 British Legends Client (MUD1)

[![GitHub Release](https://img.shields.io/github/v/release/scottlafond/british-legends-client?color=success&style=flat-square)](https://github.com/scottlafond/british-legends-client/releases/latest)
[![Windows Code Signing](https://img.shields.io/badge/Security-Digitally_Signed-blue?style=flat-square&logo=windows)](https://github.com/scottlafond/british-legends-client/releases/latest)

A custom-built, modern, and highly polished desktop client for the classic MUD, **British Legends** (MUD1). 

Built from the ground up to bring a premium, modern aesthetic to a classic game without sacrificing the raw text-based feel.

> **📸 Screenshot:** *[I highly recommend taking a beautiful screenshot of the client running, editing this README on GitHub, and dragging the image right here!]*

## ✨ Features

- **Modern & Premium UI:** A beautiful, responsive interface with customized typography, glowing cyan/gold accents, and dynamic styling that feels lightyears ahead of standard command-prompt telnet clients.
- **Verified Security:** The Windows `.exe` release is **digitally signed** using Microsoft Azure Trusted Signing. No scary "Windows Protect Your PC" blue screens or unknown publisher warnings!
- **Interactive 3D Map Explorer:** Built-in interactive map viewer.
- **Auto-fill & Auto-complete:** Intelligent name auto-completion for faster typing.
- **Advanced Alias & Macro Support:** Fully customizable shortcuts.
- **Real-time Player Tracking:** Dynamic stat display and tracking.

## 📥 Download & Installation

You don't need to install Python, configure environments, or mess with code to play! 

1. Go to the [**Releases Page**](https://github.com/scottlafond/british-legends-client/releases/latest).
2. Download the latest **`BritishLegends.exe`** from the Assets section.
3. Double-click to run and start adventuring!

## 🛠️ Architecture for Developers

For those curious about how it works under the hood, the client bridges the gap between classic telnet and modern web technologies:

1. **Frontend:** HTML, Vanilla CSS, and JS (`index.html`, `index.css`, `index.js`) providing the premium visual layout, web fonts, and DOM manipulation.
2. **Backend:** A local Python server (`web_server.py`) using WebSockets to connect the web interface to the MUD server (via raw telnet protocol), parsing game text in real-time.

### Building from Source

We use GitHub Actions to fully automate our builds and code signing, but if you want to build it locally to test changes:
1. Ensure you have Python installed.
2. Run the provided `build.bat` script to clean previous builds and package the application into a standalone Windows executable using `PyInstaller`.

## 🐛 Feedback & Bug Reports

I would love to hear your feedback! Whether you've found a bug, have an idea for a new feature, or just want to suggest an improvement, please let me know.

You can report bugs or suggest features by opening an issue on the [GitHub Issues page](https://github.com/scottlafond/british-legends-client/issues).
