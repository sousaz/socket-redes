import socket
import os
import sys
import struct
import time
import select
import binascii

errors = {0: "0 - Rede de Destino Inalcançável",
          1: "1 - Host de Destino Inalcançável"}

def rtts(rtt):
  avg = sum(rtt) / len(rtt)
  max_rtt = max(rtt)
  min_rtt = min(rtt)
  return avg, max_rtt, min_rtt

stats = []
countTimeouts = 0
countPings = 0

ICMP_ECHO_REQUEST = 8

def checksum(data):

  csum = 0
  countTo = (len(data) / 2) * 2

  count = 0
  while count < countTo:
    thisVal = (data[count+1]) * 256 + (data[count])
    csum = csum + thisVal
    csum = csum & 0xffffffff #
    count = count + 2

  if countTo < len(data):
    csum = csum + ord(data[len(data) - 1])
    csum = csum & 0xffffffff #

  csum = (csum >> 16) + (csum & 0xffff)
  csum = csum + (csum >> 16)
  
  answer = ~csum
  answer = answer & 0xffff
  answer = answer >> 8 | (answer << 8 & 0xff00)

  return answer


def receiveOnePing(mySocket, ID, timeout, destAddr):
  global stats
  global countTimeouts
  timeLeft = timeout

  while 1:
    startedSelect = time.time()
    whatReady = select.select([mySocket], [], [], timeLeft)
    howLongInSelect = (time.time() - startedSelect)
    if whatReady[0] == []: # Timeout
      countTimeouts += 1
      return "Request timed out."

    timeReceived = time.time()
    recPacket, addr = mySocket.recvfrom(1024)

    icmpHeader = recPacket[20:28]
    type, code, checksum, receivedID, sequence = struct.unpack("bbHHh", icmpHeader)

    if type == 3:
      return errors[code]

    #receivedID must equal process ID
    if receivedID == ID:
      numOfBytes = struct.calcsize("d")
      timeSent = struct.unpack("d", recPacket[28:28 + numOfBytes])[0]
      rtt = (timeReceived - timeSent)*1000
      stats.append(rtt)

      print ("Reply from:",destAddr, "Time:",rtt, "ms")
      return ""

    timeLeft = timeLeft - howLongInSelect
    if timeLeft <= 0:
      countTimeouts += 1
      return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
  # Header is type (8), code (8), checksum (16), id (16), sequence (16)
  myChecksum = 0
  # Make a dummy header with a 0 checksum.
  # struct -- Interpret strings as packed binary data
  header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)

  data = struct.pack("d", time.time())

  # Calculate the checksum on the data and the dummy header.
  myChecksum = checksum(header + data)

  #Get the right checksum, and put in the header
  if sys.platform == 'darwin':
    myChecksum = socket.htons(myChecksum) & 0xffff   #Convert 16-bit integers from host to network byte order.
  else:
    myChecksum = socket.htons(myChecksum) # Transforma em bytes para que possa ser lido pelo sistema

  #print ("ICMP Header: ", ICMP_ECHO_REQUEST,0,myChecksum,ID,1)
  header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
  packet = header + data

  mySocket.sendto(packet, (destAddr, 1))
  # AF_INET address must be tuple, not str.
  # Both LISTS and TUPLES consist of a number of objects
  # which can be referenced by their position number within the object.


def doOnePing(destAddr, timeout):

  icmp = socket.getprotobyname("icmp")
  #SOCK_RAW is a powerful socket type. For more details:   http://sock-raw.org/papers/sock_raw

  # Fill in start
  # Create socket here.
  mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp) # Sock_raw é um pacote cru pacotes não processados pelo SO diretamente

  # Fill in end
  myID = os.getpid() & 0xFFFF  #Return the current process i
  sendOnePing(mySocket, destAddr, myID)
  delay = receiveOnePing(mySocket, myID, timeout, destAddr)
  mySocket.close()

  return delay


def ping(host, timeout=1):
  #timeout=1 means: If one second goes by without a reply from the server,
  #the client assumes that either the client's ping or the server's pong is lost
  global countPings

  dest = socket.gethostbyname(host)
  print ("Pinging " + dest + " using Python:")
  print ("")

  # Send ping requests to a server separated by approximately one second.
  # I will be sending a single ping message to each server.
  for i in range(0, 4):
    delay = doOnePing(dest, timeout)
    countPings += 1
    print (delay)
    time.sleep(1)# one second

  return delay



print("Localhost")
ping("127.0.0.1")

print("bbc.co.uk")
ping("bbc.co.uk")

print("Ásia")
ping("4.2.2.2")

print("Oceania")
ping("202.158.214.106")

print("África")
ping("196.25.1.1")

print("Alemanha")
ping("84.200.69.80")

print("--------------------------------Resultados--------------------------------")
avg, max_rtt, min_rtt = rtts(stats)
print(f"Maior tempo: {max_rtt:.2f}ms")
print(f"Menor tempo: {min_rtt:.2f}ms")
print(f"Tempo medio: {avg:.2f}ms")
print(f"Timeouts: {countTimeouts}, {countTimeouts / countPings * 100:.0f}%")