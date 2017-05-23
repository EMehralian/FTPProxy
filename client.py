import socket


class client:
    def Main(self):
        host = '127.0.0.1'
        data_port = 3020
        control_port = 3021

        ControlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        DataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ControlSocket.connect((host, control_port))
        DataSocket.connect((host, data_port))

        Flag = "False"

        while Flag == "False":
            username = input("username")
            password = input("password")
            auth = [username, password]
            auth = ','.join(auth)
            ControlSocket.send(auth.encode())
            Flag = ControlSocket.recv(1000).decode()

        message = input(" ? ")
        while True:
            if message:
                MessageList = message.split()
                Order = MessageList[0]
            else:
                Order = ""
                MessageList = []
            ControlSocket.send(message.encode())
            if Order == "QUIT":
                break
            if Order == "LIST":
                size = int(DataSocket.recv(100).decode())
                data = DataSocket.recv(int(size)).decode()
                dataList = data.split('&')
                for item in dataList:
                    print(item)
            elif Order == "RETR":
                with open("client/" + MessageList[1], 'wb') as f:
                    print('file opened')
                    size = int(DataSocket.recv(100).decode())
                    data = DataSocket.recv(int(size))
                    f.write(data)
                f.close()
                print("RETR")
            elif Order == "DELE":
                controlMessage = DataSocket.recv(1000).decode()
                print(controlMessage)
            elif Order == "RMD":
                controlMessage = DataSocket.recv(1000).decode()
                print(controlMessage)
                print("RMD")
            message = input(" ? ")


if __name__ == '__main__':

    client.Main(client)
