import random
import socket
import time

# Criar um socket UDP
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Atribuir endereço IP e número da porta ao socket
serverSocket.bind(('localhost', 12000))
print(f"Server listening on {'localhost'}:{12000}")
last_heartbeat = {}
timeout = 5  # Tempo limite em segundos

while True:
    # Gerar número aleatório entre 0 e 10
    rand = random.randint(0, 10)

    serverSocket.settimeout(timeout)  # Definir um timeout para recvfrom
    try:
        # Receber o pacote do cliente junto com o endereço de origem
        message, address = serverSocket.recvfrom(1024)
        current_time = time.time()

        # Colocar a mensagem recebida em maiúsculas
        message = message.upper()

        # Se o número rand for menor que 4, consideramos que o pacote foi perdido e não respondemos
        if rand < 4:
            continue

        last_heartbeat[address] = current_time

        # Caso contrário, o servidor responde
        serverSocket.sendto(message, address)
    except socket.timeout:
        current_time = time.time()
        expired_clients = [addr for addr, last_time in last_heartbeat.items() if current_time - last_time > timeout]
        for addr in expired_clients:
            print(f"Conexão expirada para o cliente {addr}")
            del last_heartbeat[addr]
