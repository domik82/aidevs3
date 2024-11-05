class ResponseBaseHandler:
    def __init__(self, response_json):
        self.response_json = response_json
        self.code = self.response_json.get("code", None)
        self.message = self.response_json.get("message", None)
