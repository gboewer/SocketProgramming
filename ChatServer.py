import socket
from _thread import *

HOST = "127.0.0.1"
PORT = 65432
MAX_CLIENTS = 64

usersOnline = []
connections = []

def handshake(req, conn):
    reqSplit = req.split(" ", 1)
    if(len(reqSplit) != 2):
        raise Exception("BAD-RQST-BODY\n")
    username = reqSplit[1][:-1]
    if len(usersOnline) >= MAX_CLIENTS:
        raise Exception("BUSY\n")
    
    for i in range(len(usersOnline)):
        if(username == usersOnline[i]):
            raise Exception("IN-USE\n")
    
    usersOnline.append(username)
    res = "HELLO " + username + '\n' 

    conn.send(str.encode(res))
        

def listUsers(conn):
    list = ''
    for i in range(len(usersOnline)):
        list += usersOnline[i] + ','
    list = list[:-1]
    res = "WHO-OK " + list + '\n'
    conn.send(str.encode(res))

def respondSend(req, conn):
    reqSplit = req.split(" ", 2)
    user = reqSplit[1]
    message = reqSplit[2]
    found = False
    for i in range(len(usersOnline)):
        if user == usersOnline[i]:
            found = True
            for j in range(len(connections)):
                if conn == connections[j]:
                    sender = usersOnline[j]
                    break
            sendMsg = "DELIVERY " + sender + " " + message 
            receiver = connections[i]
            receiver.send(str.encode(sendMsg))
            res = "SEND-OK\n"
    
    if not found:
        raise Exception("UNKNOWN\n")

    conn.send(str.encode(res))


def incoming(conn, addr):
    try:
        while True:
            req = conn.recv(4096).decode("utf-8")
            try:
                if(req[0] == 'S'):
                    count = 0
                    for i in range(len(req)):
                        if req[i] == " ":
                            count += 1
                    if(count < 2):
                        raise Exception("BAD-RQST-BODY\n")
                if(req.split(" ", 1)[0] == "HELLO-FROM"):
                    connections.append(conn)
                    handshake(req, conn)
                elif(req == "WHO\n"):
                    listUsers(conn)
                elif(req.split(" ", 1)[0] == "SEND"):
                    respondSend(req, conn)
                else:
                    res = "BAD-RQST-HDR\n" 
                    conn.send(str.encode(res))
            
            except Exception as errorMsg:
                conn.send(str.encode(str(errorMsg)))
    
    except BrokenPipeError:
        for i in range(len(connections)):
            if conn == connections[i]:
                break

        usersOnline.pop(i)
        connections.pop(i)
        conn.close()

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    
    try:
        s.bind((HOST,PORT))
    except socket.error as e:
        print(str(e))
    print("Socket is listening...")
    s.listen()

    while True:
        conn, addr = s.accept()
        start_new_thread(incoming, (conn, addr))

    s.close()
