import datetime
import json


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            # datetime transformation
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, datetime.date):
            # date transformation
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)
