import ssl
import socket
import json
from pathlib import Path
from .terminal import Terminal
from .settings import Settings

CONFIG_DIR = Path.home() / ".config" / "diablo"
CERTS_DIR = Path(__file__).parent.parent / "certs"

def load_config():
    cfg_file = CONFIG_DIR / "config.json"
    if cfg_file.exists():
        return json.loads(cfg_file.read_text())
    return {}

def start_tls_server(bind_addr="0.0.0.0", port=4433, backlog=5):
    cfg = Settings.load_config()
    password_required = cfg.get("require_password", False)
    password = cfg.get("password", None)

    # SSL context
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(
        certfile=str(CERTS_DIR / "server.crt"),
        keyfile=str(CERTS_DIR / "server.key")
    )

    # TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((bind_addr, port))
    sock.listen(backlog)

    Terminal.success(f"TLS server started on {bind_addr}:{port} "
                     f"{'(password protected)' if password_required else ''}")

    return sock, ctx, password_required, password

def authenticate_client(conn, password_required, password):
    """
    Authenticate client after TLS handshake.
    Returns True if auth ok, False otherwise.
    """
    try:
        data = conn.recv(1024).decode()
        msg = json.loads(data)

        if password_required:
            client_pw = msg.get("auth", {}).get("password", "")
            if client_pw == password:
                conn.sendall(json.dumps({"auth": "ok"}).encode())
                return True
            else:
                conn.sendall(json.dumps({"auth": "fail", "reason": "invalid password"}).encode())
                return False
        else:
            # No password required
            conn.sendall(json.dumps({"auth": "ok"}).encode())
            return True

    except Exception as e:
        Terminal.error(f"Auth error: {e}")
        return False
