from .actor import *

REPLICATED_RB_STATE_KEY = 'TAGame.RBActor_TA:ReplicatedRBState'

_HANDLERS = [
    GameInfoHandler,
    GameEventHandler,
    BallHandler,
    PlayerHandler,
    TeamHandler,
    CarHandler,
    JumpHandler,
    DodgeHandler,
    DoubleJumpHandler,
    BoostHandler,
    BoostPickupHandler,
    CameraSettingsHandler,
    RumbleItemHandler,
    PlatformHandler
]

_PRIORITY_HANDLERS = [
    GameInfoHandler,
    PlayerHandler,
    CarHandler
]

# These handlers will also handle frames with a delta of 0 to match the old implementation
# TODO check if this is needed
_0_DELTA_HANDLERS = [
    GameInfoHandler,
    PlayerHandler
]


def parse_frames(game):
    """
    :return: all_data = {
        'player_ball_data': player_ball_data,
        'player_dicts': player_dicts,
        'team_dicts': team_dicts,
        'frames_data': frames_data,
        'cameras_data': cameras_data
        'demos_data': demos_data
    }

    player_ball_data format:
    {
    'ball': {frame_number: {pos_x, pos_y ...}, f_no2: {...} ...,}
    player_actor_id: {
        frame_number: {
            pos_x, pos_y ...,
            throttle, steer, ...,
            ping, ball_cam
        },
        f_no2: {...} ...,
    }

    currently implemented:
        inputs: posx, posy, posz, rotx, roty, rotz, vx, vy, vz, angvx, angy, angvz, boost_amt
        outputs: throttle, steer, handbrake, boost, jump, doublejump, dodge

    player_dicts  = {player_actor_id : {actor_data}, player_actor_id_2: {actor_data_2}}
    team_dicts = {team_actor_id: {actor_data, 'colour':'blue'/'orange', also includes name}
    frames_data = {frame_number: {time, delta, seconds_remaining, is_overtime, ball_has_been_hit}
    cameras_data = {player_actor_id: actor_data}
    demos_data = {frame_number: demolish_data}

    """
    parser = FrameParser(game.replay_data, game)
    parser.parse_frames()

    player_ball_data = parser.player_data
    player_ball_data['ball'] = parser.ball_data

    return {
        'player_ball_data': player_ball_data,
        'player_dicts': parser.player_dicts,
        'car_dicts': parser.car_dicts,
        'team_dicts': parser.team_dicts,
        'frames_data': parser.frames_data,
        'cameras_data': parser.cameras_data,
        'demos_data': parser.demos_data,
        'game_info_actor': parser.game_info_actor,
        'soccar_game_event_actor': parser.soccar_game_event_actor,
        'parties': parser.parties,
        'dropshot': parser.dropshot
    }


class FrameParser(object):

    def __init__(self, replay_frames, game):
        self.replay_frames = replay_frames
        self.game = game
        self.replay_version = game.replay_version
        self.objects = game.replay['objects']
        self.names = game.replay['names']
        self.class_indices = game.replay['class_indices']

        self.game_info_actor = None
        self.soccar_game_event_actor = None

        self.frames_data = {}
        self.ball_data = {}
        self.player_data = {}

        # dictionaries to contain data in frames
        self.parties = {}
        self.player_dicts = {}
        self.team_dicts = {}
        self.car_dicts = {}

        self.player_car_ids = {}  # player_actor_id: car_actor_id
        self.car_player_ids = {}  # car_actor_id: player_actor_id

        self.cameras_data = {}  # player_actor_id: actor_data
        self.demos_data = []  # frame_number: demolish_data

        # stores car_actor_ids to collect data for at each frame
        self.current_car_ids_to_collect = []

        self.actors = {}

        self.dropshot = {
            'tile_states': {},
            'damage_events': {},
            'ball_state': 0,
            'ball_events': [],
            'tile_frames': {}
        }

    def parse_frames(self):

        self.actors = {}
        handlers = [dict() for _ in range(len(_PRIORITY_HANDLERS) + 1)]
        handled_actors = set()

        current_goal_number = 0

        for i, frame in enumerate(self.replay_frames):
            time = frame['time']
            delta = frame['delta']

            for actor_id in frame['deleted_actors']:
                for handler_group in handlers:
                    handler_group.pop(actor_id, None)
                handled_actors.discard(actor_id)
                self.player_car_ids.pop(actor_id, None)
                self.car_player_ids.pop(actor_id, None)
                self.actors.pop(actor_id, None)

            for new_actor in frame['new_actors']:
                actor_id = new_actor['actor_id']
                object_name = self.objects[new_actor['object_id']]
                self.actors[actor_id] = {
                    'Id': actor_id,
                    'TypeName': object_name,
                    'ClassName': OBJECT_CLASSES.get(object_name, None),
                    'Name': self.names[new_actor['name_id']],
                }

                handler = next(filter(lambda handler_cls: handler_cls.can_handle(self.actors[actor_id]),
                                      _HANDLERS), None)

                if handler is not None:
                    try:
                        priority = _PRIORITY_HANDLERS.index(handler)
                    except ValueError:
                        priority = len(_PRIORITY_HANDLERS)

                    handlers[priority][actor_id] = handler(self), handler in _0_DELTA_HANDLERS
                    handled_actors.add(actor_id)

            for updated in frame['updated_actors']:
                actor_id = updated['actor_id']

                if actor_id not in self.actors:
                    continue

                actor = self.actors[actor_id]
                prop_name = self.objects[updated['object_id']]
                # update property
                actor[prop_name] = find_actual_value(updated['attribute'])

            # stop data collection after goal
            try:
                if i > self.game.goals[current_goal_number].frame_number:
                    # set all players to sleeping after goal
                    for car_actor_id in self.car_player_ids:
                        try:
                            car = self.actors[car_actor_id]
                            car[REPLICATED_RB_STATE_KEY]['Sleeping'] = True
                        except KeyError as e:
                            # Ignore the case where the car does not have a REPLICATED_RB_STATE_KEY
                            pass
                    current_goal_number += 1
            except IndexError:
                # after last goal.
                pass

            # apply the update handlers
            for handler_group in handlers:
                for actor_id, handler_tuple in handler_group.items():
                    handler = handler_tuple[0]

                    # skip 0 delta frames, except for these two handlers (matches old implementation)
                    if handler_tuple[1] or delta != 0:
                        handler.update(self.actors[actor_id], i, time, delta)

            self.current_car_ids_to_collect.clear()


