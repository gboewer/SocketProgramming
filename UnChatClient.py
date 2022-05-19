import socket
import threading
import time
import queue

SERVERIP = "143.47.184.219"
SERVERPORT = 5382
SERVERADDRESS = (SERVERIP, SERVERPORT)
SOCKETLISTENSIZE = 4096
KEY = "1011"
q = queue.Queue()
# timeout = time.time() + 20

def sendMsg(recipient, msg):
    binary = (''.join(format(ord(x), 'b') for x in msg))

    appendZero = binary + "000"
    remainder = mod(appendZero, KEY)

    result = binary + remainder
    # print("Binary msg sent: ", result)

    apiMsg = "SEND {} {}\n".format(recipient, result)

    q.put(apiMsg)
    resend()

def resend():
    while not q.empty():
        '''
        if time.time() > timeout:
            q.get()
            q.task_done()
            print("Unable to send message. Try again.")
            break'''
        apiMsg = q.get()
        q.put(apiMsg)
        sock.sendto(str.encode(apiMsg), SERVERADDRESS)

        time.sleep(0.1)
        # print("Items in queue: ", q.qsize())
    # print("Unable to send message. Try again.")
    

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
    apiMsg = "WHO\n"
    q.put(apiMsg)
    resend()

def errorDetection(msg, sender):
    msg = msg[:-1]
    for i in range (0, len(msg)):
        if msg[i] == '0' or msg[i] == '1':
            pass
        else:
            return False
        
    remainder = mod(msg, KEY)
    noError = "000" 

    if remainder == noError:
        ackn = "SEND {} ack\n".format(sender)
        sock.sendto(str.encode(ackn), SERVERADDRESS)
        # print("No Error detected")
        return True
    else:
        # print("Error detected")
        return False

def BinaryToDecimal(binary):
	string = int(binary, 2)
	
	return string

def receiveMessages():
    lastMsg = "" 
    while(True):
        res = sock.recvfrom(SOCKETLISTENSIZE)

        msg = str(res)
        split = msg.split("'", 2)
        msg = split[1]
        msg = msg[:-2]
        res = msg + '\n'

        # print("Server response: ", res)
        
        if(res.split(" ", 1)[0] == "WHO-OK"):
            q.get()
            q.task_done()
            usernames = res.split(" ", 1)[1]
            print(usernames)
        elif(res.split(" ", 1)[0] == "DELIVERY"):
            count = 0
            for i in range (0, len(res)):
                if res[i] == " ":
                    count += 1
            if count > 1:
                sender = res.split(" ", 2)[1]
                msg = res.split(" ", 2)[2]
                if(msg == "ack\n"):
                    q.get()
                    q.task_done()
                    # print("acknowledged")
                else:
                    noError = errorDetection(msg, sender)
                    if noError and msg != lastMsg:
                        str_data =' '
                        # print("Binary msg received: ", msg)
                        i = 0
                        while i < len(msg):
                            temp_data = msg[i:i + 7]
                            if temp_data[:-1] == "100000":
                                str_data = str_data + ' '
                                i += 6
                            else:
                                decimal_data = BinaryToDecimal(temp_data)
                                str_data = str_data + chr(decimal_data)
                                i += 7
                        lastMsg = msg
                        print("\rNew Message from ", end = "")
                        print(sender,":", str_data)
                        print("\nCommand: ")
        elif(res == "SEND-OK\n"):
            pass
        elif(res == "UNKNOWN\n"):
            pass
            # print("Failed to send message: Unknown recipient\n")

def configure():
    drop = 0.3
    drop = "SET DROP {}\n".format(drop) # message drop probability between 0 and 1
    sock.sendto(str.encode(drop), SERVERADDRESS)

    flip = 0.002
    flip = "SET FLIP {}\n".format(flip) # bit flip probability between 0 and 1
    sock.sendto(str.encode(flip), SERVERADDRESS)

    burst = 0.002
    burst = "SET BURST {}\n".format(burst) # burst error probability
    sock.sendto(str.encode(burst), SERVERADDRESS)

    bUpper = 3
    bLower = 0
    bLen = "SET BURST-LEN {} {}\n".format(bLower, bUpper) # burst error length; default is 3
    sock.sendto(str.encode(bLen), SERVERADDRESS)

    delay = 0.3
    delay = "SET DELAY {}\n".format(delay) # message delay probability
    sock.sendto(str.encode(delay), SERVERADDRESS)

    dUpper = 5
    dLower = 0
    dLen = "SET DELAY-LEN {} {}\n".format(dLower, dUpper) # delay length in seconds; default is 5
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
            else: print("Command unknown")

    except OSError as err:
        print(err)

    except Exception:
        pass