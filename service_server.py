"""Run the British Legends bridge as a local-only service behind Cloudflare Tunnel."""

import os


os.environ.setdefault("BL_WEB_HOST", "127.0.0.1")
os.environ.setdefault("BL_WEB_PORT", "8080")
os.environ.setdefault("BL_CONNECT_ON_START", "0")
os.environ.setdefault("BL_TELNET_DEBUG", "0")

from preview_server import main


if __name__ == "__main__":
    main()
