import socket
import threading
import time

# SERVERIP = "143.47.184.219"
# SERVERPORT = 5378 
SERVERIP = "127.0.0.1"
SERVERPORT = 65432
SERVERADDRESS = (SERVERIP, SERVERPORT)
SOCKETLISTENSIZE = 4096


def sendMsg(recipient, msg):
    apiMsg = "SEND {} {}\n".format(recipient, msg)
    sock.sendall(apiMsg.encode("utf-8"))


def printUserList():
    sock.sendall("WHO\n".encode("utf-8"))
    

def receiveMessages(): 
    while(True):
        res = sock.recv(SOCKETLISTENSIZE).decode("utf-8")
        
        if(res.split(" ", 1)[0] == "WHO-OK"):
            usernames = res.split(" ", 1)[1]
            print(usernames)
        elif(res.split(" ", 1)[0] == "DELIVERY"):
            print("New Message from ", end = "")
            sender = res.split(" ", 2)[1]
            msg = res.split(" ", 2)[2]
            print(sender,":", msg)
        elif(res == "SEND-OK\n"):
            print("Message sent succesfully\n")
        elif(res == "UNKNOWN\n"):
            print("Failed to send message: Unknown recipient\n")


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(SERVERADDRESS)

    rec = threading.Thread(target=receiveMessages, daemon=True)

    try:     
        usernameAccepted = False
        while not usernameAccepted:
            username = input("Please enter a username: ")

            req = "HELLO-FROM {}\n".format(username)
            sock.sendall(req.encode("utf-8"))

            res = sock.recv(SOCKETLISTENSIZE).decode("utf-8")
            if(res == "IN-USE\n"):
                print("Username is already in use, please choose a different one.")
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(SERVERADDRESS)
            elif(res == "BUSY\n"):
                print("Server is currently busy, please try again later")
                raise Exception
            elif(res == "HELLO " + username + '\n'):
                print("Login successful")
                usernameAccepted = True
            elif(res == "BAD-RQST-HDR\n"):
                print("Error. Contact the administrator.")
            elif(res == "BAD-RQST-BODY\n"):
                print("Invalid input. Please try again.")
            elif(not res):
                print("Connection terminated. Socket is closed.")
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        running = True

        rec.start()

        print("""\nCommands:\n- !who: provides a list of users that are currenty online\n- @<recipient> <message>: send a message to a recipient thats currently online\n- !quit: quit the chat client\n""")

        while(running):
            time.sleep(0.3)
            cmd = input("\nCommand: ")
            if cmd == "!who":
                printUserList()
            elif cmd[0] == '@':
                recipient = cmd.split()[0][1:]
                msg = cmd.split(' ', 1)[1]
                sendMsg(recipient, msg)
            elif cmd == "!quit":
                running = False
                sock.close()
            else: print("Command unknown")

    except OSError as err:
        print(err)

    except Exception:
        pass