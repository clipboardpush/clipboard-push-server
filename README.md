# Clipboard Push Server

A self-hosted relay server for the [Clipboard Push](https://clipboardpush.com) app — relays clipboard text and files between Android and PC over the internet or LAN.

## Features

- **Real-time clipboard push** via Socket.IO (text and files)
- **LAN-first file transfer** — direct device-to-device when on the same network, with automatic cloud fallback
- **AES-256-GCM end-to-end encryption** — the server never sees plaintext clipboard content
- **Cloudflare R2 file relay** — temporary pre-signed URLs for cross-network file transfers
- **Admin dashboard** — view connected devices, room states, transfer activity, and live logs
- **Room-based routing** — up to 2 devices per room; oldest device is evicted when limit exceeded
- **Docker support** — single `docker-compose up` deployment

## Quick Start (Docker)

```bash
git clone https://github.com/clipboardpush/clipboard-push-server.git
cd clipboard-push-server
cp .env.example .env
# Edit .env and fill in your values (see Configuration section)
docker-compose up -d
```

The server starts on port `5055` by default.

## Manual / Other Deployment Options

See [DEPLOY.md](DEPLOY.md) for full guides covering Linux (Debian/Ubuntu/CentOS), macOS local dev, Nginx reverse proxy, SSL, and systemd setup.

## Configuration

Copy `.env.example` to `.env` and fill in the following:

| Variable | Required | Description |
|---|---|---|
| `FLASK_SECRET_KEY` | Yes | Random secret for Flask sessions. Generate with `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `ADMIN_PASSWORD` | Yes | Initial admin dashboard password (hashed on first use) |
| `R2_ACCOUNT_ID` | For file relay | Cloudflare account ID |
| `R2_ACCESS_KEY_ID` | For file relay | R2 API token key ID |
| `R2_SECRET_ACCESS_KEY` | For file relay | R2 API token secret |
| `R2_BUCKET_NAME` | For file relay | R2 bucket name for file storage |
| `DASHBOARD_R2_BUCKET` | For dashboard | R2 bucket name shown in dashboard stats (can be same as above) |
| `FLASK_DEBUG` | No | Set to `1` for debug mode (never use in production) |

**Text-only mode:** If you don't configure R2, the server works fine for clipboard text sync. File transfer will be unavailable.

## Architecture

```
Android App  ── Socket.IO (AES-256-GCM encrypted) ──► Relay Server ◄── Socket.IO (AES-256-GCM encrypted) ──  PC Client
                                                            │
                                                            └── R2 (file storage, optional)
```

- Clients connect to a shared **room** (identified by a room ID you set in the app)
- Text clipboard content is **AES-256-GCM encrypted** on the device — the server relays ciphertext only
- For files, the server orchestrates a **LAN-first pull** flow: the sender serves the encrypted file over HTTP, the receiver pulls it directly over LAN; if that fails, the file is uploaded to R2 and downloaded via pre-signed URL. Both Android→PC and PC→Android directions are supported.
- The admin dashboard is accessible at `http://your-server:5055/dashboard` (login with `ADMIN_PASSWORD`)

### Protocol Version

Current protocol version: `4.0`

Clients must include `"protocol_version": "4.0"` in file transfer events. See [RELAY_SERVER_API.md](RELAY_SERVER_API.md) for the full Socket.IO and HTTP API reference.

## Clients

| Client | Link |
|---|---|
| Android | [Google Play](https://play.google.com/store/apps/details?id=com.clipboardpush.plus) — [source on GitHub](https://github.com/clipboardpush/clipboard-push-android) |
| PC (Windows) | [GitHub](https://github.com/clipboardpush/clipboard-push-win32) · [Releases](https://github.com/clipboardpush/clipboard-push-win32/releases) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
