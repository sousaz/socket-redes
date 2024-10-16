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
    # 25, 465ssl, 587tls 2525
    #587 é um padrão e suportado por muitos servidores
    #suporta comunicação com e sem tls
    #Outras portas são bloqueadas para evitar spam
    s.connect((mailserver, 587))
    recv = s.recv(1024).decode('utf-8')
    print("recv1:", recv)

    #Inicia comunicação atraves do comando EHLO
    #Alice é um nome ficticio, normalmente é o nome do servidor, host, identificador
    send_command(s, "EHLO Alice")

    #Inicia o TLS atraves do comando STARTTLS
    #diz ao servidor para mudar para uma conexão segura, e cria uma camada de transporte segura
    send_command(s, "STARTTLS")
    #Camada SSL
    #Cria um socket securo que ira criptografar os dados e usar o TLS
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

    #Avisa que vai enviar o corpo do email
    send_command(secure, "DATA")

    #Corpo do email
    secure.send("Subject: Teste de envio de email\r\n".encode('utf-8'))
    #MIME (Multipurpose Internet Mail Extensions) é uma extensão do 
    #protocolo de e-mail que permite o envio de diferentes tipos de 
    #conteúdo além de texto simples.
    secure.send("MIME-Version: 1.0\r\n".encode('utf-8'))
    #boundary é um delimitador que separa as partes do email
    #usado para demilitar a parte do texto e a parte do arquivo
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