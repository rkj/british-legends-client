# British Legends Client

A custom-built, modern desktop client for the classic MUD, British Legends.

## Features
- Interactive 3D map viewer and explorer
- Auto-fill and auto-complete for names
- Advanced alias and macro support
- Real-time player tracking and stats display

## Architecture
The client is split into two main pieces:
1. **Frontend:** HTML, CSS, and JS files (`index.html`, `index.css`, `index.js`) providing a modern and premium UI.
2. **Backend:** A local Python server (`web_server.py`) using WebSockets to connect the web interface to the MUD server (via telnet protocol), parsing game text in real-time.

## Build Instructions
We use `PyInstaller` to package the client into a standalone Windows executable.
Run the provided `build.bat` script to clean previous builds and generate the new `BritishLegends.exe` in the `dist` folder.
