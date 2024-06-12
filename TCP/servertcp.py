import socket
import struct
import threading


class Server:
    def __init__(self,serverIP,serverPort):
        self.serverIP=serverIP
        self.serverPort=serverPort
        self.tcpSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.tcpSocket.bind((self.serverIP,self.serverPort))
        self.tcpSocket.listen(5)

    def send_response(self,packet):
            while True:
                type=int.from_bytes(packet.recv(2),'big')

                if not type:
                    break

                if type== 1:
                    N=int.from_bytes(packet.recv(4),'big')
                    sendType=2
                    bytesType=sendType.to_bytes(2,'big')
                    packet.sendall(bytesType)

                elif type==3:
                    length=int.from_bytes(packet.recv(4),'big')
                    data=packet.recv(length).decode('utf-8')
                    reversed_data=data[::-1]
                    sendType=4
                    responese=sendType.to_bytes(2,'big')+len(reversed_data).to_bytes(4,'big')+reversed_data.encode('utf-8')
                    packet.sendall(responese)
            packet.close()

    def start(self):
        while True:
            packet,addr=self.tcpSocket.accept()
            handler=threading.Thread(target=self.send_response,args=(packet,))
            handler.start()

if __name__=='__main__':
    server=Server('127.0.0.1',12345)
    server.start()

