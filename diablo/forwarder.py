import os
import threading

def start_forwarding(tun_fd, tls_socket):
    """
    Start two threads:
    1. TUN -> TLS (client to proxy)
    2. TLS -> TUN (proxy to client)
    """
    threading.Thread(target=tun_to_socket, args=(tun_fd, tls_socket), daemon=True).start()
    threading.Thread(target=socket_to_tun, args=(tls_socket, tun_fd), daemon=True).start()

    print("[*] Forwarding started. Press Ctrl+C to exit.")
    try:
        while True:
            pass  # keep main thread alive
    except KeyboardInterrupt:
        print("\n[!] Shutting down Diablo.")
        tls_socket.close()
        os.close(tun_fd)

def tun_to_socket(tun_fd, tls_socket):
    while True:
        try:
            packet = os.read(tun_fd, 2048)
            if packet:
                tls_socket.sendall(packet)
        except Exception as e:
            print("[-] Error in tun_to_socket:", e)
            break

def socket_to_tun(tls_socket, tun_fd):
    while True:
        try:
            data = tls_socket.recv(2048)
            if data:
                os.write(tun_fd, data)
        except Exception as e:
            print("[-] Error in socket_to_tun:", e)
            break


