from socket import *
import json
import threading
import os
import uuid

server_Port = 46500

starting_p_port_Range = 46501
ending_p_port_Range = 46999

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('192.168.1.2', server_Port))
serverSocket.settimeout(1)

Available_Ports = {}

class Players_Queue:
    Players_Queue = []
    @classmethod
    def add_Player(self, player):
        self.Players_Queue.append(player)
        player.queue_Placement = len(self.Players_Queue)

    '''
    @classmethod
    def remove_Player(self, player):
        #self.Players_Queue[player.queue_Placement-1:].queue_Placement -= 1
        #print([player.__dict__ for player in self.Players_Queue])

        for index in range(player.queue_Placement-1, len(self.Players_Queue)):
            self.Players_Queue[index].queue_Placement -= 1
            print(index)

        #print([player.__dict__ for player in self.Players_Queue])

        self.Players_Queue.remove(player)
        #print(player.queue_Placement)
    '''
    @classmethod
    def consume_Next_Player(self):
        try:
            player = self.Players_Queue[0]
        except IndexError:
            print("No players in Player Queue!")
            return False
        
        for index in range(player.queue_Placement-1, len(self.Players_Queue)):
            self.Players_Queue[index].queue_Placement -= 1
        
        print("Consuming Next Player")
        return self.Players_Queue.pop(0)

    @classmethod
    def consume_Player(self, player):
        for index in range(player.queue_Placement-1, len(self.Players_Queue)):
            self.Players_Queue[index].queue_Placement -= 1
            print("Consuming")
        
        self.Players_Queue.remove(player)
        
    @classmethod
    def size(self):
        return len(self.Players_Queue)

class Players_Data:
    Number_Of_Players = 0
    Players = {}

    @classmethod
    def toJSON(self):
        return json.dumps({
            "Number_Of_Players": self.Number_Of_Players,
            "Players": {player: self.Players[player].toDict() for player in self.Players}
        })

class Games_Data:
    Number_Of_Games = 0
    Games = {}

    @classmethod
    def toJSON(self):
        formatting = {
            "Number_Of_Games": self.Number_Of_Games,
            "Games": [self.Games[game].toDict() for game in self.Games]
        }
        #for game in formatting["Games"]:
            #formatting["Games"][game] = [player.toJSON()\ for player in formatting["Games"][game]["Players"]]
        
        """
        for game in formatting["Games"]:
            for player in formatting["Games"][game]["Players"]:
                print(player)
        """

        return json.dumps(formatting)

class Player(object):
    def __init__(self):
        self.name = ""
        self.status = "free"
        self.ipv4 = ""
        self.t_port = ""
        self.p_port = ""
        self.queue_Placement = 0
        self.role = ""
        self.cards = []
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.settimeout(1)
    def toDict(self):
        return {
            "name": self.name,
            "status": self.status,
            "ipv4": self.ipv4,
            "p_port": self.p_port,
            "queue_Placement": self.queue_Placement,
            "role": self.role,
            "cards": self.cards
        }

class Game(object):
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.Players = []
        self.status = "Starting"

    def toDict(self):
        return {
            "id": self.id,
            "Players": [player.toDict() for player in self.Players],
            "status": self.status,
        }
    def toJSON(self):
        return json.dumps(self.toDict())
    def add_Player(self, player, status, role):
        player.status = status
        player.role = role
        self.Players.append(player)


def send_Server_Response(message):
    serverSocket.sendto(message.encode(), clientAddress)   

def verify_Player(player, t_port, command):
    if not player in Players_Data.Players:
        status_Code = f"FAILURE.|{command}.|{player} is not registered!.|"
        send_Server_Response(status_Code) 
        print(status_Code)
        return False
    elif not Players_Data.Players[player].t_port == t_port:
        status_Code = f"FAILURE.|{command}.|{command} request is not coming from {player}!.|"
        send_Server_Response(status_Code) 
        print(status_Code)
        return False
    elif Players_Data.Players[player].status == "in-play":
        status_Code = f"FAILURE.|{command}.|{player} is in a game!.|"
        send_Server_Response(status_Code) 
        print(status_Code)
        return False
    
    return True

def register(player="", IPv4="", t_port="", p_port=""):
    if not (player or IPv4 or t_port or p_port):
        print("Invalid arguments")

    print("Registering", player, IPv4, t_port, p_port)

    try:   
        if Available_Ports[p_port]:
            status_Code = f"FAILURE.|register.|port {p_port} already taken!.|"
            send_Server_Response(status_Code) 
            print(status_Code)
            return False
    except KeyError:
            status_Code = f"FAILURE.|register.|port {p_port} is not within range!.|"
            send_Server_Response(status_Code) 
            print(status_Code)
            return False

    status_Code = ""

    if player in Players_Data.Players:
        status_Code = f"FAILURE.|register.|{player} already exists!.|"
        send_Server_Response(status_Code) 
        print(status_Code)
        return False
    elif len(player) == 0:
        status_Code = f"FAILURE.|register.|Name can't be empty!.|"
        send_Server_Response(status_Code) 
        print(status_Code)
        return False

    newPlayer = Player()
    newPlayer.name = player
    newPlayer.status = "free"
    newPlayer.ipv4 = IPv4
    newPlayer.t_port = t_port
    newPlayer.p_port = p_port
    newPlayer.queue_Placement = Players_Queue.size()
    Players_Queue.add_Player(newPlayer)

    Players_Data.Number_Of_Players += 1
    Players_Data.Players[newPlayer.name] = newPlayer

    Available_Ports[p_port] = True

    status_Code = f"SUCCESS.|register.|{player} are registered!.|"

    send_Server_Response(status_Code) 

    print(status_Code)

