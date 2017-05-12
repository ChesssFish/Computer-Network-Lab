#encode "utf-8"
import socket
import gbn

addr = ("127.0.0.1", 23333)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
  command = raw_input()
  c = gbn.createDataFrame(command)
  print c.next()
  # s.sendto(c.next(), addr)
  # s.recvfrom(4096)