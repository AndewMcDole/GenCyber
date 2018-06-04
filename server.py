#!/usr/local/bin/python3

import socketserver

class AvengerHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler is instantiated once per connection
    to the server, and must override the handle() method
    to implement communication to the client
    """

    def handle(self):
        # print("Request Received")
        self.data = self.request.recv(1024).strip()
        print ("{} wrote: {}".format(self.client_address[0], self.data.decode()))
        self.request.send("Thank you for connecting to the Avenger's Stone Hunt".encode())


HOST, PORT = "", 6789

#create a server, binding it to localhost on port 6789
server = socketserver.TCPServer((HOST, PORT), AvengerHandler)

#Activate the server; this will keep running until you interrupt
server.serve_forever()
