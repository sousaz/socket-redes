import socket
import time

def rtts(rtt):
    avg = sum(rtt) / len(rtt)
    max_rtt = max(rtt)
    min_rtt = min(rtt)
    return avg, max_rtt, min_rtt

def udp_client(host, port, message, timeout=1, n=10):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(timeout)
        stats = []
        timeouts = 0
        for i in range(n):
            try:
                start = time.time()
                s.sendto(message.encode('utf-8'), (host, port))
                data, _ = s.recvfrom(1024)
                end = time.time()
                print(f"mensagem: {data.decode('utf-8')}, tempo: {((end - start) * 1000):.2f}ms")
                stats.append(end - start)
            except socket.timeout:
                print('Timeout')
                timeouts += 1
        print("--------------------------------Resultados--------------------------------")
        avg, max_rtt, min_rtt = rtts(stats)
        print(f"Maior tempo: {max_rtt * 1000:.2f}ms")
        print(f"Menor tempo: {min_rtt * 1000:.2f}ms")
        print(f"Tempo medio: {avg * 1000:.2f}ms")
        print(f"Timeouts: {timeouts}, {timeouts / n * 100:.0f}%")

udp_client('localhost', 12000, 'ping', 1, 40)
