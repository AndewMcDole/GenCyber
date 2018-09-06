import select
import time

import Stonehunt

class Session:

    def __init__(self, ID, maxNumClients):
        self.ID = ID

        self.maxNumClients = int(maxNumClients)
        self.list_of_clients = []

        self.state = 'Open'

        # This should be used to interupt the execution of this thread
        self.STOP_ALL = False
        self.listening = False

        # Stonehunt
        self.game = Stonehunt.StoneHuntGame(maxNumClients)

        # Time tracking
        self.startTime = None
        self.currTime = None
        self.timer = 600 # 15 minutes

        # game over and winner
        self.gameOver = False
        self.heroWin = False

    def __str__(self):
        return "Session {}  {}/{}  {}".format( self.ID, len(self.list_of_clients), self.maxNumClients, self.state)

    def __repr__(self):
        return str(self)

    def addClient(self, conn):
        if self.game.addClient(conn, self.ID):
            self.list_of_clients.append(conn)

    def checkForUserInput(self):
        read, write, error = select.select(self.lists_of_clients, [], [])
        return read

    def broadcast(self, msg):
        for client in self.list_of_clients:
            try:
                client.send(msg.encode())
            except BrokenPipeError:
                self.list_of_clients.remove(client)

    def processClients(self):
        # Check each client to see if they sent a message
        read_socks, write_socks, error_socks = select.select(self.list_of_clients, [], [], 1)

        # Proccess each request
        for client in read_socks:
            msg = client.recv(2048).decode()
            if msg:
                self.game.process(conn, message)
            else:
                self.list_of_clients.remove(client)

    def start(self):
        # Sessions begin in the 'open' state
        while not self.game.hasGameStarted():
            if self.STOP_ALL:
                self.state = 'Closed'
                self.broadcast("close")
                print("Session {} closed by server".format(self.ID))
                return

            self.broadcast('Waiting for players... {}/{}\r'.format(len(self.list_of_clients), self.maxNumClients))
            time.sleep(3)

        # all clients connected, notify then and start game
        print("Session {} has started...".format(self.ID))
        self.broadcast("start")
        self.state = "Running"
        self.startTime = time.time()
        self.currTime = self.startTime

        while not self.gameOver:
            self.processClients()
            # Check if time limit is over
            self.currTime = time.time()
            # print("\rCurr time: {}  Elapsed Time: {}".format(self.currTime, self.currTime - self.startTime), end="")
            if self.currTime - self.startTime > self.timer:
                self.gameOver = True
                self.heroWin = False

        # Game is over
        self.state = 'Closed'
        time.sleep(2)
        self.broadcast("game over")
        time.sleep(2)
        if self.heroWin:
            self.broadcast("win")
        else:
            self.broadcast("loss")

        print("Session {} ending...".format(self.ID))

    def close(self):
        self.STOP_ALL = True
