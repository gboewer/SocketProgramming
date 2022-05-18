# ToDO
# guaranteed delivery with acks -> queue: put messages in queue and send as long as there is an item in the queue

import socket
import threading
import time
import queue

SERVERIP = "143.47.184.219"
SERVERPORT = 5382
SERVERADDRESS = (SERVERIP, SERVERPORT)
SOCKETLISTENSIZE = 4096
KEY = "0011"
q = queue.Queue()

def sendMsg(recipient, msg):
    keyLen = len(KEY)
    binary = (''.join(format(ord(x), 'b') for x in msg))

    appendZero = binary + '0'*(keyLen-1)
    remainder = mod(appendZero, KEY)

    result = binary + remainder

    apiMsg = "SEND {} {}\n".format(recipient, msg)

    q.put(apiMsg)

    while q.qsize() != 0:
        apiMsg = q.get()
        sock.sendto(apiMsg.encode(), SERVERADDRESS)

        time.sleep(0.1)

    # print("Message transmitted successfully")
    

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
    sock.sendto(str.encode("WHO\n"), SERVERADDRESS)

def errorDetection(msg, sender):
    '''
    keyLen = len(KEY)

    appendZero = msg.decode() + '0'*(keyLen-1) # decode data
    remainder = mod(appendZero, KEY)

    noError = "0" * (len(KEY) - 1)

    if remainder == noError:'''
    ackn = "SEND {} ack\n".format(sender)
    sock.sendto(str.encode(ackn), SERVERADDRESS)

def receiveMessages(): 
    while(True):
        res = sock.recvfrom(SOCKETLISTENSIZE)

        msg = str(res)
        split = msg.split("'", 2)
        msg = split[1]
        msg = msg[:-2]
        res = msg + '\n'
        # print("Server response: ", res)
        
        if(res.split(" ", 1)[0] == "WHO-OK"):
            usernames = res.split(" ", 1)[1]
            print(usernames)
        elif(res.split(" ", 1)[0] == "DELIVERY"):
            sender = res.split(" ", 2)[1]
            msg = res.split(" ", 2)[2]
            if(msg == "ack\n"):
                q.task_done()
                print("acknowledged")
            else:
                errorDetection(msg, sender)
                print("\rNew Message from ", end = "")
                print(sender,":", msg)
                print("\nCommand: ")
        elif(res == "SEND-OK\n"):
            pass
        elif(res == "UNKNOWN\n"):
            print("Failed to send message: Unknown recipient\n")


def configure():
    drop = 0
    drop = "SET DROP {}\n".format(drop) # message drop probability between 0 and 1
    sock.sendto(str.encode(drop), SERVERADDRESS)

    flip = 0
    flip = "SET FLIP {}\n".format(flip) # bit flip probability between 0 and 1
    sock.sendto(str.encode(flip), SERVERADDRESS)

    burst = 0
    burst = "SET BURST {}\n".format(burst) # burst error probability
    sock.sendto(str.encode(burst), SERVERADDRESS)

    bLen = 3
    bLen = "SET BURST-LEN {}\n".format(bLen) # burst error length; default is 3
    sock.sendto(str.encode(bLen), SERVERADDRESS)

    delay = 0
    delay = "SET DELAY {}\n".format(delay) # message delay probability
    sock.sendto(str.encode(delay), SERVERADDRESS)

    dLen = 2
    dLen = "SET DELAY-LEN {}\n".format(dLen) # delay length in seconds; default is 5
    sock.sendto(str.encode(dLen), SERVERADDRESS)

def reset():
    sock.sendto(str.encode("RESET\n"), SERVERADDRESS)

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(SERVERADDRESS)

    rec = threading.Thread(target=receiveMessages, daemon=True)

    try:     
        usernameAccepted = False
        while not usernameAccepted:
            username = input("Please enter a username: ")

            req = "HELLO-FROM {}\n".format(username)
            sock.sendto(str.encode(req), SERVERADDRESS)

            res = sock.recvfrom(SOCKETLISTENSIZE)
            
            msg = str(res)
            split = msg.split("'", 2)
            msg = split[1]
            msg = msg[:-2]
            res = msg + '\n'

            if(res == "IN-USE\n"):
                print("Username is already in use, please choose a different one.")
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
            else:
                print("Problem logging in occured. Please try again.")

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