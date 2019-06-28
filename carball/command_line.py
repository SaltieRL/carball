import argparse
import carball
from google.protobuf.json_format import MessageToJson


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', type=str, required=True, help='Path to replay file that will be analyzed.')
    parser.add_argument('--output', '-o', type=str, required=True,
                        help='Path to the output file where the result will be saved.')
    parser.add_argument('--format', '-f', choices=['json', 'protobuf', 'gzip'], default='protobuf',
                        help='The format of the output file. Gzip format will be a compressed protobuf file.')
    args = parser.parse_args()

    manager = carball.analyze_replay_file(args.input)

    if args.format == 'protobuf':
        with open(args.output, 'wb') as f:
            manager.write_proto_out_to_file(f)
    elif args.format == 'json':
        proto_game = manager.get_protobuf_data()
        with open(args.output, 'w') as f:
            f.write(MessageToJson(proto_game))


if __name__ == '__main__':
    main()
