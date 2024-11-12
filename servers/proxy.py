from socket import *
import sys

HOST = "127.0.0.1"
PORT = 8888

# Função para determinar o tipo de conteúdo
def get_content_type(filename):
    if filename.endswith('.html'):
        return "text/html"
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        return "image/jpeg"
    elif filename.endswith('.png'):
        return "image/png"
    else:
        return "application/octet-stream"

# Cria o socket do servidor, vincula-o a uma porta e começa a escutar
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind((HOST, PORT))
tcpSerSock.listen(1)

try:
    while True:
        print('Pronto para servir...')
        tcpCliSock, addr = tcpSerSock.accept()
        message = tcpCliSock.recv(1024).decode('utf-8', 'ignore')
        
        try:
            # Verifica se a requisição HTTP está no formato esperado (GET /algo HTTP/1.1)
            filename = message.split()[1]
            
            # Extrai o hostname da URL solicitada (ex: /google.com -> google.com)
            if filename.startswith('/'):
                filename = filename[1:]  # Remove o leading '/'

            print("Arquivo solicitado:", filename)
            filetouse = filename

            # Verifica se o arquivo está no cache
            try:
                with open(filetouse, "rb") as f:
                    outputdata = f.readlines()
                    print("Lido do cache.")
                    
                    # Verifica se o conteúdo cacheado contém um redirecionamento
                    if b"HTTP/1.1 301" in outputdata[0] or b"HTTP/1.1 302" in outputdata[0]:
                        # Extrai o cabeçalho de localização para redirecionamento
                        for line in outputdata:
                            if line.startswith(b"Location:"):
                                location = line.decode().split(": ", 1)[1].strip()
                                tcpCliSock.send("HTTP/1.1 301 Moved Permanently\r\n".encode())
                                tcpCliSock.send(f"Location: {location}\r\n\r\n".encode())
                                print(f"Redirecionando para {location}")
                                break
                    else:
                        # Envia a resposta do cache para o cliente
                        tcpCliSock.send("HTTP/1.1 200 OK\r\n".encode())
                        for line in outputdata:
                            tcpCliSock.send(line)
            except IOError:
                # Conecta ao servidor remoto para buscar o arquivo
                hostn = filename.replace("www.", "", 1)
                print("Servidor remoto:", hostn)
                
                try:
                    c = socket(AF_INET, SOCK_STREAM)
                    c.connect((hostn, 80))
                    
                    # Envia a requisição HTTP para o servidor remoto
                    c.sendall(f"GET / HTTP/1.1\r\nHost: {hostn}\r\nConnection: close\r\n\r\n".encode('utf-8'))
                    
                    # Recebe a resposta do servidor remoto e armazena no cache
                    with open(filetouse, "wb") as tmpFile:
                        while True:
                            buff = c.recv(4096)
                            if not buff:
                                break
                            tmpFile.write(buff)
                            tcpCliSock.send(buff)
                    c.close()
                except Exception as e:
                    print("Erro ao conectar ao servidor remoto:", e)
                    tcpCliSock.send("HTTP/1.1 404 Not Found\r\n".encode())
                    tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
                    tcpCliSock.send("<html><body><h1>404 Not Found</h1></body></html>".encode())
                    
        except IndexError:
            print("Solicitação HTTP inválida")
            tcpCliSock.send("HTTP/1.1 400 Bad Request\r\n".encode())
            tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
            tcpCliSock.send("<html><body><h1>400 Bad Request</h1></body></html>".encode())
        
        tcpCliSock.close()
except KeyboardInterrupt:
    print("Servidor encerrado.")
    tcpSerSock.close()
    sys.exit()
