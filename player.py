from socket import *
import json
import threading
import random
from time import sleep

serverName = "192.168.1.2"
serverPort = 46500
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)

game_Port = 0
game_Status = "Waiting"
game_Socket = socket(AF_INET, SOCK_DGRAM)
game_Socket.settimeout(1)

player_Name = ""

threads = {}
game_Data = {}
player_Sockets = []

deck_Of_Cards = [
    {"AD": 1},
    {"AC": 1},
    {"AH": 1},
    {"AS": 1},
    {"2D": -2},
    {"2C": -2},
    {"2H": -2},
    {"2S": -2},
    {"3D": 3},
    {"3C": 3},
    {"3H": 3},
    {"3S": 3},
    {"4D": 4},
    {"4C": 4},
    {"4H": 4},
    {"4S": 4},
    {"5D": 5},
    {"5C": 5},
    {"5H": 5},
    {"5S": 5},
    {"6D": 6},
    {"6C": 6},
    {"6H": 6},
    {"6S": 6},
    {"7D": 7},
    {"7C": 7},
    {"7H": 7},
    {"7S": 7},
    {"8D": 8},
    {"8C": 8},
    {"8H": 8},
    {"8S": 8},
    {"9D": 9},
    {"9C": 9},
    {"9H": 9},
    {"9S": 9},
    {"10D": 10},
    {"10C": 10},
    {"10H": 10},
    {"10S": 10},
    {"JD": 10},
    {"JC": 10},
    {"JH": 10},
    {"JS": 10},
    {"QD": 10},
    {"QC": 10},
    {"QH": 10},
    {"QS": 10},
    {"KD": 0},
    {"KC": 0},
    {"KH": 0},
    {"KS": 0},
]

deck_Of_Cards_Copy = deck_Of_Cards.copy()

def formatRequest(response):
    response = list(response.decode().split(".|", 3))
    responseFormatted = {
        "response_Status_Code": response[0],
        "response_Command": response[1],
        "response_Message": response[2],
        "response_Data": response[3],
    }
    
    return responseFormatted

def sendRequest(request):
    clientSocket.sendto(request.encode(), (serverName, serverPort))
    
    try:
        response, serverAddress = clientSocket.recvfrom(2048)
    except TimeoutError:
        print("Timeout, no response from server")
        #homeMenu()
        return False

    responseFormatted = formatRequest(response)

    if responseFormatted["response_Status_Code"] == "SUCCESS":
        if not responseFormatted["response_Command"] == "start-game":
            print("\nSUCCESS", responseFormatted["response_Message"])
    elif responseFormatted["response_Status_Code"] == "FAILURE":
        print("\nFAILURE", responseFormatted["response_Message"])

    return responseFormatted

def gameMenu():
    option_choice = input("huhu")
    print("game")
    gameMenu()


def waiting_Room(game_Port):
    print("\nWaiting for a game to start")
    global game_Data
    global socket
    global deck_Of_Cards_Copy
    global player_Name

    while True:
        try:
            #print("")
            message, senderAddress = game_Socket.recvfrom(2048)
        except TimeoutError:
            continue

        responseFormated = formatRequest(message)
        #print(responseFormated)

        if not responseFormated:
            continue

        match responseFormated["response_Command"]:
            case "game_init":
                global game_Status
                game_Status = "In_Game"
                print("\nNow Starting Game")
                print("Press Enter to Once or Twice to Begin?")
                input()
            case "show_role":
                print(responseFormated["response_Message"])
            case "give_players":
                game_Data = json.loads(responseFormated["response_Data"])
                random.shuffle(deck_Of_Cards_Copy)
                #print(game_Data["Players"])
                for player in game_Data["Players"]:
                    player_Socket = socket(AF_INET, SOCK_DGRAM)
                    player_Sockets.append(player_Socket)
                    player_Socket.settimeout(1) 
                    player["cards"] = []
                    for index in range(0,6):
                        player["cards"].append(deck_Of_Cards_Copy.pop())

                for player in game_Data["Players"]:
                    player_Socket.sendto(("SUCCESS.|deal.|This is from the dealer.|"+json.dumps(game_Data)).encode(), (player["ipv4"], int(player["p_port"])))

            case "deal":
                game_Data = json.loads(responseFormated["response_Data"])
                for player in game_Data["Players"]:
                    deck_String = ""
                    index = 0
                    #cards = list(player["cards"]).
                    for card in player["cards"]:
                        if index > 1:
                            #deck_String += cards[index] + " "
                            break
                        card_Value = list(card.keys())[0]
                        deck_String += card_Value
                        index += 1
                    deck_String += " ***\n*** *** ***"
                    print(deck_String)

                    print()
                print(responseFormated["response_Message"])
                print()
        
        


