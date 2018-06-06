#!/usr/local/bin/python3

import socketserver
import ClientDirectory

CD = ClientDirectory.ClientDirectory(2)

class AvengerHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler is instantiated once per connection
    to the server, and must override the handle() method
    to implement communication to the client
    """

    def handle(self):
        # print("Request Received")
        self.data = self.request.recv(1024).strip()
        message = self.data.decode()
        print ("{} wrote: {}".format(self.client_address[0], message))
        #Check the first character
        if message[0] == "0":
            name = message[2:]
            print ("Adding new client {} to client directory".format(name))
            CD.addClient(name, self.client_address[0])
            self.request.send("Thank you for connecting to the Avenger's Stone Hunt".encode())
        else:
            print ("Transmitting message")


HOST, PORT = "", 6789

#create a server, binding it to localhost on port 6789
server = socketserver.TCPServer((HOST, PORT), AvengerHandler)

#Activate the server; this will keep running until you interrupt
server.serve_forever()
