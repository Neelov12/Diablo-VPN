import socket
import ssl

# Hardcoded port for now
TLS_PORT = 4433

# File paths for server certificate and key (relative to project root)
CERT_PATH = "certs/cert.pem"
KEY_PATH = "certs/key.pem"

def start_tls_server(tun_fd):
    print("[*] Starting Diablo TLS server on port", TLS_PORT)

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERT_PATH, keyfile=KEY_PATH)

    bindsocket = socket.socket()
    bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    bindsocket.bind(('0.0.0.0', TLS_PORT))
    bindsocket.listen(5)

    newsocket, addr = bindsocket.accept()
    print(f"[+] Client connected from {addr[0]}:{addr[1]}")

    tls_socket = context.wrap_socket(newsocket, server_side=True)
    print("[+] TLS handshake successful")
    return tls_socket

def start_tls_client(server_ip):
    print(f"[*] Connecting to Diablo proxy server at {server_ip}:{TLS_PORT}")

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # NOTE: Replace with pinned cert later

    raw_socket = socket.socket()
    raw_socket.connect((server_ip, TLS_PORT))

    tls_socket = context.wrap_socket(raw_socket, server_hostname=server_ip)
    print("[+] Connected and TLS handshake completed")
    return tls_socket


