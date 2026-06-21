# Pi5 + Cloudflare Tunnel Bring-Up

Goal:

`phone browser -> Cloudflare Access -> existing Pi5 cloudflared tunnel -> Pi web bridge on port 8080 -> British Legends telnet`

For the packaged DIY flow, start with `docs/diy-pi-package.md`. This file remains as a lower-level bring-up checklist.

## 1. Install the Bridge on the Pi

Preferred packaged install:

```bash
git clone https://github.com/scottlafond/british-legends-client.git
cd british-legends-client
sudo bash deploy/install-pi.sh
```

If the existing Cloudflare tunnel runs in Docker, install with:

```bash
sudo BL_WEB_HOST=0.0.0.0 bash deploy/install-pi.sh
```

Manual install notes:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv

sudo mkdir -p /opt/british-legends-client
sudo chown "$USER:$USER" /opt/british-legends-client

# Use your current repo source here. If cloning from GitHub:
git clone https://github.com/scottlafond/british-legends-client.git /opt/british-legends-client

cd /opt/british-legends-client
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

For manual testing before installing the service:

```bash
cd /opt/british-legends-client
BL_WEB_HOST=0.0.0.0 BL_WEB_PORT=8080 BL_CONNECT_ON_START=0 BL_TELNET_DEBUG=0 .venv/bin/python service_server.py
```

In another terminal:

```bash
curl http://127.0.0.1:8080/healthz
curl http://<pi-lan-ip>:8080/healthz
curl http://127.0.0.1:8080/updates
```

Expected: `healthz` returns `ok`, and `/updates` returns JSON with `"is_connected": false` until you press **Reconnect MUD** in the web UI.

## 2. Install the Systemd Service

```bash
sudo groupadd --system britishlegends || true
sudo useradd --system --gid britishlegends --home /opt/british-legends-client --shell /usr/sbin/nologin britishlegends || true
sudo chown -R britishlegends:britishlegends /opt/british-legends-client
sudo mkdir -p /etc/british-legends-client
sudo cp /opt/british-legends-client/deploy/british-legends.env.example /etc/british-legends-client/british-legends.env
sudo cp /opt/british-legends-client/deploy/british-legends.service /etc/systemd/system/british-legends.service
sudo systemctl daemon-reload
sudo systemctl enable --now british-legends.service

systemctl status british-legends.service
curl http://127.0.0.1:8080/healthz
curl http://<pi-lan-ip>:8080/healthz
```

Useful logs:

```bash
journalctl -u british-legends.service -f
```

The packaged installer configures:

- `BL_WEB_HOST=127.0.0.1` by default, or `0.0.0.0` when installed with `sudo BL_WEB_HOST=0.0.0.0 bash deploy/install-pi.sh`
- `BL_WEB_PORT=8080`
- `BL_CONNECT_ON_START=0`
- `BL_TELNET_DEBUG=0`

That means the MUD telnet connection starts only when the browser user taps **Reconnect MUD**.

## 3. Add a Route to the Existing N8N Tunnel

Since the existing `cloudflared` n8n tunnel is already running on the Pi5, add a second public hostname route to the same tunnel:

- Hostname: `mud.example.com`
- Service type: `HTTP`
- Service URL: `<pi-lan-ip>:8080` for Dockerized `cloudflared`, or `localhost:8080` for host-installed `cloudflared`

If the tunnel is dashboard-managed:

1. Cloudflare Zero Trust dashboard
2. Networks
3. Tunnels
4. Select the existing n8n tunnel
5. Add a public hostname route for `mud.example.com`
6. Point it to `http://<pi-lan-ip>:8080` for Dockerized `cloudflared`, or `http://localhost:8080` for host-installed `cloudflared`

If the tunnel is config-file-managed, see `deploy/cloudflared-ingress.example.yml`. Keep the existing n8n route and add the MUD route before the final catch-all `http_status:404` rule.

## 4. Protect the Hostname with Cloudflare Access

Create or enable an Access policy for the MUD hostname:

- Application: self-hosted web app
- Hostname: `mud.example.com`
- Policy: allow only your email address

Do not leave the MUD bridge public. Anyone who reaches the UI can send commands to the active MUD session.

## 5. Test Matrix

Local Pi test:

```bash
curl http://127.0.0.1:8080/healthz
curl http://<pi-lan-ip>:8080/healthz
systemctl status british-legends.service
```

Tunnel route test:

```bash
cloudflared tunnel ingress validate
cloudflared tunnel ingress rule https://mud.example.com
```

Phone on Wi-Fi:

1. Open `https://mud.example.com`
2. Authenticate through Cloudflare Access
3. Confirm the mobile client loads
4. Tap **Reconnect MUD**
5. Log in
6. Test `look`, `score`, `who`, and tell autocomplete/swipe

Phone on mobile data:

1. Turn Wi-Fi off
2. Open `https://mud.example.com`
3. Authenticate through Cloudflare Access
4. Confirm the client loads
5. Send a harmless command such as `look`

MUD outbound test from the Pi:

```bash
python3 - <<'PY'
import socket
s = socket.create_connection(("british-legends.com", 27750), timeout=10)
print("connected")
s.close()
PY
```

Expected: `connected`.

## 6. Rollback

```bash
sudo systemctl disable --now british-legends.service
sudo rm /etc/systemd/system/british-legends.service
sudo systemctl daemon-reload
```

Then remove the `mud.example.com` route from the existing Cloudflare tunnel.
