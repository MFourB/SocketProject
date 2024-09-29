from socket import *
serverName = "localhost"
serverPort = 1000
clientSocket = socket(AF_INET, SOCK_DGRAM)
message = input("Input lowercase sentance:")
clientSocket.sendto(message.encode(), (serverName, serverPort))
# modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
clientSocket.close()