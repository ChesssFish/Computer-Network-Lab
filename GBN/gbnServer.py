#encode "utf-8"
import socket
import gbn
from select import select

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", 23333))

b = bytearray(100)
b[0:5] = "12345"
b[10:15] = "12345"[0:15]
print b


while True:
  print u"接收指令中..."
  result = s.recvfrom(4096)
  frame = result[0]
  addr = result[1]
  print frame, addr
  command = gbn.parseFrame(frame[0])[1]
  if command == "-time":
    sendTime(addr)
  elif command == "-quit":
    sendGoodBye(addr)
  elif command == "-testgbn":
    sendFile(addr)
  else:
    sendUnknown(addr)

