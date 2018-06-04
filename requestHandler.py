#!/usr/local/bin/python3

import socketserver

class RequestHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler is instantiated once per connection
    to the server, and must override the handle() method
    to implement communication to the client
    """

    def handle(self):
        print("Request Received")
        # self.data = self.request.recv(1024).strip()
        # print "{} wrote:".format(self.client_address[0])
        # print self.data.decode()
        self.request.send("Thank you for connecting".encode())

    """
    if __name__ == "__main__" is a way for this file
    to be run as the main program
    """
if __name__ == "__main__":
    HOST, PORT = "", 6789

    #create a server, binding it to localhost on port 6789
    server = socketserver.TCPServer((HOST, PORT), RequestHandler)

    #Activate the server; this will keep running until you interrupt
    server.serve_forever()
