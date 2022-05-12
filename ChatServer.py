''' 
- connect multiple clients and forward messages 
- multiple open connections at the same time -> keep checking all of them for incoming data
- support at least 64 clients simultaneuosly
- implement chat protocol
'''

import socket
# import threading
import os
from _thread import *

HOST = "127.0.0.1"
PORT = 65432

usersOnline = []
connections = []

def handshake(req, conn):
    # DEBUG
    print("Handshake function")
    
    username = req.split(" ", 1)[1]
    for i in range(len(usersOnline)):
        if(username == usersOnline[i]):
            res = "IN-USE\n"
        else:
            usersOnline.append(username)
            res = "HELLO " + username 
            break
            # make new thread for new connection?
            # connections = threading.Thread(target=incoming, daemon=True)
            # connections.start()
        # res = "BUSY\n"
    '''if len(usersOnline) == 0:
        usersOnline.append(username)
        res = "HELLO " + username + '\n' '''
    
    usersOnline.append(username)
    res = "HELLO " + username 
    print("Response: " + res)

    # conn.sendall(res.encode("utf-8"))
    conn.send(str.encode(res))
        

def listUsers(conn):
    for i in usersOnline:
        if i == 0:
            list = i + ','
        elif i == len(usersOnline - 1):
            list += i
        else: 
            list += i + ','
    res = "WHO-OK " + list 
    conn.send(str.encode(res))

def respondSend(req, conn):
    user = req.split(" ", 2)[1]
    message = req.split(" ", 2)[2]
    userLogIn = False
    for i in usersOnline:
        if user == usersOnline[i]:
            userLogIn = True
            index = i
    if userLogIn == False:
        res = "UNKNOWN\n" 
    else:
        sendMsg = "DELIVERY " + user + message 
        conn = connections[index]
        conn.send(str.encode(sendMsg))
        res = "SEND-OK\n" # send was succesful
    
    conn.send(str.encode(res))


def incoming(conn, addr):
    # DEBUG
    print("Incoming function")
    while True:
        req = conn.recv(4096).decode("utf-8")

        if(req.split(" ", 1)[0] == "HELLO-FROM"):
            connections.append(conn)
            handshake(req, conn)
        elif(req == "WHO\n"):
            listUsers(conn)
        elif(req.split(" ", 1)[0] == "SEND"):
            respondSend(req, conn)
        else:
            res = "BAD-RQST-HDR\n" # error in header
            conn.send(str.encode(res))

        # error in Body
        # res = "BAD-RQST-BODY\n"
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
        print("New Thread connected to: "+ addr[0] + ':' + str(addr[1]))

        start_new_thread(incoming, (conn, addr))

    s.close()
