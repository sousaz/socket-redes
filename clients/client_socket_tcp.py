import socket
import sys

def http_client(host, port, path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        
        s.sendall(f"GET /{path} HTTP/1.1\r\nHost: {host}\r\n\r\n".encode('utf-8'))
        
        res = b""
        while True:
            data = s.recv(1024)
            if not data:
                break
            res += data

        res = res.decode('utf-8').split("\r\n\r\n")[1]

        with open('response.html', 'w', encoding='utf-8') as f:
            f.write(res)
        print(res)

if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <host> <port> <path>")
    sys.exit(1)

host = sys.argv[1]
port = int(sys.argv[2])
path = sys.argv[3]

# for i in range(4):
http_client(host, port, path)
