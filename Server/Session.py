import select
import time
import StoneHuntGame

class Session:

    def __init__(self, ID, maxNumClients):
        self.ID = ID

        self.maxNumClients = int(maxNumClients)
        self.list_of_clients = []

        self.state = 'Open'

        self.game = StoneHuntGame.StoneHuntGame(self.maxNumClients)

        # This should be used to interupt the execution of this thread
        self.STOP_ALL = False
        self.listening = False

    def __str__(self):
        return "Session {}  {}/{}  {}".format( self.ID, len(self.list_of_clients), self.maxNumClients, self.state)

    def __repr__(self):
        return str(self)

    def checkForUserInput(self):
        read, write, error = select.select(self.lists_of_clients, [], [])
        return read

    def broadcast(self, msg):
        for client in self.list_of_clients:
            client.send(msg.encode())

    def start(self):
        # Sessions begin in the 'open' state
        # Repeatedly send updates to the client until enough players join
        while (len(self.list_of_clients) < self.maxNumClients):
            if self.STOP_ALL:
                self.state = 'Closed'
                self.broadcast("close")
                print("Session {} closed by server".format(self.ID))
                return

            self.broadcast('\rWaiting for players... {}/{}'.format(len(self.list_of_clients), self.maxNumClients))
            time.sleep(3)

        # all clients connected, notify then and start game
        self.broadcast("start")
        self.state = "Running"

        for client in self.list_of_clients:
            self.game.sendClientSetup(client)

        while True:
            clients = self.checkForUserInput()
            for client in clients:
                msg = client.recv(2048).decode()
                if msg:
                    self.game.processCommand()
                else:
                    self.list_of_clients.remove(client)

        win = True

        # Close the session once the game is over
        for client in self.listOfClients:
            if win:
                client.send("Win".encode())
            else:
                client.send("Loss".encode())
            client.close()

    def close(self):
        self.STOP_ALL = True
