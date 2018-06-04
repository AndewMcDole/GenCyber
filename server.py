#!/usr/local/bin/python3

import socket
import socketserver
import requestHandler

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# host = socket.gethostname()
# port = 6789
# # Essential, ensures that the resuse of the socket
# # is setup before the socket is bound. Will avoid
# # TIME_WAIT issue
# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# s.bind((host, port))
#
# s.listen(5)
# while True:
#     c, addr = s.accept()
#     print ("Got connection from", addr)
#     c.send("Thank you for connecting".encode())
#     c.close()
