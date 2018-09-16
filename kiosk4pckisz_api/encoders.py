from decimal import Decimal
from json import JSONEncoder


class DynamoDBEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if o == int(o):
                return int(o)
            return float(o)

        return JSONEncoder.default(self, o)
