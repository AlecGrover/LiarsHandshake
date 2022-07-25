from wonderwords import RandomWord
from profanity_filter import ProfanityFilter


class LobbyNameGen:
    def __init__(self):
        self.lobbies = set()
        self.r = RandomWord()
        self.pf = ProfanityFilter()

    def get_new_lobby_id(self):
        lobby_id = self.get_valid_lobby_id()
        while self.lobbies.__contains__(lobby_id) or self.pf.is_profane(lobby_id):
            lobby_id = self.get_valid_lobby_id()
        return lobby_id

    def get_valid_lobby_id(self):
        adjective = self.r.word(include_categories=["adjective"])
        noun = self.r.word(include_categories=["noun"])
        lobby_id = adjective + " " + noun
        return lobby_id

    def remove_lobby_id(self, lobby_id):
        self.lobbies.remove(lobby_id)
