import uuid
import websockets


class Player:
    def __init__(self, _socket, _uuid):
        self.player_id = uuid.uuid4()
        self.lobby_id = "None"
        self.socket = _socket
