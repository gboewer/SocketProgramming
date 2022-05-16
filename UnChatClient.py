# ToDO
# change send and receive syntax to match UDP
# guaranteed delivery with acks
# make server resend data if error was detected

import socket
import threading
import time

SERVERIP = "143.47.184.219"
SERVERPORT = 5382
SERVERADDRESS = (SERVERIP, SERVERPORT)
SOCKETLISTENSIZE = 4096
SOCKETSEND = 1024
KEY = "0011"

def sendMsg(recipient, msg):
    keyLen = len(KEY)
    binary = (''.join(format(ord(x), 'b') for x in msg))

    appendZero = binary + '0'*(keyLen-1)
    remainder = mod(appendZero, KEY)

    result = binary + remainder

    apiMsg = "SEND {} {}\n".format(recipient, result)
    sock.sendto(apiMsg.encode(), SERVERADDRESS)

def xor(a,b):
    result = []

    for i in range(1, len(b)):
        if a[i] == b[i]:
            result.append('0')
        else:
            result.append('1')
    
    return ''.join(result)

def mod(divident, divisor):
    toXOR = len(divisor)
    temp = divident[0 : toXOR]

    while toXOR < len(divident):
        if temp[0] == '1':
            temp = xor(divisor, temp) + divident[toXOR]
        else:
            temp = xor('0'*toXOR, temp) + divident[toXOR]

        toXOR += 1

    if temp[0] == '1':
        temp = xor(divisor, temp)
    else: 
        temp = xor('0'*toXOR, temp)

    codeword = temp
    return codeword


def printUserList():
    sock.sendall("WHO\n".encode("utf-8"))  

def receiveMessages(): 
    while(True):
        res = sock.recv(SOCKETLISTENSIZE).decode("utf-8")
        
        if(res.split(" ", 1)[0] == "WHO-OK"):
            usernames = res.split(" ", 1)[1]
            print(usernames)
        elif(res.split(" ", 1)[0] == "DELIVERY"):
            sender = res.split(" ", 2)[1]
            msg = res.split(" ", 2)[2]
            errorDetection(msg)
            print("\rNew Message from ", end = "")
            print(sender,":", msg)
            print("\nCommand: ")
        elif(res == "SEND-OK\n"):
            print("Message sent succesfully\n")
        elif(res == "UNKNOWN\n"):
            print("Failed to send message: Unknown recipient\n")

def errorDetection(msg):
    keyLen = len(KEY)

    appendZero = msg.decode() + '0'*(keyLen-1)
    remainder = mod(appendZero, KEY)

    noError = "0" * (len(KEY) - 1)

    if remainder == noError:
        print("No error")
    else:
        print("Error")
        # ask server to resend data


def configure():
    print("Server Configuration\n")
    drop = input("Please enter drop: ") # message drop probability between 0 and 1
    drop = "SET DROP {}\n".format(drop)
    sock.sendall(drop.encode("utf-8"))

    flip = input("Please enter flip: ")
    flip = "SET FLIP {}\n".format(flip) # bit flip probability between 0 and 1
    sock.sendall(flip.encode("utf-8"))

    burst = input("Please enter burst: ")
    burst = "SET BURST {}\n".format(burst) # burst error probability
    sock.sendall(burst.encode("utf-8"))

    bLen = input("Please enter burst length: ")
    bLen = "SET BURST-LEN {}\n".format(bLen) # burst error length; default is 3
    sock.sendall(bLen.encode("utf-8"))

    delay = input("Please enter delay probability: ")
    delay = "SET DELAY {}\n".format(delay) # message delay probability
    sock.sendall(delay.encode("utf-8"))

    dLen = input("Please enter delay length: ")
    dLen = "SET DELAY-LEN {}\n".format(dLen) # delay length in seconds; default is 5
    sock.sendall(dLen.encode("utf-8"))

    '''
    setting = "DROP"
    req = "GET {}\n".format(setting)
    sock.sendall(req.encode("utf-8"))
    res = sock.recv(SOCKETLISTENSIZE).decode("utf-8")
    print("Current setting: ", res)
    '''

def reset():
    sock.sendall("RESET\n".encode("utf-8"))

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(SERVERADDRESS)

    rec = threading.Thread(target=receiveMessages, daemon=True)

    try:     
        usernameAccepted = False
        while not usernameAccepted:
            username = input("Please enter a username: ")

            req = "HELLO-FROM {}\n".format(username)
            # sock.sendall(req.encode("utf-8"))
            sock.sendto(str.encode(req), SERVERADDRESS)

            # res = sock.recv(SOCKETLISTENSIZE).decode("utf-8")
            res = sock.recvfrom(SOCKETLISTENSIZE)

            print("Server response: ", res)

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

        configure()

        print("""\nCommands:\n- !who: provides a list of users that are currenty online\n- @<recipient> <message>: send a message to a recipient thats currently online\n- !quit: quit the chat client\n""")

        while(running):
            time.sleep(0.1)
            cmd = input("\nCommand: ")
            if cmd == "!who":
                printUserList()
            elif cmd[0] == '@':
                count = 0
                for i in range(len(cmd)):
                    if cmd[i] == " ":
                        count += 1
                if(count < 1):
                    print("Invalid input. Please try again.")
                else:
                    recipient = cmd.split()[0][1:]
                    msg = cmd.split(' ', 1)[1]
                    sendMsg(recipient, msg)
            elif cmd == "!quit":
                running = False
                sock.close()
            elif cmd == "!configure":
                configure()
            elif cmd == "!reset":
                reset()
            else: print("Command unknown")

    except OSError as err:
        print(err)

    except Exception:
        pass