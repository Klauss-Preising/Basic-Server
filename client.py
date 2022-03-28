"""
This Code is written for Question 3
"""

import socket


# client class to handle the client
class Client:

    # initiates the connection to the server and tests whether a connection was made
    def __init__(self, server_host, server_port):
        # client settings
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.connect((server_host, server_port))

        # error handling
        try:
            # start talking to server
            self.request()
        except ConnectionResetError:  # if the server closed our connection or is offline during the client running
            print("Connection forced closed")
            self.server_sock.close()  # to free up the port
        except Exception as e:  # unexpected error
            print("Other Error:", e)
            self.server_sock.close()  # to free up the port

    # contains the main loop for the client connection.
    def request(self):

        # main loop
        while True:
            # grabs the word they want to query and sends it to server
            word = input("word to query: ")
            bin_msg = word.encode('utf-8')
            self.server_sock.sendall(bin_msg)

            # this grabs the wordlist from the server
            words = ""

            # loop to receive packets
            while True:
                # get the packet
                bin_resp = self.server_sock.recv(1024).decode('utf-8')

                # That's-all-folks is my indication that i will not be receiving anymore packets
                if "That's-all-folks" in bin_resp:
                    words += bin_resp[:-len("That's-all-folks"):]
                    break  # break packet loop
                words += bin_resp

            # prints what we get from the server
            print(words)

            # input to quit out of the client
            q = input("type quit to end, anything else to continue: ").lower().strip()

            # checks if we need to quit the main loop
            if q == "quit":
                self.server_sock.sendall("False".encode())  # Tell the server to end the connection
                break  # break main loop
            self.server_sock.sendall("True".encode())  # Tell the server to continue
        # Close server socket
        self.server_sock.close()


# Server socket parameters
server_host = 'localhost'
server_port = 50008

# Create Client object
client = Client(server_host, server_port)
