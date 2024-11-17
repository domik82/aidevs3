import json


def extract_json_from_wrapped_response(response):
    start = response.index("{")
    end = response.index("}") + 1
    json_str = response[start:end]
    return json.loads(json_str)
