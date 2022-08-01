import json

import websockets
import asyncio
import uuid
import PlayerDB
import DestinyAPI
from Player import Player
from Lobby import Lobby

from LobbyNameGen import LobbyNameGen

global db
global active_players
global seperator
global lobby_generator
global active_lobbies


# Hacky way to test for valid UUIDs I found online at: https://lindevs.com/check-if-string-is-valid-uuid-using-python/
def check_valid_uuid(_uuid):
    try:
        uuid.UUID(str(_uuid))
        return True
    except ValueError:
        return False


# Queries the Destiny API for users with a matching Destiny ID (must be a complete ID)
def search_player_by_name(_name):
    full_data = DestinyAPI.search_for_user(_name)
    if len(full_data) > 0:
        return full_data[0]
    else:
        return None


# Stores player data in the database keyed by a UUID
def assign_data_to_uuid(_uuid, data):
    global db
    if not check_valid_uuid(_uuid):
        return
    db.set_player_data(_uuid, data)


# Attempts to fetch any player stats from the database for the provided UUID
def get_stats_from_uuid(_uuid):
    # Reject query if the UUID is improperly formatted
    if not check_valid_uuid(_uuid):
        print("Attempted to check stats for an invalid UUID.")
        return None
    raw_data = search_player_by_id(_uuid)
    # Reject query if the UUID does not have stored data or is not in the database
    if raw_data is None:
        print("Attempted to fetch stats for a UUID with no data.")
        return None
    data = eval(raw_data)
    membership_id = data["membershipId"]
    membership_type = data["membershipType"]
    # Reject query if the user has an API entry but no Destiny stats
    if membership_id is None or membership_type is None:
        print("Missing required membership information in API data for UUID.")
        return None
    player = active_players[_uuid]
    # Reject query if the player is not in the active_players list
    if player is None:
        print("No player with provided UUID in active_players.")
        return None
    # Acquires updated stats for the player from the API and returns
    stats = player.get_updated_stats(membership_id, membership_type)
    return stats


# Queries the Database for an extant user with the specified UUID
def search_player_by_id(_id):
    player_data = db.get_player_data(_id)
    return player_data


# Creates lobby names on a loop, exists for name generation testing and will need to be deprecated or modified
async def create_lobby_names():
    global lobby_generator
    global active_players
    while True:
        for player in active_players.keys():
            await active_players[player].socket.send(lobby_generator.get_new_lobby_id())
        await asyncio.sleep(15)


# Matchmakes a player with the specified UUID
def matchmake(_uuid):
    global lobby_generator
    print(active_players.keys().__contains__(_uuid))
    # Attempts to locate the player in the active player list
    if active_players.keys().__contains__(_uuid):
        player = active_players[_uuid]
        # If the player does not have a lobby id, matchmake them
        if player.lobby_id == "None":
            # Search the active lobbies for a lobby with space, if found, add the player to that lobby and return the id
            for lobbyKey in active_lobbies.keys():
                lobby = active_lobbies[lobbyKey]
                if len(lobby.players) < 2:
                    lobby.players.add(_uuid)
                    player.lobby_id = lobby.lobby_id
                    return lobby.lobby_id
            # If there is no lobby with space, create a new one, place the player into it, and return the lobby id
            new_lobby = Lobby(lobby_generator)
            new_lobby.players.add(_uuid)
            active_lobbies[new_lobby.lobby_id] = new_lobby
            player.lobby_id = new_lobby.lobby_id
            return new_lobby.lobby_id
        else:
            return player.lobby_id
    return "ERROR"