def de_register(player, IPv4, t_port):
    if not verify_Player(player, t_port, "de-register"):
        return False
    
    player = Players_Data.Players[player]
    Players_Queue.consume_Player(player)
    Available_Ports[player.p_port] = False
    del Players_Data.Players[player.name]
    Players_Data.Number_Of_Players -= 1

    status_Code = f"SUCCESS.|de-register.|{player.name} has been de-registered!.|"
    send_Server_Response(status_Code) 

    print(status_Code)


def query_Players():
    queried_Players = Players_Data.toJSON()
    status_Code = "SUCCESS.|query-players.|players retrieved.|"+queried_Players 
    send_Server_Response(status_Code) 
    
    print(status_Code)                

def query_Games():
    queried_Games = Games_Data.toJSON()
    status_Code = "SUCCESS.|query-games.|games retrieved.|"+queried_Games
    send_Server_Response(status_Code) 

    print(status_Code)

def start_Game(player, num_Of_Additional_Players, num_Of_Holes, IPv4, p_port):
    if not player or not num_Of_Additional_Players or not num_Of_Holes:
        status_Code = "FAILURE.|start-game.|Invalid Game Parameters!.|"
        send_Server_Response(status_Code)
        return False
    elif num_Of_Additional_Players < 1 or num_Of_Additional_Players > 3:
        status_Code = "FAILURE.|start-game.|Number of Additional Players is out of range!\nMust be more than 0 and less than 4.|"
        send_Server_Response(status_Code)
        return False
    elif num_Of_Holes < 1 or num_Of_Holes > 9:
        status_Code = "FAILURE.|start-game.|Number of Holes is out of range!\nMust be more than 0 and less than 10.|"
        send_Server_Response(status_Code)
        return False
    elif num_Of_Additional_Players > len(Players_Queue.Players_Queue)-1:
        status_Code = "FAILURE.|start-game.|Not enough players for this request!\nReduce the number of requested players!.|"
        send_Server_Response(status_Code)
        return False
    elif not verify_Player(player, p_port, "start-game"):
        return False

    newGame = Game()
    Games_Data.Games[newGame.id] = newGame
    Games_Data.Number_Of_Games += 1

    dealer = Players_Data.Players[player]

    newGame.add_Player(dealer, "in-play", "Dealer")
    Players_Queue.consume_Player(dealer)
    for index in range(0, num_Of_Additional_Players):
        newPlayer = Players_Queue.consume_Next_Player()
        newPlayer.socket.sendto("SUCCESS.|game_init.|Game is Starting.|".encode(), (newPlayer.ipv4, int(newPlayer.p_port)))   
        newPlayer.socket.sendto("SUCCESS.|show_role.|You are now a player.|".encode(), (newPlayer.ipv4, int(newPlayer.p_port)))   
        newGame.add_Player(newPlayer, "in-play", "Player")
        print("Adding Player", newPlayer)

    dealer.socket.sendto("SUCCESS.|game_init.|Game is Starting.|".encode(), (dealer.ipv4, int(dealer.p_port)))  
    dealer.socket.sendto("SUCCESS.|show_role.|You are now the Dealer.|".encode(), (dealer.ipv4, int(dealer.p_port)))  
    dealer.socket.sendto(("SUCCESS.|give_players.|Here is the player data.|"+newGame.toJSON()).encode(), (dealer.ipv4, int(dealer.p_port)))  

    status_Code = "SUCCESS.|start-game.|games has started.|"
    send_Server_Response(status_Code) 



    #print(status_Code, player, Players_Queue.size(), num_Of_Additional_Players)

def main():
    for index in range(46501, 46999):
        Available_Ports[str(index)] = False
    
    print(Available_Ports)

if __name__=="__main__":
    main()

try:
    while True:
        try:
            message, clientAddress = serverSocket.recvfrom(2048)
        except TimeoutError or ConnectionResetError:
            continue

        commands_and_parameters = message.decode().lower().split(' ')
        command = commands_and_parameters[0]
        parameters = commands_and_parameters [1:]
        
        match command:
            case "register":
                try:
                    player = parameters[0]
                    p_port = parameters[1]
                except IndexError:
                    print("Invalid Register Parameters")
                    continue
                
                register(player, *clientAddress, p_port)
            
            case "query-players":
                print("querying players")
                query_Players()

            case "query-games":
                print("querying games")
                query_Games()
                
            case "start-game":
                try:
                    player = parameters[0]
                    num_Of_Additional_Players = int(parameters[1])
                    num_Of_Holes = int(parameters[2])

                except IndexError:
                    print("Missing Game Parameters")
                    player = False
                    num_Of_Additional_Players = False
                    num_Of_Holes = False

                print("starting game")  
                newThread = threading.Thread(target=start_Game, \
                                             args=(player, num_Of_Additional_Players, num_Of_Holes, *clientAddress,))
                newThread.start()
                print(newThread.name)

            case "end":
                print("ending game")

            case "de-register":
                print("De-registering")
                try:
                    player = parameters[0]
                except IndexError:
                    print("No player name given")
                    continue
                
                de_register(player, *clientAddress)

            case _:
                status_Code = "FAILURE.|command.|Invalid command.|"
                serverSocket.sendto(status_Code.encode(), clientAddress)

                print(status_Code)
                
except KeyboardInterrupt:
    print("Keyboard interrupt")
    serverSocket.close()
    exit()

    #print(command, parameters, clientAddress)