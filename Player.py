import uuid
import datetime
import DestinyAPI

STATS_EXPIRY_DAYS = 0.05


class Player:
    def __init__(self, _socket, _uuid):
        self.player_id = uuid.uuid4()
        self.lobby_id = "None"
        self.socket = _socket
        self.stats = None
        self.stats_last_updated = datetime.datetime.now()

    def get_updated_stats(self, membership_id, membership_type):
        if self.stats is None or datetime.datetime.now() - self.stats_last_updated > datetime.timedelta(
                days=STATS_EXPIRY_DAYS):
            self.stats = DestinyAPI.get_user_stats(membership_id, membership_type)
            self.stats_last_updated = datetime.datetime.now()
        return self.stats
