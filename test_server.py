from _thread import *
import socket
import sys
import time

import StoneHuntGame

def main(argv):
    print("Starting server on {} on {}".format(argv[1], argv[2]))
    server = setupNetwork(argv[1], int(argv[2]))
    game = StoneHuntGame.StoneHuntGame(int(argv[3]))
    print("Awaiting connections...")
    while True:
        conn, addr = server.accept()
        start_new_thread(clientthread, (conn, addr, game))

def clientthread(conn, addr, game):
    validClient = True
    openingRequest = conn.recv(1024).decode()
    if openingRequest == "connect":
        print("{} attempting connect...".format(addr))
        validClient = game.addClient(conn)
    elif openingRequest == "reconnect":
        print("{} attempting to reconnect...".format(addr))
        validClient = game.reconnect(conn)
    elif openingRequest == "admin":
        validClient = game.sendGameState(conn)

    # block this thread until the game is started
    # check every 2 seconds
    while not game.hasGameStarted():
        time.sleep(2)

    # send out the client setup and begin message sending
    game.sendClientSetup(conn)

    while validClient:
        try:
            message = conn.recv(2048).decode()
            if message:
                game.process(conn, message)
            else:
                """message may have no content if the connection
                is broken, in this case we remove the connection"""
                pass
        except:
            continue

def setupNetwork(ip_addr, port):
    """The first argument AF_INET is the address domain of the
    socket. This is used when we have an Internet Domain with
    any two hosts The second argument is the type of socket.
    SOCK_STREAM means that data or characters are read in
    a continuous flow."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ip_addr, port))
    server.listen(100)
    return server


"""
This allows us to put the main at the top
and avoid any undefined function scenarios
"""
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Proper Usage: python3 StoneHuntGameServer.py ip_addr port NumPlayers")
        exit()
    main(sys.argv)
