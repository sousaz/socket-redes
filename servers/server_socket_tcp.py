import socket
import os
import sys
import threading
import random
from time import sleep

HOST = "127.0.0.1"
PORT = 8080

def read_html_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding='utf-8') as file:
            return file.read()
    else:
        return None

def build_response(status_code, content_type, content):
    response_line = f"HTTP/1.1 {status_code}\r\n"
    headers = f"Content-Type: {content_type}\r\nContent-Length: {len(content)}\r\n"
    return f"{response_line}{headers}\r\n{content}"

def handle_client(conn, addr):
    # time = random.choice([3, 9])
    # sleep(time)
    with conn:
        try:
            # print(f"Connected by {addr}")
            req = conn.recv(1024).decode('utf-8')
            # print(f"Received: {req}")

            path = req.splitlines()[0]
            path = path.split()[1]
            if path == "/":
                path = "helloWorld.html"
            path = path.lstrip("/")

            html_content = read_html_file(path)
            if html_content is None:
                res = build_response(404, "text/plain", "404 Not found")
            else:
                res = build_response(200, "text/html", html_content)

            conn.sendall(res.encode('utf-8'))
            # print("Sent response")
        except Exception as e:
            print(f"Error: {e}")
            res = build_response(500, "text/plain", "Internal server error")
            conn.sendall(res.encode('utf-8'))
        finally:
            conn.close()
            print("Connection closed")
            sys.exit(0)
    
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            # print(f"New connection from {addr}")
            threading.Thread(target=handle_client, args=(conn, addr)).start()

start_server()
