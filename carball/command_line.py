import argparse
import carball
import logging
import gzip
from carball.json_parser.game import Game
from carball.analysis.analysis_manager import AnalysisManager
from google.protobuf.json_format import MessageToJson


def main():
    parser = argparse.ArgumentParser(description='Rocket League replay parsing and analysis.')
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Path to replay file that will be analyzed. Carball expects a raw replay file unless '
                             '--skip-decompile is provided.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Path to the output file where the result will be saved.')
    parser.add_argument('-f', '--format', choices=['json', 'protobuf', 'gzip'], default='protobuf',
                        help='The format of the output file. Gzip format will be a compressed protobuf file.')
    parser.add_argument('-sd', '--skip-decompile', action='store_true', default=False,
                        help='If set, carball will treat the input file as a json file that Rattletrap outputs.')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Set the logging level to INFO. To set the logging level to DEBUG use -vv.')
    parser.add_argument('-s', '--silent', action='store_true', default=False,
                        help='Disable logging altogether.')
    args = parser.parse_args()

    log_level = logging.WARNING

    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG

    if args.silent:
        logging.basicConfig(handlers=[logging.NullHandler()])
    else:
        logging.basicConfig(handlers=[logging.StreamHandler()], level=log_level)

    if args.skip_decompile:
        game = Game()
        game.initialize(loaded_json=args.input)
        manager = AnalysisManager(game)
        manager.create_analysis()
    else:
        manager = carball.analyze_replay_file(args.input)

    if args.format == 'protobuf':
        with open(args.output, 'wb') as f:
            manager.write_proto_out_to_file(f)
    elif args.format == 'json':
        proto_game = manager.get_protobuf_data()
        with open(args.output, 'w') as f:
            f.write(MessageToJson(proto_game))
    elif args.format == 'gzip':
        with gzip.open(args.output, 'wb') as f:
            manager.write_pandas_out_to_file(f)


if __name__ == '__main__':
    main()
