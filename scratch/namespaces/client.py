import socket

client_socket = socket.socket()
port = 1025
client_socket.connect(('127.0.0.1', port))
print(client_socket.recv(1024).decode())
client_socket.close()