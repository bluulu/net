import socket
import struct
import time
import random
import string
import statistics

class Client:
    def __init__(self,serverIp,serverPort):
        self.serverIp=serverIp
        self.serverPort=serverPort
        self.udpSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    # 模拟TCP建立过程
    def Creat_link(self):
        self.udpSocket.sendto(b'SYN',(self.serverIp,self.serverPort))
        response,_=self.udpSocket.recvfrom(1024)
        if response==b'ACK':
            print("链接已经建立 开始传输数据")
            return True
        else:
            print("链接建立失败")
            return False

    #发送、接收数据包
    def packets(self):
        recv_packets=0 #接收到的udppackets
        send_packets=0 #发送的udppackets
        all_RTT=list() #所有RTT的记录
        all_Servertime=list() #所有系统时间的记录
        all_ServertimeStamp=list() #所有系统时间戳

        sequence_number=1 #序列号从1开始
        ver=2
        #发送12个数据包
        while sequence_number<13:
            loseNum=0 #丢包的次数
            while loseNum<=2:
                randomStr=self.random_seq() #随机生成字母序列
                sendTime=time.time() #时间戳
                sendPacket=self.creat_Packet(sequence_number,ver,sendTime,randomStr)
                self.udpSocket.sendto(sendPacket,(self.serverIp,self.serverPort))
                send_packets+=1
                self.udpSocket.settimeout(0.1) #设置超时时间

                try:
                    response,_=self.udpSocket.recvfrom(1024)
                    recv_seq,recv_ver,client_timestamp,server_timestamp,server_time=self.parse_response(response)
                    recv_packets+=1 #接收到的packets+1
                    RTT=1000*(time.time()-client_timestamp) #计算RTT
                    all_RTT.append(RTT)
                    all_ServertimeStamp.append(server_timestamp)
                    all_Servertime.append(server_time)
                    print(f"sequence no: {recv_seq}, ServerIP {self.serverIp} : Port {self.serverPort}, RTT: {RTT}")
                    sequence_number+=1
                    break
                except socket.timeout:
                    #发生丢包
                    loseNum+=1
                    print(f"sequence no: {sequence_number} , request timeout")

            if(loseNum>2):
                print("丢弃这个包")
                sequence_number+=1 #直接发下一个包
        #12个数据包全部发完
        print(f"收到的udppackets数量：{recv_packets}, 发送的udppackets数量：{send_packets}")
        print(f'丢包率：{1 - recv_packets / send_packets:.4f}')
        maxrtt = max(all_RTT)
        minrtt = min(all_RTT)
        avertt = sum(all_RTT) / len(all_RTT)
        startt = statistics.stdev(all_RTT)  # 求标准差
        #系统持续时间
        continueTime=all_ServertimeStamp[-1]-all_ServertimeStamp[0]
        print(f"全部数据包发送完毕,最大RTT：{maxrtt:.4f}, 最小RTT：{minrtt:.4f}, 平均RTT：{avertt:.4f}, RTT标准差：{startt:.4f}, 系统的整体响应时间：{continueTime:.4f}")
        print(f"系统开始时间: {all_Servertime[0]},系统结束时间: {all_Servertime[-1]}")

    #生成随机序列
    def random_seq(self):
        letters=string.ascii_letters
        return ''.join(random.choices(letters,k=192))

    #创建数据包
    def creat_Packet(self,sequence_number,ver,sendTime,randomStr):
        Packet=struct.pack('!HBd',sequence_number,ver,sendTime)
        return Packet+randomStr.encode()

    #解析响应报文
    def parse_response(self,response):
        header_size = struct.calcsize('!HBdd')
        seq_no, ver, client_timestamp, server_timestamp = struct.unpack('!HBdd', response[:header_size])
        server_time = response[header_size:header_size+8].decode()
        return seq_no, ver, client_timestamp, server_timestamp, server_time

    #模拟TCP关闭连接
    def Close_link(self):
        self.udpSocket.sendto(b'FIN',(self.serverIp,self.serverPort))
        self.udpSocket.close()

if __name__ == "__main__":
    serverIP=input("请输入您要连接的服务器IP：") #192.168.136.130
    serverPort=int(input("请输入端口号：")) #12345
    client = Client(serverIP, serverPort)
    if client.Creat_link():
        client.packets()
        client.Close_link()