import socket

# Configuration des ports (doivent correspondre au code PyQt5)
UDP_PORT = 45454
TCP_PORT = 8080

# 1. Configuration du socket UDP pour répondre au scan
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind(('', UDP_PORT)) # Écoute sur toutes les interfaces

# 2. Configuration du socket TCP pour recevoir le JSON
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_sock.bind(('', TCP_PORT))
tcp_sock.listen(1)

print(f"--- Serveur de test lancé ---")
print(f"En attente de scan UDP sur le port {UDP_PORT}...")

try:
    while True:
        # Attente d'un message de découverte
        data, addr = udp_sock.recvfrom(1024)
        if b"MONITOR_REQUEST" in data:
            print(f"[UDP] Requête de scan reçue de {addr}")
            udp_sock.sendto(b"MONITOR_ALIVE", addr)
            print(f"[UDP] Réponse 'MONITOR_ALIVE' envoyée.")

            # Attente immédiate de la connexion TCP pour le JSON
            print(f"[TCP] En attente de données sur le port {TCP_PORT}...")
            conn, addr_tcp = tcp_sock.accept()
            with conn:
                payload = conn.recv(4096)
                if payload:
                    print(f"[TCP] Données JSON reçues : {payload.decode('utf-8')}")
                print("-" * 30)
except KeyboardInterrupt:
    print("\nArrêt du serveur.")
finally:
    udp_sock.close()
    tcp_sock.close()
