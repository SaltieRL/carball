import json
import logging
import pickle
from pathlib import Path

import carball
from carball.json_parser.game import Game
from carball.analysis.analysis_manager import AnalysisManager

logging.getLogger("carball").setLevel(logging.ERROR)

replays_folder_path = Path("D:\Replays\Replays\RLCS Season 7")

replays = replays_folder_path.glob("**/*.replay")

replay_parsing_file = Path("replay_parsing.json")

if replay_parsing_file.is_file():
    with replay_parsing_file.open("r") as f:
        replays_parsing = json.load(f)
else:
    replays_parsing = {}

for replay in replays:
    print("\n")
    print(replay)

    if replays_parsing.get(str(replay), False):
        print("\tReplay previously parsed. Skipping...")
        continue
    try:
        analysis_manager = carball.analyze_replay_file(str(replay))
        proto_game = analysis_manager.get_protobuf_data()
        dataframe = analysis_manager.get_data_frame()

        print(f"\tplayers name and score: {[(player.name, player.score) for player in proto_game.players]}")
        print(f"\tdf length: {len(dataframe)}")

        replays_parsing[str(replay)] = True
    except:
        import traceback

        traceback.print_exc()
        replays_parsing[str(replay)] = traceback.format_exc()

    with replay_parsing_file.open("w") as f:
        json.dump(replays_parsing, f, indent=4)
