from carball.generated.api import game_pb2


class ProtobufManager:

    @staticmethod
    def write_proto_out_to_file(file, proto_game: game_pb2.Game):
        file.write(proto_game.SerializeToString())

    @staticmethod
    def read_proto_out_from_file(file):
        proto_game = game_pb2.Game()
        proto_game.ParseFromString(file.read())
        return proto_game
