class ResponseBody:
    """ response body of http """

    def __init__(self, message="", data="", code=200):
        self.message = message
        self.data = data
        self.code = code
