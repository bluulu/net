import socket
import struct
import time
import random
import string
import threading

class Server:
    def __init__(self,serverIP,serverPort):
        self.serverIP=serverIP
        self.serverPort=serverPort
        self.udpsocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.udpsocket.bind((self.serverIP,self.serverPort))

    #回复
    def Response(self,data,addr):
        if data == b"SYN":
            self.udpsocket.sendto(b"ACK",addr)
        elif data == b"FIN":
            print(f"关闭连接：{addr}")
        else:
            if random.random() >= 0.3:
                #丢包模拟
                seq_no,ver,client_timestamp=self.parse_request(data)
                server_time=time.strftime("%H:%M:%S",time.localtime())
                server_timestamp=time.time() #系统的时间戳
                response=self.creat_response(seq_no,ver,client_timestamp,server_timestamp,server_time)
                self.udpsocket.sendto(response,addr)

    #解析request报文
    def parse_request(self,packet):
        header_size=struct.calcsize('!HBd')
        seq_no, ver ,client_timestamp=struct.unpack('!HBd',packet[:header_size])
        return seq_no,ver,client_timestamp

    #构建response报文
    def creat_response(self,seq_no,ver,client_timestamp,server_timestamp,server_time):
        header=struct.pack("!HBdd",seq_no,ver,client_timestamp,server_timestamp)
        response=header+server_time.encode()+self.random_seq().encode()
        return response

    #随机序列
    def random_seq(self):
        letters=string.ascii_letters
        return ''.join(random.choices(letters,k=176))

    def start(self):
        while True:
            data,addr=self.udpsocket.recvfrom(1024)
            threading.Thread(target=self.Response,args=(data,addr)).start()

if __name__ == "__main__":
    server=Server("127.0.0.1",12345)
    server.start()