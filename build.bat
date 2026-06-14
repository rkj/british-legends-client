@echo off
"C:\Users\Scott LaFond\AppData\Roaming\Python\Python313\Scripts\pyinstaller.exe" --noconsole --onefile --name "BritishLegends" --add-data "index.html;." --add-data "index.js;." --add-data "index.css;." --add-data "*.png;." --add-data "*.jpg;." --add-data "curated_map_layout.json;." --hidden-import webview web_server.py
