import LobbyNameGen


class Lobby:
    def __init__(self, generator):
        self.lobby_id = generator.get_new_lobby_id()
        self.players = set()

