#!/usr/local/bin/python3

import socketserver

class RequestHandler(socketserver.BaseRequestHandler):
    def __init__(self):
        print ("Created request handler")

    def handle(self):
        print("Request Received")
