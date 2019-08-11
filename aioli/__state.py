import shelve
import math

from datetime import datetime

UPDATED_ON = "__updated_on__"


class StateMeta(type):
    _instances = {}

    def __call__(cls, name, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[name] = super(StateMeta, cls).__call__(name, *args, **kwargs)

        return cls._instances[name]


class State(metaclass=StateMeta):
    _db_path = ".aioli-state"

    def __init__(self, name, lifetime_secs=math.inf):
        self._name = name
        self._lifetime_secs = lifetime_secs

        with self._get_db() as db:
            if name not in db:
                db[self._name] = {}

    def _get_db(self, *args, **kwargs):
        return shelve.open(self._db_path, *args, writeback=True, **kwargs)

    def __getitem__(self, key):
        with self._get_db() as db:
            state = db[self._name]

            if key in state:
                update_time, data = state[key]
                if self._lifetime_secs > (datetime.now() - update_time).total_seconds():
                    return data

            return {}

    def __setitem__(self, key, value):
        with self._get_db() as db:
            state = db[self._name]

            if key not in state:
                state[key] = {}

            state[key] = datetime.now(), value
