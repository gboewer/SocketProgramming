```py
# Server-address:
# IP address: 143.47.184.219
# Port number: 5378

import socket
from threading import Thread

SERVERIP = "143.47.184.219"
SERVERPORT = 5378 
SERVERADDRESS = (SERVERIP, SERVERPORT)
SOCKETLISTENSIZE = 4096

def sendMsg(recipient, msg):
    apiMsg = 'SEND {} {}\n'.format(recipient, msg)
    sock.sendall(apiMsg.encode('utf-8'))

    res = sock.recv(SOCKETLISTENSIZE).decode("utf-8")
    if(res == 'SEND-OK\n'):
        print('Message sent succesfully\n')
    elif(res == 'UNKNOWN\n'):
        print('Failed to send message: Unknown recipient\n')

def login():
    # If busy, say its busy  and do somthing else idk
    usernameAccepted = False
    while not usernameAccepted:
        username = input('Please enter a unique username: ')

        print('Logging in as {}'.format(username))

        req = 'HELLO-FROM {}\n'.format(username)
        sock.sendall(req.encode('utf-8'))

        res = sock.recv(SOCKETLISTENSIZE).decode("utf-8")
        if(res == 'IN-USE\n'):
            print('Username is already in use, please choose another.')
        elif(res == 'BUSY\n'):
            print('Server is currently busy, please try again later')
            raise Exception
        else:
            print('Login successful')
            usernameAccepted = True

def printUserList():
    sock.sendall('WHO\n'.encode('utf-8'))
    res = sock.recv(SOCKETLISTENSIZE).decode("utf-8")
    if(res.split(' ', 1)[0] == 'WHO-OK'):
        usernames = res.split(' ', 1)[1]
        print(usernames)
    else: print('Failed to get userlist from server')

def receiveMessages():
    pass

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(SERVERADDRESS)

    try:
        login()        

        running = True

        print("""\nCommands:\n- !who: provides a list of users that are currenty online\n- @<recipient> <message>: send a message to a recipient thats currently online\n- !quit: quit the chat client\n""")

        while(running):
            cmd = input('Command: ')
            if cmd == '!who':
                printUserList()
            elif cmd[0] == '@':
                recipient = cmd.split()[0][1:]
                msg = cmd.split(' ', 1)[1]
                sendMsg(recipient, msg)
            elif cmd == '!quit':
                running = False
            else: print('Command unknown')

    except OSError as err:
        print(err)

    except Exception:
        pass