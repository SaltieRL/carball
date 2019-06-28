import argparse
import carball
from carball.json_parser.game import Game
from carball.analysis.analysis_manager import AnalysisManager
from google.protobuf.json_format import MessageToJson


def main():
    parser = argparse.ArgumentParser(description='Rocket League replay parsing and analysis.')
    parser.add_argument('--input', '-i', type=str, required=True,
                        help='Path to replay file that will be analyzed. Carball expects a raw replay file unless '
                             '--skip-decompile is provided.')
    parser.add_argument('--output', '-o', type=str, required=True,
                        help='Path to the output file where the result will be saved.')
    parser.add_argument('--format', '-f', choices=['json', 'protobuf', 'gzip'], default='protobuf',
                        help='The format of the output file. Gzip format will be a compressed protobuf file.')
    parser.add_argument('--skip-decompile', '-sd', action='store_true', default=False,
                        help='If set, carball will treat the input file as a json file that Rattletrap outputs.')
    args = parser.parse_args()

    if args.skip_decompile:
        manager = carball.analyze_replay_file(args.input)
    else:
        game = Game()
        game.initialize(loaded_json=args.input)
        manager = AnalysisManager(game)
        manager.create_analysis()

    if args.format == 'protobuf':
        with open(args.output, 'wb') as f:
            manager.write_proto_out_to_file(f)
    elif args.format == 'json':
        proto_game = manager.get_protobuf_data()
        with open(args.output, 'w') as f:
            f.write(MessageToJson(proto_game))


if __name__ == '__main__':
    main()
