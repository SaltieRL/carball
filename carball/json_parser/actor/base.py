REPLICATED_ACTIVE_KEY = 'TAGame.CarComponent_TA:ReplicatedActive'
REPLICATED_RB_STATE = 'TAGame.RBActor_TA:ReplicatedRBState'
ACTIVE_KEY = 'TAGame.CarComponent_TA:Active'


class BaseActorHandler(object):
    type_name = None

    @classmethod
    def can_handle(cls, actor):
        return cls.type_name is not None and cls.type_name == actor['TypeName']

    def __init__(self, parser):
        self.parser = parser
        self._our_car = False

    def update(self, actor, time, delta):
        pass

    def destroy(self, actor, time, delta):
        pass

    def post_process_frame(self, actor, time, delta):
        pass

    def set_frame_data(self, key, value, section='base'):
        if section is None:
            return

        if section not in self.parser.frame_data:
            self.parser.frame_data[section] = {}
        self.parser.frame_data[section][key] = value

    def get_if_none(self, data_key, actor, actor_key):
        """
        Get a value from an actor if we don't already have it in our dict

        :param data_key: key of the value in our dict
        :param actor: the actor
        :param actor_key: ky of the value in the actor
        """
        if self.parser.data.get(data_key) is None:
            self.parser.data[data_key] = actor.get(actor_key, None)

    def clear_data(self, *args, section='base'):
        for arg in args:
            self.parser.frame_data[section].pop(arg, None)
