REPLICATED_ACTIVE_KEY = 'TAGame.CarComponent_TA:ReplicatedActive'
REPLICATED_RB_STATE_KEY = 'TAGame.RBActor_TA:ReplicatedRBState'
ACTIVE_KEY = 'TAGame.CarComponent_TA:Active'


class BaseActorHandler(object):
    type_name = None

    @classmethod
    def can_handle(cls, actor):
        return cls.type_name is not None and cls.type_name == actor['TypeName']

    def __init__(self, parser):
        self.parser = parser

    def update(self, actor, time, delta):
        pass

    def destroy(self, actor, time, delta):
        pass

    def post_process_frame(self, actor, time, delta):
        pass
