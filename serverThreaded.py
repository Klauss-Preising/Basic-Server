"""
This Code is written for Question 3
"""

import _thread as thread
import socket
import time


# get the current time (needs to be static)
def now():
    return time.ctime(time.time())


# wait 5 seconds before continuing (needs to be static)
def wait5():
    # forces a delay of 5 seconds
    start = time.time()
    while time.time() - start < 5:
        pass


# Server object to hand our server
class Server:

    # initializes the server
    def __init__(self, server_host, server_port, wordList):
        # initializing the servers setting
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.wordList = wordList
        self.server_host = server_host
        self.server_port = server_port
        self.server_backlog = 1
        self.server_sock.bind((self.server_host, self.server_port))
        self.server_sock.listen(self.server_backlog)

        # starts the server
        try:
            self.start()
        except KeyboardInterrupt:  # if we close the server we would like to free up the port
            print("good bye")
            self.server_sock.close()
            exit()

    # starts the servers main loop
    def start(self):
        # Wait for client connection
        while True:
            # Client has connected
            client_conn, client_addr = self.server_sock.accept()
            print('Client has connected with address: ', client_addr, "at", now())

            # starts a new thread processing client interactions with server
            thread.start_new_thread(self.client_handler, (client_conn, client_addr))

    # processes the query
    def getwords(self, word):
        # splits the word based on *
        temp = word.split("*")
        result = []  # temporary variable to be returned
        for i in self.wordList:
            if len(temp) > 1:  # checks whether the we have a star in the word
                # checks if the beginning of the word from wordlist is equal to temp[0]
                # checks if the ending of the word from wordlist is equal to temp[1]
                if temp[0] in i[:len(temp[0]):] and temp[1] in i[-len(temp[1])::]:
                    result.append(i)
            else:
                if word == i:  # if our word is equal to word from the word list is equal the our query word
                    result.append(i)
                    break  # we can break because we are only looking for the word
        return result

    # handles each client process
    def client_handler(self, client_conn, client_addr):
        q = True
        while q:
            # Receive query from client
            bin_data = client_conn.recv(1024)

            # prints word query and process the query
            word = str(bin_data)[2:-1:]
            print("From " + str(client_addr) + " at " + str(now()) + ":", word)
            words = self.getwords(word)

            # we are converting the words list to a string and then encoding it
            words = str(words).encode('utf-8')

            wait5()  # makes us wait 5 seconds

            # we have to split up the words we get into 1024 bits so we can send them as separate packets
            for i in range(0, len(words), 1024):
                temp = ''.encode('utf-8')  # temp is a variable that is used for creating output

                # this is to set temp to the next part of that needs to be sent
                if i + 1024 < len(words):
                    temp = words[i:i + 1024:]
                else:
                    temp = words[i::]

                client_conn.sendall(temp)  # Send the temp to the client
            client_conn.sendall("That's-all-folks".encode())

            start = time.time()

            # This waits for the client to send a True or False to the server
            while True:
                temp = eval(str(client_conn.recv(1024)))
                # if the client doesn't send us something in five minutes we Time them out
                if time.time() - start > 300:
                    q = False
                    print("Timed Out client", client_addr)
                    break

                # checking to see if we get a message
                if temp is not None:
                    q = temp
                    break
        print("Client", client_addr, "has disconnected")
        client_conn.close()


# server socket parameters
server_host = 'localhost'
server_port = 50008

# grabbing the wordlist
fh = open("wordlist.txt", "r")
wordlist = [i.strip() for i in fh.readlines()]
fh.close()

# Create Server object
try:
    server = Server(server_host, server_port, wordList=wordlist)
except OSError:  # if our ip/port is already in use
    print("Address in use:", server_host, server_port)
    exit(1)  # Exit code 1 for address issue
except Exception as e:  # any other exception we didn't count for
    print("Other exception:", e)
    exit(2)  # Exit code 2 for unexpected error
