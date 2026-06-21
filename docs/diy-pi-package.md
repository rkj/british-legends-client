# British Legends Mobile DIY Package

This guide is for players who want an always-on mobile British Legends client hosted on their own Raspberry Pi and protected by Cloudflare Tunnel + Cloudflare Access.

The package runs:

```text
phone browser -> Cloudflare Access -> Cloudflare Tunnel -> Pi web bridge -> British Legends telnet
```

## What You Need

- Raspberry Pi 5, or another always-on Linux host
- Raspberry Pi OS or Debian/Ubuntu
- A domain managed by Cloudflare
- A Cloudflare Tunnel, either existing or new
- Cloudflare Access enabled for the public hostname

Do not expose this bridge as an unprotected public website. Anyone who can reach the page can send commands through the active MUD session.

## Install On The Pi

Clone the project on the Pi:

```bash
sudo apt update
sudo apt install -y git
git clone https://github.com/scottlafond/british-legends-client.git
cd british-legends-client
```

Install the service:

```bash
sudo bash deploy/install-pi.sh
```

The installer:

- Copies the app to `/opt/british-legends-client`
- Creates a Python virtual environment
- Installs Python dependencies
- Creates a dedicated `britishlegends` system user
- Installs and starts `british-legends.service`
- Writes settings to `/etc/british-legends-client/british-legends.env`

By default, the service listens on `127.0.0.1:8080`. This is the best setting when `cloudflared` runs directly on the Pi host.

## Existing Docker Cloudflared Tunnel

If your existing `cloudflared` tunnel runs in Docker or another network namespace, it may not be able to reach `127.0.0.1` on the Pi host. In that case, install the bridge so it listens on the Pi LAN interface:

```bash
sudo BL_WEB_HOST=0.0.0.0 bash deploy/install-pi.sh
```

Then point the Cloudflare public hostname service URL to:

```text
http://<pi-lan-ip>:8080
```

For a host-installed `cloudflared`, point the tunnel service URL to:

```text
http://localhost:8080
```

## Cloudflare Tunnel Route

Add a public hostname to your tunnel:

- Hostname: `mud.yourdomain.com`
- Service type: `HTTP`
- Service URL, host-installed tunnel: `http://localhost:8080`
- Service URL, Docker tunnel: `http://<pi-lan-ip>:8080`

If the tunnel is config-file-managed, add the MUD route before the final catch-all rule:

```yaml
ingress:
  - hostname: mud.yourdomain.com
    service: http://localhost:8080
  - service: http_status:404
```

Use `http://<pi-lan-ip>:8080` instead of `http://localhost:8080` when the tunnel runs in Docker.

## Cloudflare Access

Create a self-hosted Access application for the MUD hostname:

- Application type: Self-hosted
- Hostname: `mud.yourdomain.com`
- Policy: allow only your email, or a small allowlist

This Access layer is the difference between a private mobile client and an open command console on the internet.

## Test Checklist

On the Pi:

```bash
systemctl status british-legends.service
curl http://127.0.0.1:8080/healthz
journalctl -u british-legends.service -f
```

If installed with `BL_WEB_HOST=0.0.0.0`, test from another device on the same LAN:

```bash
curl http://<pi-lan-ip>:8080/healthz
```

Test outbound telnet from the Pi:

```bash
python3 - <<'PY'
import socket
s = socket.create_connection(("british-legends.com", 27750), timeout=10)
print("connected")
s.close()
PY
```

On the phone:

1. Open `https://mud.yourdomain.com`
2. Authenticate through Cloudflare Access
3. Confirm the mobile client loads
4. Tap `Reconnect MUD`
5. Log in
6. Test `look`, `score`, `who`, macros, logging, and tell autocomplete
7. Turn Wi-Fi off and repeat a light test over mobile data

## Upgrade

From the clone directory on the Pi:

```bash
git pull
sudo bash deploy/install-pi.sh
```

The installer can be rerun. It refreshes the app files, rebuilds dependencies if needed, and restarts the service.

## Uninstall

Remove the systemd service but keep app files:

```bash
sudo bash deploy/uninstall-pi.sh
```

Remove the service, environment file, app directory, and service user:

```bash
sudo REMOVE_ENV=1 REMOVE_APP=1 REMOVE_USER=1 bash deploy/uninstall-pi.sh
```

Then remove the public hostname route and Access application from Cloudflare.

## Troubleshooting

`curl http://127.0.0.1:8080/healthz` fails:

```bash
journalctl -u british-legends.service -f
```

Cloudflare shows a bad gateway:

- Confirm the service URL matches how `cloudflared` is running.
- Host-installed tunnel: `http://localhost:8080`
- Docker tunnel: `http://<pi-lan-ip>:8080`

The web page loads, but commands fail:

- Tap `Reconnect MUD`
- Check outbound telnet from the Pi
- Read service logs with `journalctl -u british-legends.service -f`

The phone can only reach it on Wi-Fi:

- Confirm you are using the Cloudflare HTTPS hostname, not the LAN IP
- Confirm the Access policy allows your email
- Confirm the tunnel status is healthy