# Primary handler of socket events
async def handler(websocket, path):
    global db
    print(db.get_db_list())
    # Loops handler indefinitely
    global seperator
    seperator = "::"
    global active_players
    while True:
        # Wait for socket events
        try:
            data = await websocket.recv()
            data_segments = data.split(seperator)
            print(data_segments)
            header = ""
            # IDE gets mad that this assignment is useless, but it protects against my own future carelessness
            reply = ""

            # Activates if a message is sent that somehow has no segments, should be impossible, but it would cause a crash
            if len(data_segments) <= 0:
                await websocket.send("Error" + seperator + "NO DATA")
                break
            # Detects the initial connection and informs it of the seperator string
            elif data_segments[0] == "Connection Established":
                print("User connected.")
                header = "Seperator="
            # Sends a UUID
            elif data_segments[0] == "Get New UUID":
                header = "UUID"
                reply = str(uuid.uuid4())
            # Searches for a player by their full Bungie ID, has some more aggressive handling to avoid a situation where
                # a player's ID includes the seperator text.
            elif data_segments[0] == "uuid" and len(data_segments) > 1:
                header, reply = await register_uuid_connection(active_players, data_segments, header, reply, websocket)
            # EDIT: Nevermind, apologies to anyone with a username that includes the seperator...
            elif len(data_segments) > 1 and data_segments[0] == "Player Search":
                header = "Player Data"
                reply = str(search_player_by_name(data_segments[1]))
            # Locks in an entered username and registers the account data to the UUID in the database
            elif data_segments[0] == "Set Username" and len(data_segments) >= 3:
                await set_username_to_db(data_segments, db)
            # Calls the matchmaker
            elif data_segments[0] == "Matchmake" and len(data_segments) > 1:
                if check_valid_uuid(data_segments[1]):
                    lobby_id = matchmake(data_segments[1])
                    header = "Lobby"
                    reply = lobby_id
            # Requests details on the player's current lobby if one exists
            elif data_segments[0] == "Get Game Data" and len(data_segments) > 1:
                header, reply = await get_lobby_data(active_players, data_segments, header, reply)
            # Returns the player's stats
            elif data_segments[0] == "Get My Stats" and len(data_segments) > 1:
                if check_valid_uuid(data_segments[1]):
                    header = "STATS"
                    reply = json.dumps(get_stats_from_uuid(data_segments[1]))
            else:
                reply = "Unknown Socket Data"
            # else:
            #     reply = f"Data received as {type(data)} {data}!"
            await websocket.send(header + seperator + reply)
        # Disconnects the user
        except websockets.ConnectionClosedOK as e:
            print("User disconnected.")
            break


# Asynchronous function for acquiring lobby data
async def get_lobby_data(active_players, data_segments, header, reply):
    if check_valid_uuid(data_segments[1]):
        player = active_players[data_segments[1]]
        if player is not None and player.lobby_id != "None":
            lobby = active_lobbies[player.lobby_id]
            if lobby is not None:
                header = "GameData"
                reply = "Players=" + str(lobby.players) + "; Lobby ID=" + lobby.lobby_id
        else:
            reply = "ERROR"
    return header, reply


# Inserts player data to the database keyed to their UUID
# TODO: Refactor to make the name more accurately descriptive
async def set_username_to_db(data_segments, db):
    if check_valid_uuid(data_segments[2]):
        db.set_player_data(data_segments[2], str(search_player_by_name(data_segments[1])))


# Creates an active player object registered to a UUID
async def register_uuid_connection(active_players, data_segments, header, reply, websocket):
    if not check_valid_uuid(data_segments[1]):
        header = "UUID"
        reply = str(uuid.uuid4())
        active_players[reply] = Player(websocket, reply)
    else:
        active_players[data_segments[1]] = Player(websocket, data_segments[1])
        print(active_players)
    return header, reply


# Disused development function
# TODO: Delete later
async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)


# Every hour check the user database for users who have been inactive for over a week and delete them
async def clear_old_data():
    global db
    print("Starting data clear loop")
    while True:
        await asyncio.sleep(360)
        db.clear_inactive_users(7)
        print("Cleared Old Data")


# Main function, called at start
if __name__ == "__main__":
    global active_players
    active_players = {}

    global db
    db = PlayerDB.PlayerDB(0)

    global lobby_generator
    lobby_generator = LobbyNameGen()

    global active_lobbies
    active_lobbies = {}

    start_server = websockets.serve(handler, "localhost", 80)

    # asyncio.get_event_loop().run_forever()

    try:

        loop = asyncio.get_event_loop()
        loop.create_task(clear_old_data())
        # loop.create_task(create_lobby_names())
        loop.run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
        # async with websockets.serve(echo, "localhost", 80):
        #     await asyncio.Future()
    finally:
        print("Shutting down.")
        db.shutdown()
