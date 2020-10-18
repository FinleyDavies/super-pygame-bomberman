import socket

s = socket.socket()
host = "ec2-3-17-188-254.us-east-2.compute.amazonaws.com"
port = 4832

s.connect((host, port))
print(s.recv(1024).decode())
s.close()