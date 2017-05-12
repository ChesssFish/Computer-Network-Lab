#encode "utf-8"
import socket
import gbn
import time
from select import select

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", 23333))

def sendTime(addr):
  pass

while True:
  print u"接收指令中..."
  result = gbn.gbnRecv(s)
  command = result[0]
  addr = result[1]
  
  if command == "-time":
    sendTime(addr)
  elif command == "-quit":
    sendGoodBye(addr)
  elif command == "-testgbn":
    sendFile(addr)
  else:
    f = open("recv", "wb")
    f.write(command)
    #print command
    # sendUnknown(addr)

