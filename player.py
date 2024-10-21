from socket import *
import json

serverName = "192.168.1.2"
serverPort = 1000
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)

def sendRequest(request):
    clientSocket.sendto(request.encode(), (serverName, serverPort))
    
    try:
        response, serverAddress = clientSocket.recvfrom(2048)
    except TimeoutError:
        print("Timeout, no response from server")
        #homeMenu()
        return False

    response = list(response.decode().split(".|", 3))
    responseFormatted = {
        "response_Status_Code": response[0],
        "response_Command": response[1],
        "response_Message": response[2],
        "response_Data": response[3],
    }

    if responseFormatted["response_Status_Code"] == "SUCCESS":
        print("\nSUCCESS", responseFormatted["response_Message"])
    elif responseFormatted["response_Status_Code"] == "FAILURE":
        print("\nFAILURE", responseFormatted["response_Message"])
    
    return responseFormatted

def registerMenu():
    player_Name = input("\nRegister a username: ")
    sendRequest("register " + player_Name)

    homeMenu()

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
    option_choice = input("\nEnter option (Example: start-game JohnDoe 3 9): ")

    if option_choice.split(" ")[0].lower() == "register":
        print("FAILURE You've already registered!")

    responseFormated = sendRequest(option_choice)

    if not responseFormated\
    or responseFormated["response_Status_Code"] == "FAILURE":
        homeMenuInputs()

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

    elif responseFormated["response_Command"] == "de-register":
        print("\nNow exiting application\n")

    #print(response)

def main():
    registerMenu()

if __name__=="__main__":
    main()

clientSocket.close()