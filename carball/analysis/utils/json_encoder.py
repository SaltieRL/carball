import json
import numpy as np


class CarballJsonEncoder(json.JSONEncoder):
    def default(self, o):
        # it cannot normally serialize np.int64 and possibly other np data types
        if type(o).__module__ == np.__name__:
            return o.item()
        return super(CarballJsonEncoder, self).default(o)
