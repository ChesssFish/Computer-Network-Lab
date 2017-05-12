#encode "utf-8"

from select import select
import ctypes
seqLen = 1 #in bytes
frameDataLen = 1024 #in bytes
#maxWindowSize = (1 << (seqLen * 8)) - 1
maxWindowSize = 50
MAX_BUFFER_LEN = 0x100000 #1MB

def gbnSend(data, s, addr, pSend = 1):
  # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  frames = createDataFrame(data)
  window = []
  
  #装填数据到窗口
  tail = 0
  while tail < maxWindowSize:
    try:
      window.append(frames.next())
      tail += 1
    except StopIteration:
      break
  
  for f in window: print "frame:" ,parseFrame(f)[0]
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
      response = s.recvfrom(2048)
      ackNum = parseFrame(response[0])[0]
      slideSize = abs(getPos(head, ackNum) - head) + 1
      
      print u"收到ACK", ackNum, u"滑动窗口", slideSize
      while slideSize:
        try:
          window[head % maxWindowSize] = frames.next()
        except StopIteration:
          head += slideSize
          break
        head += 1
        tail += 1
        slideSize -= 1
      
    else:        #超时,进行重传
      print "time out!"
      cur = head
def gbnRecv(s, pACK = 1):
  head = 0
  # fileBuffer = open("fileRecv", "wb")
  buffer = bytearray(MAX_BUFFER_LEN)
  dataLen = 0
  recived = [False] * maxWindowSize
  
  while True:
    #接收并解析数据帧
    recv = s.recvfrom(2048)
    seqNum, data = parseFrame(recv[0])
    addr = recv[1]
    
    #将数据写入缓存
    print head, seqNum
    pos = getPos(head, seqNum)
    buffer[pos * frameDataLen:pos * frameDataLen + frameDataLen] = data
    dataLen += len(data)
    
    #标识收到的数据帧
    windowIndex = getWindowIndex(head, seqNum)
    recived[windowIndex] = True
    
    #滑动接收窗口
    ack = head % (maxWindowSize + 1)
    while recived[head % maxWindowSize]:
      recived[head % maxWindowSize] = False;
      head += 1
      ack = head % (maxWindowSize + 1)
      
    #发送累计确认ACK
    s.sendto(createAckFrame(ack), recv[1])
    print "send ack:", ack
    
    #如果该帧数据长度小于定义的长度
    #说明是最后一帧
    #接收结束
    if len(data) < frameDataLen:
      break
  
  return (buffer[:dataLen], addr)
  
#根据数据窗口位置和序列号计算
#该数据帧在窗口中的位置
#head：当前窗口的起始位置
#seqNum: 序列号
def getWindowIndex(head, seqNum):
  return getPos(head, seqNum) % maxWindowSize #当前帧在窗口中的位置

#根据数据窗口位置和序列号计算
#该数据帧在整个文件中的位置
#head：当前窗口的起始位置
#seqNum: 序列号
def getPos(head, seqNum):                     
  headSeqNum = head % (maxWindowSize + 1)     #当前窗口位置的序列号
  return head + abs(headSeqNum - seqNum)      #当前帧在整个序列中的位置
  
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
    
    seqNum = (seqNum + 1) % (maxWindowSize + 1)
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
  b = bytearray(b)
  for c in b:
    i = (i << 8) + c
  return i