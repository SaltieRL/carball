import logging
import time
from typing import Dict, Callable, Union

import pandas as pd
import json
import os
import gzip

from google.protobuf.json_format import _Printer
from typing.io import IO

from .utils.json_encoder import CarballJsonEncoder

script_path = os.path.abspath(__file__)
with open(os.path.join(os.path.dirname(script_path), 'PROTOBUF_VERSION'), 'r') as f:
    PROTOBUF_VERSION = json.loads(f.read())

from ..analysis.cleaner.cleaner import clean_replay
from ..analysis.saltie_game.metadata.ApiGame import ApiGame
from ..analysis.saltie_game.metadata.ApiMutators import ApiMutators
from ..analysis.saltie_game.metadata.ApiPlayer import ApiPlayer
from ..analysis.saltie_game.metadata.ApiTeam import ApiTeam
from ..analysis.saltie_game.saltie_game import SaltieGame
from ..analysis.stats.stats_manager import StatsManager
from ..analysis.utils.pandas_manager import PandasManager
from ..analysis.utils.proto_manager import ProtobufManager
from ..generated.api import game_pb2
from ..generated.api.player_pb2 import Player
from ..json_parser.game import Game
from ..analysis.events.event_creator import EventsCreator

logger = logging.getLogger(__name__)


