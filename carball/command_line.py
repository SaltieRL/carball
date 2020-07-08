import argparse
import carball
import logging
import gzip


def main(program_args=None):
    parser = argparse.ArgumentParser(description='Rocket League replay parsing and analysis.')
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Path to replay file that will be analyzed. Carball expects a raw replay file unless '
                             '--skip-decompile is provided.')
    parser.add_argument('--proto', type=str, required=False,
                        help='The result of the analysis will be saved to this file in protocol buffers format.')
    parser.add_argument('--json', type=str, required=False,
                        help='The result of the analysis will be saved to this file in json file format.')
    parser.add_argument('--gzip', type=str, required=False,
                        help='The pandas data frame containing the replay frames will be saved to this file in a '
                             'compressed gzip format.')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Set the logging level to INFO. To set the logging level to DEBUG use -vv.')
    parser.add_argument('-s', '--silent', action='store_true', default=False,
                        help='Disable logging altogether.')
    parser.add_argument('-dr', '--dry-run', action='store_true', default=False,
                        help='Explicitly notifying that there is not going to be any output to be saved')
    if program_args is not None:
        args = parser.parse_args(program_args)
    else:
        args = parser.parse_args()

    if not args.proto and not args.json and not args.gzip and not args.dry_run:
        parser.error('at least one of the following arguments are required: --proto, --json, --gzip')

    log_level = logging.WARNING

    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG

    if args.silent:
        logging.basicConfig(handlers=[logging.NullHandler()])
    else:
        logging.basicConfig(handlers=[logging.StreamHandler()], level=log_level)

    manager = carball.analyze_replay_file(args.input)

    if args.proto:
        with open(args.proto, 'wb') as f:
            manager.write_proto_out_to_file(f)
    if args.json:
        with open(args.json, 'w') as f:
            manager.write_json_out_to_file(f)
    if args.gzip:
        with gzip.open(args.gzip, 'wb') as f:
            manager.write_pandas_out_to_file(f)


if __name__ == '__main__':
    main()
