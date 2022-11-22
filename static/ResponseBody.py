class ResponseBody:
    """ response body of http """

    def __init__(self, message="", status_code="", code=200):
        self.message = message
        self.status_code = status_code
        self.code = code
