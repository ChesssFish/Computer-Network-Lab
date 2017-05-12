#encode "utf-8"
import socket
import gbn

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ("127.0.0.1", 23333)
  
while True:
  command = raw_input()
  buf = "a" * (1024 * 100 + 1)
  gbn.gbnSend(buf, s, addr)
    
  # s.recvfrom(4096)