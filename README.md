# 🐉 British Legends Client (MUD1)

[![GitHub Release](https://img.shields.io/github/v/release/scottlafond/british-legends-client?color=success&style=flat-square)](https://github.com/scottlafond/british-legends-client/releases/latest)
[![Windows Code Signing](https://img.shields.io/badge/Security-Digitally_Signed-blue?style=flat-square&logo=windows)](https://github.com/scottlafond/british-legends-client/releases/latest)

A custom-built, modern, and highly polished desktop client for the classic MUD, **British Legends** (MUD1). 

Built from the ground up to bring a premium, modern aesthetic to a classic game without sacrificing the raw text-based feel.

<img width="2548" height="1363" alt="Screenshot 2026-06-17 160253" src="https://github.com/user-attachments/assets/405e2ff2-2036-442d-8823-84bd2a09d77a" />

## ✨ Features

- **The following game guides have been incorporated into the interface for quick easy review during play: How to Play, Tips for Players, FAQ, Terms and Conditions, MUD Client guide and finally a Tip Jar to Sysop!
- **Modern & Premium UI:** A beautiful, responsive interface with customized typography, glowing gold accents, and dynamic styling that brings an ease of play not present in standard command-prompt telnet clients.
- **Verified Security:** The Windows `.exe` release is **digitally signed** using Microsoft Azure Trusted Signing. No scary "Windows Protect Your PC" blue screens or unknown publisher warnings! (HOWEVER, you may still get that scary screen as I'm hardly a know software developer entity, so no reputation)
- **Auto-fill & Auto-complete:** Intelligent name auto-completion for faster typing.
- **Advanced Alias & Macro Support:** Fully customizable shortcuts.
- **Real-time Player Tracking:** Dynamic player list and tracking. TRACKING??? NO!!! don't you wish! You still have to hone your skills and instincts just like when I was a mere mortal!

## 📥 Download & Installation

You don't need to install Python, configure environments, or mess with code to play! 

1. Go to the [**Releases Page**](https://github.com/scottlafond/british-legends-client/releases/latest).
2. Download the latest **`BritishLegends.exe`** from the Assets section.
3. Double-click to run and start adventuring!

## 🐛 Feedback & Bug Reports
I would love to hear your feedback! Whether you've found a bug, have an idea for a new feature, or just want to suggest an improvement, please let me know.
You can report bugs or suggest features by opening an issue on the [GitHub Issues page](https://github.com/scottlafond/british-legends-client/issues).

## 🛠️ Architecture for Developers

For those curious about how it works under the hood, the client bridges the gap between classic telnet and modern web technologies:

1. **Frontend:** HTML, Vanilla CSS, and JS (`index.html`, `index.css`, `index.js`) providing the premium visual layout, web fonts, and DOM manipulation.
2. **Backend:** A local Python server (`web_server.py`) using WebSockets to connect the web interface to the MUD server (via raw telnet protocol), parsing game text in real-time.

### Building from Source

We use GitHub Actions to fully automate our builds and code signing, but if you want to build it locally to test changes:
1. Ensure you have Python installed.
2. Run the provided `build.bat` script to clean previous builds and package the application into a standalone Windows executable using `PyInstaller`.
