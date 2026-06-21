"""Run the web dashboard on a fixed local port for browser and phone previews."""

import http.server
import os
import socket
import sys

import web_server


HOST = os.environ.get("BL_WEB_HOST", "0.0.0.0")
try:
    PORT = int(os.environ.get("BL_WEB_PORT", "8080"))
except ValueError:
    print("BL_WEB_PORT must be an integer.", file=sys.stderr)
    sys.exit(2)


def get_lan_ips():
    ips = []
    hostname = socket.gethostname()
    try:
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except socket.gaierror:
        pass
    return ips


class PreviewDashboardHTTPHandler(web_server.DashboardHTTPHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        return super().end_headers()

    def log_message(self, format, *args):
        message = "%s - - [%s] %s" % (
            self.client_address[0],
            self.log_date_time_string(),
            format % args,
        )
        print(message, flush=True)

    def do_GET(self):
        if self.path == "/healthz":
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"ok\n")
            return
        return super().do_GET()


def main():
    server_address = (HOST, PORT)
    httpd = http.server.ThreadingHTTPServer(server_address, PreviewDashboardHTTPHandler)
    print(f"British Legends server listening on http://{HOST}:{PORT}", flush=True)
    print(f"Local URL: http://127.0.0.1:{PORT}", flush=True)
    if HOST in ("0.0.0.0", "::", ""):
        for ip in get_lan_ips():
            print(f"Phone/LAN URL: http://{ip}:{PORT}", flush=True)
            print(f"Phone/LAN health check: http://{ip}:{PORT}/healthz", flush=True)
    print("Press Ctrl+C to stop.", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping preview server.", flush=True)
    finally:
        web_server.client.close()


if __name__ == "__main__":
    main()
