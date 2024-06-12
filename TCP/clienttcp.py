import socket
import struct
import random

class Client:
    def __init__(self,serverIP,serverPort,filename,Lmin,Lmax):
        self.serverIP=serverIP
        self.serverPort=serverPort
        self.filename=filename
        self.Lmin=Lmin
        self.Lmax=Lmax
        self.tcpSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def send_file(self):
        with open(self.filename, 'r') as f:
            content = f.read()

        blocks = []
        start = 0
        while start < len(content):
            block_size = random.randint(self.Lmin, self.Lmax)
            block = content[start:start + block_size]
            blocks.append(block)
            start += block_size

        N = len(blocks)  #要发送的Initialization报文数量
        self.tcpSocket.connect((self.serverIP,self.serverPort))
        self.send_initialzation(N) #发送请求报文
        response=int.from_bytes(self.tcpSocket.recv(2),'big')
        if response!=2:
            print("未接收到agree报文")
            return

        reversed_content = ''
        for i, block in enumerate(blocks):
            self.send_reverseRequest(block)
            response_type = int.from_bytes(self.tcpSocket.recv(2),'big')
            reversed_length = int.from_bytes(self.tcpSocket.recv(4), 'big')
            reversed_data = self.tcpSocket.recv(reversed_length).decode('utf-8')
            print(f'第{i + 1}块，反转的文本: {reversed_data}')
            reversed_content += reversed_data

        with open('reversed_output.txt', 'w') as f:
            f.write(reversed_content)

        self.tcpSocket.close()


    def send_initialzation(self,N):
        type=1
        initial_str=struct.pack('!HI',type,N)
        self.tcpSocket.sendall(initial_str)

    def send_reverseRequest(self,str):
        type=3
        estr=str.encode()
        length=len(estr)
        request_str=struct.pack("!HI",type,length)+estr
        self.tcpSocket.sendall(request_str)

if __name__=="__main__":
    serverIP=input("输入ServerIP：")
    serverPort=int(input("输入ServerPort："))
    filename=input("输入ASCII文件路径：")
    Lmin=int(input("数据块的最小长度："))
    Lmax=int(input("数据块的最大长度："))
    client=Client(serverIP,serverPort,filename,Lmin,Lmax)
    client.send_file()