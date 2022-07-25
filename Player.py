import uuid
import DestinyAPI


class Player:
    def __init__(self):
        self.player_id = uuid.uuid4();
        self.account_name = "Unknown"
        self.lobby_id = "None"

