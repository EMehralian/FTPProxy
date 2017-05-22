import os
import socket
from threading import Thread
from os import listdir
from os.path import isfile, join
import re


class ClientThread(Thread):
    def __init__(self, ip, port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        print("[+] New server socket thread started for " + ip + ":" + str(port))

    def run(self):
        Flag = "false"
        while Flag =="false":
            data = conn.recv(2048).decode()
            print(data)
            username = data.split(',')[0]
            password = data.split(',')[1]
            if username == "root" and password == "root":
                conn.send("True".encode())
                Flag = "True"
            else:
                conn.send("False".encode())
        while True:
            data = conn.recv(2048).decode()

            print("Server received data:", data)
            MessageList = data.split()
            Order = MessageList[0]
            if Order == 'Quit':
                break
            if Order == 'LIST':
                ClientThread.list_server_files(self)
                print("List")
            if Order == 'RETR':
                ClientThread.retrive_file(self, MessageList[1])
                print("retrive")
            if Order == 'DELE':
                ClientThread.delete_file(self, MessageList[1])
                print("delete")
            if Order == 'RMD':
                ClientThread.delete_all_cached_files(self)
                print("RMD")

                # MESSAGE = input("Server: Enter Response from Server/Enter Quit:")
                # if MESSAGE == 'Quit':
                #     break

                # conn.send(MESSAGE.encode())  # echo

    def retrive_file(self, file_name):
        host = socket.gethostbyname('ceit.aut.ac.ir')
        request = "GET /~94131090/CN1_Project_Files/" + str(file_name) + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
        proxy_files = self.local_files()
        print("going to check")
        for file in proxy_files:
            if file == file_name:
                print("in local")
                break

        print("connecting to server")
        host = socket.gethostbyname('ceit.aut.ac.ir')
        port = 80
        ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ServerSocket.connect((host, port))
        ServerSocket.send(request.encode())
        with open(file_name, 'wb') as f:
            while True:
                print('receiving data...')
                data = ServerSocket.recv(1024)
                re.sub(r'.*\n\n', '', data.decode())
                print('data=%s', (data))
                if not data:
                    break
                # write data to a file
                f.write(data)

    def local_files(self):
        mypath = "File/"
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        return onlyfiles

    def list_server_files(self):
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
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', result)
        urls.pop(0)
        urls.pop(0)
        urls.pop(0)
        urls.pop(0)
        urls.pop(0)
        print(urls)
        ehsan = ','.join(urls)
        dataConn.send(ehsan.encode())
        ServerSocket.close()


    # def return_server_files(self, file_list):
    #     TCP_IP = '127.0.0.1'
    #     TCP_PORT = 6021
    #     BUFFER_SIZE = 20  # Usually 1024, but we need quick response
    #
    #     tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #     tcpServer.bind((TCP_IP, TCP_PORT))

    def delete_file(self, file_name):
        local_files_list = self.local_files()
        if (file_name in local_files_list):
            os.remove("File/" + file_name)
        else:
            print("no such file in cache proxy!")

    def delete_all_cached_files(self):
        local_files_list = self.local_files()
        for file in local_files_list:
            self.delete_file(file)


# Multithreaded Python server : TCP Server Socket Program Stub
TCP_IP = '127.0.0.1'
data_port = 3020
control_port = 3021

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
