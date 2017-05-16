# -*- coding: utf-8 -*-
import socket
import gbn

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ("127.0.0.1", 23333)
while True:
  command = raw_input("«Î ‰»Î÷∏¡Ó\n")
  s.sendto(command, addr)
  f = open("recv", "wb")
  recv = gbn.gbnRecv(s)
  data = recv[0]
  f.write(data)
  f.close()
  # s.recvfrom(4096)