def find_actual_value(attribute: dict):
    item = list(attribute.items())[0]
    attribute_type = item[0]
    attribute_value = item[1]

    if attribute_type == 'Flagged' or attribute_type == 'FlaggedByte':
        return attribute_value[1]
    return attribute_value


OBJECT_CLASSES = {
    "Archetypes.Ball.Ball_BasketBall_Mutator": "TAGame.Ball_TA",
    "Archetypes.Ball.Ball_Basketball": "TAGame.Ball_TA",
    "Archetypes.Ball.Ball_BasketBall": "TAGame.Ball_TA",
    "Archetypes.Ball.Ball_Beachball": "TAGame.Ball_TA",
    "Archetypes.Ball.Ball_Breakout": "TAGame.Ball_Breakout_TA",
    "Archetypes.Ball.Ball_Default": "TAGame.Ball_TA",
    "Archetypes.Ball.Ball_Trajectory": "TAGame.Ball_TA",
    "Archetypes.Ball.Ball_Haunted": "TAGame.Ball_Haunted_TA",
    "Archetypes.Ball.Ball_Puck": "TAGame.Ball_TA",
    "Archetypes.Ball.Ball_Anniversary": "TAGame.Ball_TA",
    "Archetypes.Ball.CubeBall": "TAGame.Ball_TA",
    "Archetypes.Ball.Ball_Training": "TAGame.Ball_TA",
    "Archetypes.Car.Car_Default": "TAGame.Car_TA",
    "Archetypes.CarComponents.CarComponent_Boost": "TAGame.CarComponent_Boost_TA",
    "Archetypes.CarComponents.CarComponent_Dodge": "TAGame.CarComponent_Dodge_TA",
    "Archetypes.CarComponents.CarComponent_DoubleJump": "TAGame.CarComponent_DoubleJump_TA",
    "Archetypes.CarComponents.CarComponent_FlipCar": "TAGame.CarComponent_FlipCar_TA",
    "Archetypes.CarComponents.CarComponent_Jump": "TAGame.CarComponent_Jump_TA",
    "Archetypes.GameEvent.GameEvent_Basketball": "TAGame.GameEvent_Soccar_TA",
    "Archetypes.GameEvent.GameEvent_BasketballPrivate": "TAGame.GameEvent_SoccarPrivate_TA",
    "Archetypes.GameEvent.GameEvent_BasketballSplitscreen": "TAGame.GameEvent_SoccarSplitscreen_TA",
    "Archetypes.GameEvent.GameEvent_Breakout": "TAGame.GameEvent_Soccar_TA",
    "Archetypes.GameEvent.GameEvent_Hockey": "TAGame.GameEvent_Soccar_TA",
    "Archetypes.GameEvent.GameEvent_HockeyPrivate": "TAGame.GameEvent_SoccarPrivate_TA",
    "Archetypes.GameEvent.GameEvent_HockeySplitscreen": "TAGame.GameEvent_SoccarSplitscreen_TA",
    "Archetypes.GameEvent.GameEvent_Items": "TAGame.GameEvent_Soccar_TA",
    "Archetypes.GameEvent.GameEvent_Season:CarArchetype": "TAGame.Car_TA",
    "Archetypes.GameEvent.GameEvent_Season": "TAGame.GameEvent_Season_TA",
    "Archetypes.GameEvent.GameEvent_Soccar": "TAGame.GameEvent_Soccar_TA",
    "Archetypes.GameEvent.GameEvent_SoccarLan": "TAGame.GameEvent_Soccar_TA",
    "Archetypes.GameEvent.GameEvent_SoccarPrivate": "TAGame.GameEvent_SoccarPrivate_TA",
    "Archetypes.GameEvent.GameEvent_SoccarSplitscreen": "TAGame.GameEvent_SoccarSplitscreen_TA",
    "Archetypes.SpecialPickups.SpecialPickup_BallFreeze": "TAGame.SpecialPickup_BallFreeze_TA",
    "Archetypes.SpecialPickups.SpecialPickup_BallGrapplingHook": "TAGame.SpecialPickup_GrapplingHook_TA",
    "Archetypes.SpecialPickups.SpecialPickup_BallLasso": "TAGame.SpecialPickup_BallLasso_TA",
    "Archetypes.SpecialPickups.SpecialPickup_BallSpring": "TAGame.SpecialPickup_BallCarSpring_TA",
    "Archetypes.SpecialPickups.SpecialPickup_BallVelcro": "TAGame.SpecialPickup_BallVelcro_TA",
    "Archetypes.SpecialPickups.SpecialPickup_Batarang": "TAGame.SpecialPickup_Batarang_TA",
    "Archetypes.SpecialPickups.SpecialPickup_BoostOverride": "TAGame.SpecialPickup_BoostOverride_TA",
    "Archetypes.SpecialPickups.SpecialPickup_CarSpring": "TAGame.SpecialPickup_BallCarSpring_TA",
    "Archetypes.SpecialPickups.SpecialPickup_GravityWell": "TAGame.SpecialPickup_BallGravity_TA",
    "Archetypes.SpecialPickups.SpecialPickup_StrongHit": "TAGame.SpecialPickup_HitForce_TA",
    "Archetypes.SpecialPickups.SpecialPickup_Swapper": "TAGame.SpecialPickup_Swapper_TA",
    "Archetypes.SpecialPickups.SpecialPickup_Tornado": "TAGame.SpecialPickup_Tornado_TA",
    "Archetypes.SpecialPickups.SpecialPickup_HauntedBallBeam": "TAGame.SpecialPickup_HauntedBallBeam_TA",
    "Archetypes.SpecialPickups.SpecialPickup_Rugby": "TAGame.SpecialPickup_Rugby_TA",
    "Archetypes.Teams.Team0": "TAGame.Team_Soccar_TA",
    "Archetypes.Teams.Team1": "TAGame.Team_Soccar_TA",
    "GameInfo_Basketball.GameInfo.GameInfo_Basketball:GameReplicationInfoArchetype": "TAGame.GRI_TA",
    "GameInfo_Breakout.GameInfo.GameInfo_Breakout:GameReplicationInfoArchetype": "TAGame.GRI_TA",
    "Gameinfo_Hockey.GameInfo.Gameinfo_Hockey:GameReplicationInfoArchetype": "TAGame.GRI_TA",
    "GameInfo_Items.GameInfo.GameInfo_Items:GameReplicationInfoArchetype": "TAGame.GRI_TA",
    "GameInfo_Season.GameInfo.GameInfo_Season:GameReplicationInfoArchetype": "TAGame.GRI_TA",
    "GameInfo_Soccar.GameInfo.GameInfo_Soccar:GameReplicationInfoArchetype": "TAGame.GRI_TA",
    "GameInfo_Tutorial.GameInfo.GameInfo_Tutorial:GameReplicationInfoArchetype": "TAGame.GRI_TA",
    "GameInfo_Tutorial.GameEvent.GameEvent_Tutorial_Aerial": "TAGame.GameEvent_Tutorial_TA",
    "TAGame.Default__CameraSettingsActor_TA": "TAGame.CameraSettingsActor_TA",
    "TAGame.Default__PRI_TA": "TAGame.PRI_TA",
    "TAGame.Default__Car_TA": "TAGame.Car_TA",
    "TheWorld:PersistentLevel.BreakOutActor_Platform_TA": "TAGame.BreakOutActor_Platform_TA",
    "TheWorld:PersistentLevel.CrowdActor_TA": "TAGame.CrowdActor_TA",
    "TheWorld:PersistentLevel.CrowdManager_TA": "TAGame.CrowdManager_TA",
    "TheWorld:PersistentLevel.InMapScoreboard_TA": "TAGame.InMapScoreboard_TA",
    "TheWorld:PersistentLevel.VehiclePickup_Boost_TA": "TAGame.VehiclePickup_Boost_TA",
    "Haunted_TrainStation_P.TheWorld:PersistentLevel.HauntedBallTrapTrigger_TA_1": "TAGame.HauntedBallTrapTrigger_TA",
    "Haunted_TrainStation_P.TheWorld:PersistentLevel.HauntedBallTrapTrigger_TA_0": "TAGame.HauntedBallTrapTrigger_TA",
    "Archetypes.Tutorial.Cannon": "TAGame.Cannon_TA"
}
