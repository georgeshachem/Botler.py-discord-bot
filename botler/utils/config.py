import os

class Config:
    def __init__(self):
        self.token = os.getenv("TOKEN")
        self.prefix = "&"
        self.description = "Botler by Georges"
        self.uri = "postgresql://root:password@{}:5432/botler"
        self.database = self.uri.format("localhost")
        self.migration = self.uri.format("localhost")