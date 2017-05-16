#encode "utf-8"
import socket
import gbn
import datetime
from select import select

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", 23333))

def sendTime(addr):
  gbn.gbnSend(datetime.datetime.isoformat(datetime.datetime.today()), s, addr)

def sendFile(addr, p):
  f = open("L_versionA.mp3","rb")
  buffer = f.read()
  f.close()

  gbn.gbnSend(buffer, s, addr, p)
  
def sendError(addr):
  gbn.gbnSend("Unknown Command", s, addr)
  
while True:
  print u"接收指令中..."
  result = s.recvfrom(2048)
  command = result[0].split(" ")
  addr = result[1]
  
  if command[0] == "-time":
    sendTime(addr)
  elif command[0] == "-testgbn":
    try:
      p = float(command[1])
    except Exception, e:
      print e
      p = 1.0
    sendFile(addr, p)
  else:
    sendError(addr)

