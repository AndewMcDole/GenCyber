import select
import time

import StoneHuntGame

class Session:

    def __init__(self, ID, maxNumClients, time):
        self.ID = ID

        self.maxNumClients = int(maxNumClients)
        self.list_of_clients = []

        self.state = 'Open'

        # This should be used to interupt the execution of this thread
        self.STOP_ALL = False
        self.listening = False

        # StoneHuntGame
        self.game = StoneHuntGame.StoneHuntGame(maxNumClients)

        # Time tracking
        self.startTime = None
        self.currTime = None
        self.timer = time

        # game over and winner
        self.gameOver = False
        self.heroWin = False

        # If listen is on, then let the game print out stuff
        self.listen = False

    def __str__(self):
        if self.startTime == None:
            return "Session {}  {}/{}  {}".format( self.ID, len(self.list_of_clients), self.maxNumClients, self.state)
        else:
            return "Session {}  {}/{}  {} {:.0f}".format( self.ID, len(self.list_of_clients), self.maxNumClients, self.state, self.currTime - self.startTime)
    def __repr__(self):
        return str(self)

    def addClient(self, conn):
        if self.game.addClient(conn, self.ID):
            self.list_of_clients.append(conn)
            return True
        return False

    def reconnectClient(self, conn, key):
        if self.game.reconnect(conn, key):
            self.list_of_clients.append(conn)
            return True
        return False


    def checkForUserInput(self):
        read, write, error = select.select(self.lists_of_clients, [], [])
        return read

    def broadcast(self, msg):
        for client in self.list_of_clients:
            try:
                client.send(msg.encode())
            except ConnectionResetError | BrokenPipeError:
                #print("Client disconnected in session {}".format(self.ID))
                self.list_of_clients.remove(client)

    def processClients(self):
        # Check each client to see if they sent a message
        read_socks, write_socks, error_socks = select.select(self.list_of_clients, [], [], 1)

        # Proccess each request
        for client in read_socks:
            msg = client.recv(2048).decode()
            if msg:
                self.game.process(client, msg)
            else:
                self.list_of_clients.remove(client)

    def sendClientSetups(self):
        for client in self.list_of_clients:
            self.game.sendClientSetup(client)

    def start(self):
        # Sessions begin in the 'open' state
        while not self.game.hasGameStarted():
            if self.STOP_ALL:
                self.state = 'Closed'
                self.broadcast("close")
                print("Session {} closed by server".format(self.ID))
                return

            self.broadcast('\rWaiting for players... {}/{}'.format(len(self.list_of_clients), self.maxNumClients))
            time.sleep(3)

        # all clients connected, notify then and start game
        print("Session {} has started...".format(self.ID))
        self.broadcast("start")
        self.state = "Running"
        self.startTime = time.time()
        self.currTime = self.startTime

        self.sendClientSetups()

        while not self.gameOver:
            self.processClients()
            # Check if time limit is over
            self.currTime = time.time()
            #print("Session {} elapsed Time: {}".format(self.ID, self.currTime - self.startTime))
            if self.currTime - self.startTime > self.timer:
                self.gameOver = True
                self.heroWin = False

            if self.listen:
                self.game.listen = True
            elif not self.listen:
                self.game.listen = False

        self.broadcast("LOW;END;FULL_STOP")
        time.sleep(0.1)
        if self.heroWin:
            self.broadcast("win")
            print("Broadcasting Hero Win")
        else:
            self.broadcast("loss")
            print("Broadcasting Hero Loss")

        time.sleep(0.5) # Give time for clients to register that the game has ended

        print("Session {} ending...".format(self.ID))
        # Game is over
        self.state = 'Closed'

    def close(self):
        self.STOP_ALL = True
