#encoding: utf-8
from socket import *
from SocketServer import TCPServer, StreamRequestHandler, ThreadingMixIn
from select import select
import re
import time
import sys, os
class proxyServer(ThreadingMixIn,TCPServer):pass

class Handler(StreamRequestHandler):

    def recvData(self, s):
        data = ""
        while True:
            #利用select设置超时
            #因为windows下recv不一定一次性收到全部数据
            #所以需要方法判断数据已经收全
            #这里使用最简单的超时方法
            ready = select([s],[],[],2)
            if ready[0]:
                buf = s.recv(4096)
                data += buf
                #此处若仅使用\r\n\r\n来判断数据接收完毕会死掉
                #所以仍然使用超时机制
                if buf.endswith("\r\n\r\n"):break 
            else:
                break

            #buf = s.recv(4096)
            #data += buf
            #if buf.endswith("\r\n\r\n"):break
        return data

    def handle(self):
        #接收客户端数据
        try:
            data = self.recvData(self.request)
        except Exception, e:
            print u"接收服务器数据失败", e
            return

        firstLine = data.split("\r\n")[0]
        if firstLine.startswith("CONNECT"):return

        #重定向url
        for pat in redirectMap:
            items = firstLine.split(" ")
            url = items[1]
            if re.match(pat, url):  
                url = re.sub(pat, r"http://" + redirectMap[pat] + r"/", url)
                hostPatten = re.compile(r"Host: (\S+):?(\d+)?\r\n")
                data = re.sub(hostPatten,r"Host: " + redirectMap[pat] + r"\r\n", data)
                data = items[0] + " " + url+ " " + items[2] + data[len(firstLine):]

        print items[0] + " " + url+ " " + items[2]
        #解析服务器地址
        port = 80
        try:
            host = re.search(r"Host: (\S+):?(\d+)?\r\n",data).group(1)
        except Exception, e:
            print u"解析服务器地址失败", e
            return

        #过滤网站
        for pat in blockList:
            if re.match(pat, host):
                print u"请求的网站不允许访问"
                self.request.send(r"");
                return

        #连接目标服务器
        s = socket(AF_INET, SOCK_STREAM)
        try:
            addr = getaddrinfo(host, port)
            s.connect(addr[0][4])
        except Exception, e:
            print u"连接服务器失败", e
            s.close()
            return

        #向服务器发送数据
        try:
            s.send(data)
        except Exception, e:
            print u"向服务器发送数据失败", e
            return

        #接收服务器应答
        try:
            data = self.recvData(s)
        except Exception, e:
            print u"接收应答失败", e
            return

        #应答转发给客户端
        try:
            self.request.send(data)
        except Exception, e:
            print u"将应答发送给客户端失败", e

def showHelp():
    print u"用法: proxy.py [-b blockListPath] [-r redirectMapPath] [-p portNumber]"
    return

def loadBlockList():
    blockList = []
    f = open(blockListPath, 'r')
    while True:
        line = f.readline()
        if len(line) == 0: break
        if line.endswith("\n"):
            line = line[:len(line) - 1]
        blockList.append(line)
    f.close()
    return blockList
    
def loadRedirectMap():
    redirectMap = {}
    f = open(redirectMapPath, 'r')
    while True:
        line = f.readline()
        if len(line) == 0: break
        if line.endswith("\n"):
            line = line[:len(line) - 1]
        line = line.split(' ');
        redirectMap[line[0]] = line[1]
    f.close()
    return redirectMap

blockListPath = "block.txt"
if not os.path.isfile(blockListPath): f = open("block.txt",'w');f.close()
redirectMapPath = "redirect.txt"
if not os.path.isfile(redirectMapPath): f = open("redirect.txt",'w');f.close()
port = 10240
i = 1

try:
    argvLen = len(sys.argv)
    while(i < argvLen):
        if sys.argv[i] == "-b":blockListPath = sys.argv[i + 1]
        elif sys.argv[i] == "-r":redirectMapPath = sys.argv[i + 1]
        elif sys.argv[i] == "-p":port = int(sys.argv[i+1])
        else: raise Exception
        i += 2
except Exception, e:
    showHelp()
    exit()

if not os.path.isfile(blockListPath): print u"指定的屏蔽列表不存在！";exit()
blockList = loadBlockList()
if not os.path.isfile(redirectMapPath): print u"指定的重定向列表不存在！";exit()
redirectMap = loadRedirectMap()

print u"代理服务器初始化中..."
try:
    server = proxyServer(("",port), Handler)
except Exception, e:
    print u"初始化失败", e
    exit()

print u"初始化完成！开始监听 端口:", port
server.serve_forever()