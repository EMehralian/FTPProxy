import socket
import GUI


def Main():
    # form = GUI.client_GUI()
    host = '127.0.0.1'
    data_port = 3020
    control_port = 3021

    ControlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    DataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ControlSocket.connect((host, control_port))
    DataSocket.connect((host, data_port))

    # DataSocket.listen(4)
    # print("Waiting for connections from clients...")
    # (conn, (ip, port)) = DataSocket.accept()


    # response = conn.recv(2048).decode()
    # data = response
    # while len(response) > 0:
    #     response = DataSocket.recv(1000).decode()
    #     data += response
    #

    Flag = "False"

    while Flag == "False":
        username = input("username")
        password = input("password")
        auth = [username, password]
        auth = ','.join(auth)
        ControlSocket.send(auth.encode())
        Flag = ControlSocket.recv(1000).decode()

    message = input(" ? ")
    while message != 'q':
        MessageList = message.split()
        Order = MessageList[0]
        ControlSocket.send(message.encode())

        if Order == "LIST":
            response = DataSocket.recv(100).decode()
            data = response
            while len(response) > 0:
                response = DataSocket.recv(100).decode()
                data += response
            print(data)
        elif Order == "RETR":
            print("RETR")
        elif Order == "DELE":
            print("DELETED")
        elif Order == "RMD":
            print("RMD")
        print("finihsed")
        message = input(" ? ")


        # ControlSocket.send(message.encode())
        # data = ControlSocket.recv(1024).decode()
        #
        # print('Received from server: ' + data)

    ControlSocket.close()


if __name__ == '__main__':
    Main()
