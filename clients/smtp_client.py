import socket
import base64
import ssl

msg = "I love computer networks!"
endmsg = "\r\n.\r\n"

mailserver = 'smtp.gmail.com'

def send_command(s, c):
    s.send((c + '\r\n').encode('utf-8'))
    recv = s.recv(1024).decode('utf-8')
    print(recv)
    return recv

def send_file(s, filename):
    with open(filename, 'rb') as file:
        f = base64.b64encode(file.read()).decode('utf-8')
        s.send(f.encode('utf-8'))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((mailserver, 587))
    recv = s.recv(1024).decode('utf-8')
    print("recv1:", recv)

    #Inicia comunicação atraves do comando EHLO
    send_command(s, "EHLO Alice")

    #Inicia o TLS atraves do comando STARTTLS
    send_command(s, "STARTTLS")
    #Camada SSL
    context = ssl.create_default_context()
    secure = context.wrap_socket(s, server_hostname=mailserver)

    #Autenticação Base64
    username = "yourmail@gmail.com"
    password = "password"
    send_command(secure, "AUTH LOGIN")
    send_command(secure, base64.b64encode(username.encode()).decode('utf-8'))
    send_command(secure, base64.b64encode(password.encode()).decode('utf-8'))

    #Envio de email
    send_command(secure, "MAIL FROM: <" +username+ ">")

    #Destinatario
    send_command(secure, "RCPT TO: <" +username+ ">")

    #Envio de dados
    send_command(secure, "DATA")

    #Corpo do email
    secure.send("Subject: Teste de envio de email\r\n".encode('utf-8'))
    secure.send("MIME-Version: 1.0\r\n".encode('utf-8'))
    secure.send("Content-Type: multipart/mixed; boundary=\"frontier\"\r\n".encode('utf-8'))
    secure.send("\r\n".encode('utf-8'))

    secure.send("--frontier\r\n".encode('utf-8'))
    secure.send("Content-Type: text/plain; charset='UTF-8'\r\n".encode('utf-8'))
    secure.send("\r\n".encode('utf-8'))

    secure.send(msg.encode('utf-8'))

    #Anexar arquivo
    secure.send("\r\n\r\n".encode('utf-8'))
    secure.send("--frontier\r\n".encode('utf-8'))
    secure.send("Content-Type: text/plain; charset='UTF-8'; name=\"1219181.jpg\"\r\n".encode('utf-8'))
    secure.send("Content-Transfer-Encoding: base64\r\n".encode('utf-8'))
    secure.send("Content-Disposition: attachment; filename=\"1219181.jpg\"\r\n".encode('utf-8'))
    secure.send("\r\n".encode('utf-8'))
    send_file(secure, "1219181.jpg")
    secure.send("\r\n--frontier--\r\n".encode('utf-8'))

    #Fim da mensagem
    secure.send(endmsg.encode('utf-8'))

    #Encerra a conexão
    send_command(secure, "QUIT")

    s.close()