class AnalysisManager:
    """
    AnalysisManager class takes an initialized Game object and converts the data into a Protobuf and a DataFrame. Then,
    that data is used to perform full analysis on the replay.
    """

    id_creator = None
    timer = None

    def __init__(self, game: Game):
        self.game = game
        self.protobuf_game = game_pb2.Game()
        self.protobuf_game.version = PROTOBUF_VERSION
        self.id_creator = self._create_player_id_function(game)
        self.stats_manager = StatsManager()
        self.events_creator = EventsCreator(self.id_creator)
        self.should_store_frames = False
        self.df_bytes = None

    def create_analysis(self, calculate_intensive_events: bool = False, clean: bool = True):
        """
        Sets basic metadata, and decides whether analysis can be performed and then passes required parameters
        to perform_full_analysis(...); After, stores the DataFrame.

        :param calculate_intensive_events: Indicates if expensive calculations should run to include additional stats.
        :param clean: Indicates if useless/invalid data should be found and removed.
        """

        self._start_time()
        player_map = self._get_game_metadata(self.game, self.protobuf_game)
        self._log_time("Getting in-game frame-by-frame data...")
        data_frame = self._initialize_data_frame(self.game)
        self._log_time("Getting important frames (kickoff, first-touch)...")
        kickoff_frames, first_touch_frames = self._get_kickoff_frames(self.game, self.protobuf_game, data_frame)
        self._log_time("Setting game kickoff frames...")
        self.game.kickoff_frames = kickoff_frames

        if self._can_do_full_analysis(first_touch_frames):
            self._perform_full_analysis(self.game, self.protobuf_game, player_map,
                                        data_frame, kickoff_frames, first_touch_frames,
                                        calculate_intensive_events=calculate_intensive_events,
                                        clean=clean)
        else:
            self._log_time("Cannot perform analysis: invalid analysis.")
            self.protobuf_game.game_metadata.is_invalid_analysis = True

        # log before we add the dataframes
        # logger.debug(self.protobuf_game)

        self._store_frames(data_frame)

    def write_json_out_to_file(self, file: IO):
        """
        Writes the json data to the specified file, as text.

        NOTES:
            The data is written as text (i.e. string), and the buffer mode must be 'w'.
                E.g. open(file_name, 'w')

        :param file: The file object (or a buffer).
        """

        if 'b' in file.mode:
            raise IOError("Json files can not be binary use open(path,\"w\")")
        printer = _Printer()
        js = printer._MessageToJsonObject(self.protobuf_game)
        json.dump(js, file, indent=2, cls=CarballJsonEncoder)

    def write_proto_out_to_file(self, file: IO):
        """
        Writes the proto buffer data to the specified file, as bytes.

        NOTES:
            The data is written as bytes (i.e. in binary), and the buffer mode must be 'wb'.
                E.g. open(file_name, 'wb')
            The file will NOT be human-readable.

        :param file: The file object (or a buffer).
        """

        if 'b' not in file.mode:
            raise IOError("Proto files must be binary use open(path,\"wb\")")
        ProtobufManager.write_proto_out_to_file(file, self.protobuf_game)

    def write_pandas_out_to_file(self, file: Union[IO, gzip.GzipFile]):
        """
        Writes the pandas data to the specified file, as bytes. File may be a GzipFile object to compress the data
        frame.

        NOTES:
            The data is written as bytes (i.e. in binary), and the buffer mode must be 'wb'.
                E.g. gzip.open(file_name, 'wb')
            The file will NOT be human-readable.

        :param file: The file object (or a buffer).
        """
        if isinstance(file.mode, str) and 'b' not in file.mode:
            raise IOError("Data frame files must be binary use open(path,\"wb\")")
        if isinstance(file.mode, int) and file.mode != gzip.WRITE:
            raise IOError("Gzip compressed data frame files must be opened in WRITE mode.")
        if self.df_bytes is not None:
            file.write(self.df_bytes)
        elif not self.should_store_frames:
            logger.warning("pd DataFrames are not being stored anywhere")

    def get_protobuf_data(self) -> game_pb2.Game:
        """
        :return: The protobuf data created by the analysis

        USAGE: A Protocol Buffer contains in-game metadata (e.g. events, stats). Treat it as a usual Python object with
        fields that match the API.

        INFO: The Protocol Buffer is a collection of data organized in a format similar to json. All relevant .proto
        files found at https://github.com/SaltieRL/carball/tree/master/api.

        Google's developer guide to protocol buffers may be found at https://developers.google.com/protocol-buffers/docs/overview
        """
        return self.protobuf_game

    def get_json_data(self):
        """
        :return: The protobuf data created by the analysis as a json object.

        see get_protobuf_data for more details.
        The json fields are defined by https://github.com/SaltieRL/carball/tree/master/api
        """
        printer = _Printer()
        js = printer._MessageToJsonObject(self.protobuf_game)
        return js

    def get_data_frame(self) -> pd.DataFrame:
        """
        :return: The pandas.DataFrame object.

        USAGE: A DataFrame contains in-game frame-by-frame data.

        INFO: The DataFrame is a collection of data organized in a format similar to csv. The 'index' column of the
        DataFrame is the consecutive in-game frames, and all other column headings (150+) are tuples in the following
        format:
            (Object, Data), where the Object is either a player, the ball or the game.

        All column information (and keys) may be seen by calling data_frame.info(verbose=True)

        All further documentation about the DataFrame can be found at https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
        """
        return self.data_frame

    def _perform_full_analysis(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                               data_frame: pd.DataFrame, kickoff_frames: pd.DataFrame, first_touch_frames: pd.Series,
                               calculate_intensive_events: bool = False, clean: bool = True):

        """
        Sets some further data and cleans the replay;
        Then, performs the analysis.

        :param game: The game object (instance of Game). It contains the replay metadata and processed json data.
        :param proto_game: The game's protobuf (instance of game_pb2) (refer to the comment in get_protobuf_data() for more info).
        :param data_frame: The game's pandas.DataFrame object (refer to comment in get_data_frame() for more info).
        :param player_map: A map of player name to Player protobuf.
        :param kickoff_frames: Contains data about the kickoffs.
        :param first_touch_frames:  Contains data for frames where touches can actually occur.
        :param calculate_intensive_events: Indicates if expensive calculations should run to include additional stats.
        :param clean: Indicates if useless/invalid data should be found and removed.
        """

        self._get_game_time(proto_game, data_frame)
        if clean:
            clean_replay(game, data_frame, proto_game, player_map)
        self._log_time("Creating events...")
        self.events_creator.create_events(game, proto_game, player_map, data_frame, kickoff_frames, first_touch_frames,
                                          calculate_intensive_events=calculate_intensive_events)
        self._log_time("Getting stats...")
        self._get_stats(game, proto_game, player_map, data_frame)

    def _get_game_metadata(self, game: Game, proto_game: game_pb2.Game) -> Dict[str, Player]:
        """
        Processes protobuf data and sets the respective object fields to correct values.
        Maps the player's specific online ID (steam unique ID) to the player object.

        :param game: The game object (instance of Game). It contains the replay metadata and processed json data.
        :param proto_game: The game's protobuf (instance of game_pb2) (refer to the comment in get_protobuf_data() for more info).
        :return: A dictionary, with the player's online ID as the key, and the player object (instance of Player) as the value.
        """
        # Process the relevant protobuf data and pass it to the Game object (returned data is ignored).
        ApiGame.create_from_game(proto_game.game_metadata, game, self.id_creator)

        # Process the relevant protobuf data and pass it to the Game object's mutators (returned data is ignored).
        ApiMutators.create_from_game(proto_game.mutators, game, self.id_creator)

        # Process the relevant protobuf data and pass it to the Team objects (returned data is ignored).
        ApiTeam.create_teams_from_game(game, proto_game, self.id_creator)

        # Process the relevant protobuf data and add players to their respective parties.
        ApiGame.create_parties(proto_game.parties, game, self.id_creator)

        player_map = dict()
        for player in game.players:
            player_proto = proto_game.players.add()
            ApiPlayer.create_from_player(player_proto, player, self.id_creator)
            player_map[player.online_id] = player_proto

        return player_map

    def _get_game_time(self, protobuf_game: game_pb2.Game, data_frame: pd.DataFrame):
        """
        Calculates the game length (total time the game lasted) and sets it to the relevant metadata length field.
        Calculates the total time a player has spent in the game and sets it to the relevant player field.

        :param proto_game: The game's protobuf (instance of game_pb2) (refer to the comment in get_protobuf_data() for more info).
        :param data_frame: The game's pandas.DataFrame object (refer to comment in get_data_frame() for more info).
        """

        protobuf_game.game_metadata.length = data_frame.game[data_frame.game.goal_number.notnull()].delta.sum()
        for player in protobuf_game.players:
            try:
                player.time_in_game = data_frame[
                    data_frame[player.name].pos_x.notnull() & data_frame.game.goal_number.notnull()].game.delta.sum()
                player.first_frame_in_game = data_frame[player.name].pos_x.first_valid_index()
            except:
                player.time_in_game = 0

        logger.info("Set each player's in-game times.")

    def _get_kickoff_frames(self, game: Game, proto_game: game_pb2.Game, data_frame: pd.DataFrame):
        """
        Firstly, fetches kickoff-related data from SaltieGame.
        Secondly, checks for edge-cases and corrects errors.

        NOTE: kickoff_frames is an array of all in-game frames at each kickoff beginning.
        NOTE: first_touch_frames is an array of all in-game frames for each 'First Touch' at kickoff.

        :param game: The game object (instance of Game). It contains the replay metadata and processed json data.
        :param proto_game: The game's protobuf (instance of game_pb2) (refer to the comment in get_protobuf_data() for more info).
        :param data_frame: The game's pandas.DataFrame object (refer to comment in get_data_frame() for more info).
        :return: See notes above.
        """

        kickoff_frames = SaltieGame.get_kickoff_frames(game)
        first_touch_frames = SaltieGame.get_first_touch_frames(game)

        if len(kickoff_frames) > len(first_touch_frames):
            # happens when the game ends before anyone touches the ball at kickoff
            kickoff_frames = kickoff_frames[:len(first_touch_frames)]

        for goal_number, goal in enumerate(game.goals):
            data_frame.loc[kickoff_frames[goal_number]: goal.frame_number, ('game', 'goal_number')] = goal_number

        # Set goal_number of frames that are post last kickoff to -1 (ie non None)
        if len(kickoff_frames) > len(proto_game.game_metadata.goals):
            data_frame.loc[kickoff_frames[-1]:, ('game', 'goal_number')] = -1

        for index in range(min(len(kickoff_frames), len(first_touch_frames))):
            kickoff = proto_game.game_stats.kickoffs.add()
            kickoff.start_frame_number = kickoff_frames[index]
            kickoff.end_frame_number = first_touch_frames[index]

        return kickoff_frames, first_touch_frames

    def _get_stats(self, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                   data_frame: pd.DataFrame):
        """
        For each in-game frame after a goal has happened, calculate in-game stats.
        (i.e. player, team, general-game and hit stats)

        :param game: The game object (instance of Game). It contains the replay metadata and processed json data.
        :param proto_game: The game's protobuf (instance of game_pb2) (refer to the comment in get_protobuf_data() for more info).
        :param data_frame: The game's pandas.DataFrame object (refer to comment in get_data_frame() for more info).
        :param player_map: The dictionary with all player IDs matched to the player objects.
        """

        goal_frames = data_frame.game.goal_number.notnull()
        self.stats_manager.get_stats(game, proto_game, player_map, data_frame[goal_frames])

    def _store_frames(self, data_frame: pd.DataFrame):
        self.data_frame = data_frame
        self.df_bytes = PandasManager.safe_write_pandas_to_memory(data_frame)

    def _initialize_data_frame(self, game: Game):
        data_frame = SaltieGame.create_data_df(game)

        logger.info("Assigned goal_number in .data_frame")
        return data_frame

    def _create_player_id_function(self, game: Game) -> Callable:
        name_map = {player.name: player.online_id for player in game.players}

        def create_name(proto_player_id, name):
            proto_player_id.id = str(name_map[name])

        return create_name

    def _can_do_full_analysis(self, first_touch_frames) -> bool:
        """
        Check whether or not the replay satisfies the requirements for a full analysis.
        This includes checking:
            if at least 1 team is present;
            if the ball was touched at least once;
            if both teams have an equal amount of players.

        In some cases, the check for equal team sizes must be ignored due to spectators joining the match, for example.
        Therefore, this check is ignored by default.

        :param first_touch_frames: An array of all in-game frames for each 'First Touch' at kickoff.
        :return: Bool - true if criteria above are satisfied.
        """

        team_sizes = []
        for team in self.game.teams:
            team_sizes.append(len(team.players))

        if len(team_sizes) == 0:
            logger.warning("Not doing full analysis. No teams found")
            return False

        if len(first_touch_frames) == 0:
            logger.warning("Not doing full analysis. No one touched the ball")
            return False

        # if any((team_size != team_sizes[0]) for team_size in team_sizes):
        #     logger.warning("Not doing full analysis. Not all team sizes are equal")
        #     return False

        return True

    def _start_time(self):
        self.timer = time.time()
        logger.info("starting timer")

    def _log_time(self, message=""):
        end = time.time()
        logger.info("Time taken for %s is %s milliseconds", message, (end - self.timer) * 1000)
        self.timer = end
