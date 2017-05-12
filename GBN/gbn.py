#encode "utf-8"

from select import select

seqLen = 1 #in bytes
frameDataLen = 1024 #in bytes

def gbnSend(data, s, addr):
  frames = createDataFrame(data)
  window = []
  maxWindowSize = (1 << (seqLen * 8)) - 1
  #装填初始数据到窗口
  tail = 0
  while tail < maxWindowSize:
    try:
      window.append(frames.next())
      tail += 1
    except Exception, e:
      print e
      break
  
  #开始发送数据
  cur = 0
  head = 0
  while head < tail:
    #将窗口中未确认的数据全部发送
    while cur < tail:
      s.sendto(window[cur % maxWindowSize], addr)
      cur += 1
      
    #等待ACK
    ready = select([s], [], [], 3)
    if ready[0]: #收到ACK，滑动窗口
      ack = parseFrame(s.recvfrom(2048))[0]
      slideSize = ack - (tail % maxWindowSize) + 1
      while slideSize:
        try:
          window[head % maxWindowSize] = frames.next()
        except Exception, e:
          print e
          head += slideSize
          break
        head += 1
        slideSize -= 1
    else:        #超时,进行重传
      cur = head
    
def gbnRecv(s, pACK = 1):
  data = s.recvfrom(bufferSize)
  s.sendto(createAckFrame(parseFrame(data[0])[0]), frame[1])
  
def createDataFrame(data):
  dataLen = len(data)
  seqNum = 0
  offset = 0
  while offset < dataLen:
    # 写入序列号
    frame = itob(seqNum)
      
    #写入数据
    frame += bytearray(data[offset:offset + frameDataLen])
    
    #写入结束标识
    frame.append(0)
    
    seqNum = (seqNum + 1) % (1 << (seqLen * 8))
    offset += frameDataLen
    yield frame

def parseFrame(frame):
  seqNum = btoi(frame[:seqLen])
  data = frame[seqLen:len(frame) - 1]
  
  return (seqNum, data)
  
def createAckFrame(seqNum):
  frame = itob(seqNum)
  frame.append(0)
  return frame
  
def itob(x):
  b = bytearray(0)
  if x == 0:
    b.append(0)
  while x:
    b.insert(0,x&0xFF)
    x >>= 8
  return b
  
def btoi(b):
  i = 0
  for c in b:
    i = (i << 8) + int(c)
  return i