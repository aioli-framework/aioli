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

    def __init__(self, name, *args, **kwargs):
        self._name = name

        with self._get_db() as db:
            if name not in db:
                db[self._name] = {}

    def _get_db(self, *args, **kwargs):
        return shelve.open(self._db_path, *args, writeback=True, **kwargs)

    @property
    def age_seconds(self):
        with self._get_db() as db:
            state = db[self._name]
            if UPDATED_ON not in state:
                return math.inf

            return (datetime.now() - state[UPDATED_ON]).total_seconds()

    def __getitem__(self, key):
        with self._get_db() as db:
            state = db[self._name]
            return state[key] if key in state else None

    def __setitem__(self, key, value):
        with self._get_db() as db:
            state = db[self._name]

            if key not in state:
                state[key] = {}

            state[UPDATED_ON] = datetime.now()
            state[key] = value
