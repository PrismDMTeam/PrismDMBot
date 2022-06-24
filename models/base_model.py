from abc import ABC
from redis_om import JsonModel

class BaseModel(JsonModel, ABC):
    class Meta:
        global_key_prefix = 'pr'

# from redis_om import Migrator
# Migrator().run()