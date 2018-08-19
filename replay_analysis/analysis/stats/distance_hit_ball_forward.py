from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..saltie_game.saltie_game import SaltieGame


def get_distance_hit_ball_forward(saltie_game: 'SaltieGame') -> Dict[str, float]:
    distance_hit_ball_forward: Dict[str, float] = {
        player.name: 0
        for team in saltie_game.api_game.teams for player in team.players
    }
    saltie_hits = saltie_game.saltie_hits
    hit_frame_numbers = list(saltie_hits.keys())
    for hit_number, hit_frame_number in enumerate(hit_frame_numbers):
        saltie_hit = saltie_hits[hit_frame_number]
        try:
            next_hit_frame_number = hit_frame_numbers[hit_number + 1]
            next_saltie_hit = saltie_hits[next_hit_frame_number]
        except IndexError:
            continue

        hit_distance_forward = next_saltie_hit.hit.ball_data.pos_y - saltie_hit.hit.ball_data.pos_y

        player_is_orange = saltie_hit.hit.player.is_orange
        if player_is_orange:
            hit_distance_forward *= -1

        if hit_distance_forward > 0:
            distance_hit_ball_forward[saltie_hit.hit.player.name] += hit_distance_forward

    return distance_hit_ball_forward
