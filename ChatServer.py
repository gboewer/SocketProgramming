import socket
import threading

HOST = "127.0.0.1"
PORT = 65432

def listenForConnections():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    while(True):
        conn, addr = sock.accept()
        if(len(connections) > 64):
            print('Cant connect: Number of connections exceeded max')
        else:
            connections.append(conn)
            users.append('')
        
connections = {}
users = {}

connectThread = threading.Thread(target=listenForConnections)
connectThread.start()

def handleCall(msg, connID):
    if(msg.split(" ", 1)[0] == "HELLO-FROM"):
        user = msg.split(" ", 1)[1]
        handshake(connID, user)
    elif(msg.split(" ", 1)[0] == "WHO\n"):
        sendUserlist(connID)
    elif(msg.split(" ", 1)[0] == "SEND"):
        pass

def handshake(connID, user):
    users[connID] = user
    res = 'HELLO {user}'.encode('utf-8')
    connections[connID].sendall(res)

def sendUserlist(connID):
    usrListStr = 'WHO-OK '
    for user in users:
        usrListStr.append(user + ',')
    usrListStr = usrListStr[:-1]
    res = usrListStr.encode('utf-8')
    connections[connID].sendall(res)

def handleMessage(connID, user, msg):
    for i in range(len(users)):
        if(user == users[i]):
            deliveryMsg = 'DELIVERY {users[connID]} {msg}'
            res = deliveryMsg.encode('utf-8')
            connections[i].sendall(res)