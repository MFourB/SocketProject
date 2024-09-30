from socket import *
import json

serverPort = 1000

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

players_Data = {
    "Number_Of_Players": 0,
    "Players": {}
}

games_Data = {
    "Number_Of_Games": 0,
    "Games": {}
}

def register(player, IPv4, t_port):
    if not (player and IPv4 and t_port):
        print("Invalid arguments")

    print("Registering", player, IPv4, t_port)

    status_Code = ""

    if player in players_Data["Players"]:
        status_Code = f"FAILURE.|register.|{player} already exists!.|"
        print(status_Code)
        return status_Code

    players_Data["Players"][player] = {
        "status": "free",
        "t-port": t_port
    }
    players_Data["Number_Of_Players"] += 1

    status_Code = f"SUCCESS.|register.|{player} are registered!.|"
    print(status_Code)
    return status_Code

def de_register(player, IPv4, t_port):
    if not player in players_Data["Players"]:
        status_Code = f"FAILURE.|de-register.|{player} is not registered!.|"
        print(status_Code)
        return status_Code
    elif not players_Data["Players"][player]["t-port"] == t_port:
        status_Code = f"FAILURE.|de-register.|De-register request is not coming from {player}!.|"
        print(status_Code)
        return status_Code
    elif players_Data["Players"][player]["status"] == "in-play":
        status_Code = f"FAILURE.|de-register.|{player} is in a game!.|"
        print(status_Code)
        return status_Code
    
    del players_Data["Players"][player]
    players_Data["Number_Of_Players"] -= 1

    status_Code = f"SUCCESS.|de-register.|{player} has been de-registered!.|"
    print(status_Code)
    return status_Code


def queryPlayers():
    queriedPlayers = json.dumps(players_Data)
    #print(queriedPlayers)
    status_Code = "SUCCESS.|query-players.|players retrieved.|"+queriedPlayers
    print(status_Code)
    return status_Code

while True:
    try:
        message, clientAddress = serverSocket.recvfrom(2048)
    except KeyboardInterrupt:
        serverSocket.close()
        print("Exiting")

    commands_and_parameters = message.decode().lower().split(' ')
    command = commands_and_parameters[0]
    parameters = commands_and_parameters [1:]
    
    match command:
        case "register":
            try:
                player = parameters[0]
            except IndexError:
                print("No player name given")
                continue
            
            response = register(player, *clientAddress)
            serverSocket.sendto(response.encode(),
                                      clientAddress)
        
        case "query-players":
            print("querying players")
            response = queryPlayers()

            serverSocket.sendto(response.encode(), clientAddress)

        case "start-game":
            print("starting game")
        case "query-games":
            print("querying games")
        case "end":
            print("ending game")
        case "de-register":
            print("De-registering")
            try:
                player = parameters[0]
            except IndexError:
                print("No player name given")
                continue
            
            response = de_register(player, *clientAddress)
            serverSocket.sendto(response.encode(), clientAddress)
        case _:
            status_Code = "FAILURE.|command.|Invalid command.|"
            print(status_Code)
            serverSocket.sendto(status_Code.encode(), clientAddress)

    

    #print(command, parameters, clientAddress)