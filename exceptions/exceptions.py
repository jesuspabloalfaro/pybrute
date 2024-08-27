class Exceptions(Exception):
    def __init__(self, message="An error occurred", code=500):
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self):
        return f"[Error {self.code}]: {self.message}"
