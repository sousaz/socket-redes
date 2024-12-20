from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 10
TRIES = 2

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

def build_packet():
    #Fill in start
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.

    # Make the header in a similar way to the ping exercise.
    # Append checksum to the header.

    # Don’t send the packet yet , just return the final packet in this function.
    # Fill in end

    # code from sendOnePing below***

    ID = os.getpid() & 0xFFFF  # Return the current process i

    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    #***

    # So the function ending should look like this
    packet = header + data
    return packet

def get_route(hostname):
    timeLeft = TIMEOUT
    #tracelist1 = []  # This is your list to use when iterating through each trace
    tracelist2 = []  # This is your list to contain all traces

    for ttl in range(18, MAX_HOPS):
        tracelist1 = []
        #print(str(ttl))
        #print(tracelist1)
        #print(tracelist2)
        for tries in range(TRIES):

            # Fill in start
            # Make a raw socket named mySocket
            icmp = getprotobyname("icmp")
            mySocket = socket(AF_INET, SOCK_RAW, icmp)
            # Fill in end

            # Define o valor do TTL para o pacote.
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []:  # Timeout
                    tracelist1.append("* * * Request timed out.")
                    # Fill in start
                    # You should add the list above to your all traces list
                    tracelist2.append(tracelist1)
                    # Fill in end
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    tracelist1.append("* * * Request timed out.")
                    # Fill in start
                    # You should add the list above to your all traces list
                    tracelist2.append(tracelist1)
                    # Fill in end
            except timeout:
                continue
            else:
                # Fill in start
                # Fetch the icmp type from the IP packet
                icmpHeader = recvPacket[20:28]
                types, code, revChecksum, revId, revSequence = struct.unpack('bbHHh', icmpHeader)
                # Fill in end
                try:  # try to fetch the hostname
                    # Fill in start
                    hostAddr = gethostbyaddr(addr[0])
                    # Fill in end
                except herror:  # if the host does not provide a hostname
                    # Fill in start
                    hostAddr = ["hostname not returnable"]
                    # Fill in end

                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    # Fill in start
                    # You should add your responses to your lists here
                    tracelist1 = [str(ttl-17), str(int((timeReceived - timeSent) * 1000)) + "ms", addr[0], hostAddr[0]]
                    #print(tracelist1)
                    #print("\n")
                    tracelist2.append(tracelist1)
                    # Fill in end
                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    # Fill in start
                    # You should add your responses to your lists here
                    tracelist1 = [str(ttl-17), str(int((timeReceived - timeSent) * 1000)) + "ms", addr[0], hostAddr[0]]
                    #print(tracelist1)
                    #print("\n")
                    tracelist2.append(tracelist1)
                    # Fill in end
                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    # Fill in start
                    # You should add your responses to your lists here and return your list if your destination IP is met
                    tracelist1 = [str(ttl-17), str(int((timeReceived - timeSent) * 1000)) + "ms", addr[0], hostAddr[0]]
                    #print(tracelist1)
                    #print("\n")
                    tracelist2.append(tracelist1)
                    # Fill in end
                else:
                    # Fill in start
                    # If there is an exception/error to your if statements, you should append that to your list here
                    errorMessage = "error occurred"
                    #print(errorMessage)
                    tracelist2.append(errorMessage)
                    # Fill in end
                break
            finally:
                mySocket.close()

    #print(tracelist2)
    return tracelist2

print(get_route("www.google.com"))
# print(get_route("bbc.co.uk"))
# print(get_route("4.2.2.2"))
# print(get_route("202.158.214.106"))
# print(get_route("196.25.1.1"))