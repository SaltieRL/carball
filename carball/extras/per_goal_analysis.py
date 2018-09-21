from typing import List

from carball.generated.api import game_pb2
from carball.json_parser.game import Game

from carball.analysis.analysis_manager import AnalysisManager


class PerGoalAnalysis(AnalysisManager):

    def __init__(self, game: Game):
        super().__init__(game)
        self.protobuf_games = []

    def perform_full_analysis(self, game: Game, proto_game: game_pb2.Game, player_map, data_frame, kickoff_frames):
        self.protobuf_games = []
        # split up frames
        total_score = proto_game.game_metadata.score.team_0_score + proto_game.game_metadata.score.team_1_score
        print(total_score)
        for i in range(0, total_score):
            split_pandas = data_frame[data_frame.game.goal_number == i]
            new_proto = game_pb2.Game()
            for team in proto_game.teams:
                proto_team = new_proto.teams.add()
                proto_team.CopyFrom(team)

            for player in proto_game.players:
                proto_player = new_proto.players.add()
                proto_player.CopyFrom(player)
            new_proto.game_metadata.CopyFrom(proto_game.game_metadata)
            new_game = Game()
            new_game.players = game.players
            new_game.teams = game.teams
            new_game.frames = split_pandas
            super().perform_full_analysis(new_game, new_proto, player_map, split_pandas, kickoff_frames)
            self.protobuf_games.append(new_proto)

    def get_protobuf_data(self) -> List[game_pb2.Game]:
        """
        :return: The protobuf data created by the analysis
        """
        return self.protobuf_games
