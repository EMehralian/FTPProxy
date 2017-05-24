import os
import socket
from threading import Thread
from os import listdir
from os.path import isfile, join
import re
from time import gmtime, strftime
import time
from datetime import datetime


class ClientThread(Thread):
    def __init__(self, ip, port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port

        clientsLog.write(
            strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "[+] New server socket thread started for " + ip + ":" + str(
                port) + "\n")
        print("[+] New server socket thread started for " + ip + ":" + str(port))

    def run(self):
        Flag = "false"
        superUser = False
        while Flag == "false":
            data = conn.recv(2048).decode()
            print(data)
            username = data.split(',')[0]
            password = data.split(',')[1]
            if (username == "root" and password == "root") or (username == "Admin" and password == "Admin"):
                conn.send("True".encode())
                Flag = "True"
                superUser = True
                clientsLog.write(ip + ":" + str(port) + "correctly authenticated" + "\n")
            elif self.check_auth(username, password) == "true":
                conn.send("True".encode())
                Flag = "True"
            else:
                conn.send("False".encode())
                clientsLog.write(ip + ":" + str(port) + "failed to authenticate" + "\n")
        while True:
            data = conn.recv(100).decode()
            if (not data):
                print("connection to socket has been missed!    ")
                break
            else:
                print("Server received data:", data)
                if data:
                    MessageList = data.split()
                    Order = MessageList[0]
                else:
                    Order = ""

                if Order == "QUIT":
                    clientsLog.write(ip + ":" + str(port) + "Order: Quit" + "\n")
                    break
                elif Order == 'LIST':
                    ClientThread.list_server_files(self, port, superUser)
                    clientsLog.write(ip + ":" + str(port) + "Order: LIST" + "\n")
                    print("List")
                elif Order == 'RETR':
                    MessageList = data.split()
                    ClientThread.retrive_file(self, MessageList[1], port, superUser)
                    clientsLog.write(ip + ":" + str(port) + "Order: Retrive file:" + MessageList[1] + "\n")
                    print("retrive")
                elif Order == 'DELE':
                    MessageList = data.split()
                    ClientThread.delete_file(self, MessageList[1], superUser)
                    clientsLog.write(ip + ":" + str(port) + "Order: Deleted file:" + MessageList[1] + "\n")
                    print("delete")
                elif Order == 'RMD':
                    ClientThread.delete_all_cached_files(self, superUser)
                    clientsLog.write(ip + ":" + str(port) + "Order: Deleted all cached file:" + "\n")
                    print("RMD")

    def check_auth(self, user, passs):
        with open("auth.txt", 'r+') as auth:
            for line in auth:
                data = line.split(",")
                dataa = data[1].split("$")
                print(data)
                print(dataa)
                if data[0] == user and dataa[0] == passs:
                    print("password maches")
                    return "true"
                elif data[0] == user and data[1] != passs:
                    print("password does not maches")
                    return "false"
            print("new user")
            auth.write(user + "," + passs + "$")
            return "true"

    def retrive_file(self, file_name, clientport, superUser):
        if not superUser:
            if re.match('secret_', file_name):
                print("access denied")
                ClientThread.send_file_from_proxy(self, file_name, False)
                return
        host = socket.gethostbyname('ceit.aut.ac.ir')
        request = "GET /~94131090/CN1_Project_Files/" + str(file_name) + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
        proxy_files = self.local_files()
        print("going to check")
        for file in proxy_files:
            if file == file_name:
                print("in local")
                ClientThread.send_file_from_proxy(self, file_name, True)
                break
        print("connecting to server")
        serverLog.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "|" + ip + ":" + str(
            clientport) + "Trying to connect to AUT server" + "\n")
        host = socket.gethostbyname('ceit.aut.ac.ir')
        port = 80
        ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ServerSocket.connect((host, port))
        ServerSocket.send(request.encode())
        with open("Cache/" + file_name, 'wb') as f:
            print('receiving data...')
            data = ServerSocket.recv(1024)
            linend = re.compile(b'\r\n\r\n')
            data = (linend.split(data, 1))
            data = data[1]
            f.write(data)
            while True:
                print('receiving data...')
                data = ServerSocket.recv(1024)
                if not data:
                    break
                f.write(data)
        serverLog.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "|" + ip + ":" + str(
            clientport) + "read" + file_name + " from AUT server" + "\n")
        ClientThread.send_file_from_proxy(self, file_name, True)

    def send_file_from_proxy(self, file_name, flag):
        proxy_files = self.local_files()
        if not (file_name in proxy_files) or not flag:
            data = "the file dose not exists or you dont have permition to access it "
            dataConn.send(str(len(data)).encode())
            dataConn.send(data.encode())
        else:
            print("start to send")
            f = open("Cache/" + file_name, 'rb')
            l = f.read(1024)
            data = l
            while (l):
                # dataConn.send(l)
                l = f.read(1024)
                data += l
            print("file readed")
            dataConn.send(str(len(data)).encode())
            print(len(data))

            dataConn.send(data)
            f.close()

    def local_files(self):
        mypath = "Cache/"
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        return onlyfiles

    def list_server_files(self, port, superUser):
        serverLog.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "|" + ip + ":" + str(
            port) + "Trying to connect to AUT server" + "\n")
        print("connecting to server")
        host = socket.gethostbyname('ceit.aut.ac.ir')
        port = 80
        request = "GET /~94131090/CN1_Project_Files/ HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
        ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ServerSocket.connect((host, port))
        ServerSocket.send(request.encode())
        result = ServerSocket.recv(1000).decode()
        response = result
        while len(response) > 0:
            response = ServerSocket.recv(1000).decode()
            result += response
        print(result)
        if (result[9:12] == "200"):
            urls = re.findall(r'href=[\'"]?([^\'" >]+)', result)
            print(urls)
        else:
            print("faild to connect to AUT server")
            urls = ""
        serverLog.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "|" + ip + ":" + str(
            port) + "got list of files form AUT server" + "\n")
        if (len(urls) > 5):
            urls.pop(0)
            urls.pop(0)
            urls.pop(0)
            urls.pop(0)
            urls.pop(0)
        print(urls)
        urls_copy = urls
        if not superUser:
            secretFiles = []
            for item in urls:
                if re.match('secret_', item):
                    secretFiles.append(item)
            urls = [x for x in urls_copy if x not in secretFiles]
        filelist = '&'.join(urls)
        listSize = len(filelist)
        print(listSize)
        dataConn.send(str(listSize).encode())
        time.sleep(.3)
        dataConn.send(filelist.encode())
        ServerSocket.close()

    def delete_file(self, file_name, superUser):
        if not superUser:
            if re.match('secret_', file_name):
                print("access denied")
                return
        local_files_list = self.local_files()
        print(local_files_list)
        if (file_name in local_files_list):
            os.remove("Cache/" + file_name)
            dataConn.send("selected file successfully deleted".encode())
        else:
            print("no such file in cache proxy!")
            dataConn.send("no such file in cache proxy! ".encode())

    def delete_all_cached_files(self, superUser):
        local_files_list = self.local_files()
        for file in local_files_list:
            self.delete_file(file, superUser)

    def update(self):
        local_files_list = self.local_files()
        for item in local_files_list:
            if item[1] < datetime.now():
                host = socket.gethostbyname('ceit.aut.ac.ir')
                request = "GET /~94131090/CN1_Project_Files/" + str(
                    item[0]) + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
                port = 80
                ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                ServerSocket.connect((host, port))
                ServerSocket.send(request.encode())
                with open("Cache/" + item[0], 'wb') as f:
                    print('receiving data...')
                    data = ServerSocket.recv(1024)
                    linend = re.compile(b'\r\n\r\n')
                    data = (linend.split(data, 1))
                    data = data[1]
                    f.write(data)
                    while True:
                        print('receiving data...')
                        data = ServerSocket.recv(1024)
                        if not data:
                            break
                        f.write(data)
                serverLog.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "|" + ip + ":" + "read" + item[
                    0] + " from AUT server" + "\n")


# Multithreaded Python server : TCP Server Socket Program Stub
TCP_IP = '172.20.10.10'
data_port = 3020
control_port = 3021
clientsLog = open("clientsLog.txt", "a")
serverLog = open("serverLog.txt", "a")
clientsLog.write("server Started" + "\n")
BUFFER_SIZE = 20  # Usually 1024, but we need quick response 

controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
controlSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
controlSocket.bind((TCP_IP, control_port))
threads = []

dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dataSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
dataSocket.bind((TCP_IP, data_port))

while True:
    controlSocket.listen(4)
    dataSocket.listen(4)
    print("Waiting for connections from clients...")
    (conn, (ip, port)) = controlSocket.accept()
    (dataConn, (dip, Dport)) = dataSocket.accept()
    newthread = ClientThread(ip, port)
    newthread.start()
    threads.append(newthread)

clientsLog.close()
