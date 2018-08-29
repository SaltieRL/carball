from typing import Callable
from ....generated.api import player_pb2
from ....json_parser.player import Player
from .ApiPlayerCameraSettings import ApiPlayerCameraSettings
from .ApiPlayerLoadout import ApiPlayerLoadout


class ApiPlayer:

    @staticmethod
    def create_from_player(proto_player: player_pb2.Player, player: Player, id_creator: Callable):
        ApiPlayerCameraSettings.create_from_player(proto_player.camera_settings, player)
        ApiPlayerLoadout.create_from_player(proto_player.loadout, player)

        id_creator(proto_player.id, player.name)
        if player.name is not None:
            proto_player.name = player.name
        if player.title is not None:
            proto_player.title_id = player.title
        if player.score is not None:
            proto_player.score = player.score
        if player.goals is not None:
            proto_player.goals = player.goals
        if player.assists is not None:
            proto_player.assists = player.assists
        if player.saves is not None:
            proto_player.saves = player.saves
        if player.shots is not None:
            proto_player.shots = player.shots
        if player.is_orange is not None:
            proto_player.is_orange = player.is_orange
        if player.party_leader is not None:
            proto_player.party_leader.id = player.party_leader
        return proto_player
