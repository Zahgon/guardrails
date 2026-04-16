from datetime import datetime
from dataclasses import asdict, is_dataclass
from pydantic import BaseModel
from json import JSONEncoder


class DefaultJSONEncoder(JSONEncoder):
    def default(self, o):
        pass