def registerMenu():
    print("\nReplace the following values in parenthesis")
    print("Player Port is unique to yourself. Range is from 46501 to 46999")
    print("register (Player Name) (Player Port)")
    register = input("\nregister ")
    responseFormated = sendRequest("register " + register)

    if not responseFormated\
    or responseFormated["response_Status_Code"] == "FAILURE":
        registerMenu()
        return

    register_Values = register.lower().split(' ')
    player_Name = register_Values[0]
    p_port = register_Values[1]

    print(player_Name, p_port)
    game_Port = int(p_port)
    game_Socket.bind((gethostbyname(gethostname()), game_Port))
    #print(p_port, gethostbyname(gethostname()), game_Socket)

    threads["game_Thread"] = threading.Thread(target=waiting_Room, args=(game_Port,))
    game_Thread = threads["game_Thread"]
    game_Thread.daemon = True
    game_Thread.start()

    threads["home_Thread"] = threading.Thread(target=homeMenu)
    home_Thread = threads["home_Thread"]
    home_Thread.daemon = True
    home_Thread.start()

    game_Thread.join()
    home_Thread.join()

def homeMenu():
    print("\nWelcome to the Game of Six Card Golf")
    print("Input the desired option that follows")
    #print("register (Player name)")
    print("query-players")
    print("query-games")
    print("start-game (player), (number of players), (number of holes)")
    print("de-register (player)")

    homeMenuInputs()

def homeMenuInputs():
    if game_Status == "In_Game":
        return
    option_choice = input("\nEnter option (Example: start-game JohnDoe 3 9): ")
    if game_Status == "In_Game":
        return
    
    if option_choice.split(" ")[0].lower() == "register":
        print("FAILURE You've already registered!")

    responseFormated = sendRequest(option_choice)

    if not responseFormated\
    or responseFormated["response_Status_Code"] == "FAILURE":
        homeMenuInputs()
        return

    if responseFormated["response_Command"] == "query-players":
        players_Data = json.loads(responseFormated["response_Data"])

        print("\nNumber of Players:", players_Data["Number_Of_Players"],"""\n--------------""")
        for player in players_Data["Players"]:
            print(player+",")
            if players_Data["Players"][player]["status"] == "free":
                print(f"\tPlace in queue:, {players_Data['Players'][player]['queue_Placement']}")
            elif players_Data["Players"][player]["status"] == "in-play":
                print("\tIn game")
        print()
        homeMenuInputs()
        return
    
    elif responseFormated["response_Command"] == "query-games":
        games_Data = json.loads(responseFormated["response_Data"])

        print("\nNumber of Games:", games_Data["Number_Of_Games"],"""\n--------------""")
        for game in games_Data["Games"]:
            print(game["id"])
            print(f"    Status: {game['status']}")
            print(f"    Players In Game ({len(game['Players'])}):")
            for player in game["Players"]:
                #print(player)
                print(f"        {player['name']}, Role: {player['role']}")
        print()
        homeMenuInputs()
        return

    elif responseFormated["response_Command"] == "start-game":
        homeMenuInputs()
        return

    elif responseFormated["response_Command"] == "de-register":
        print("\nNow exiting application\n")
        return

    #print(response)

def main():
    registerMenu()

if __name__=="__main__":
    main()

clientSocket.close()