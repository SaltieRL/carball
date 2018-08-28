from json_parser.game import Game


def check_game(game: Game):
    # TODO: Create 3 Levels of errors: Critical, Major, Minor, mark each as such and return a list/dict of errors.

    for player in game.players:
        assert player.is_orange is not None
        assert player.online_id is not None
        assert player.team is not None