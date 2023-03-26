import os


class Config:
    def __init__(self):
        self.token = os.getenv("TOKEN")
        self.prefix = "&"
        self.description = "Botler by Georges"
        self.database_username = os.getenv("DATABASE_USERNAME")
        self.database_password = os.getenv("DATABASE_PASSWORD")
        self.database_host = os.getenv("DATABASE_HOST")
        self.database_port = os.getenv("DATABASE_PORT")
        self.database_name = os.getenv("DATABASE_NAME")
        self.database_uri = "postgres://{}:{}@{}:{}/{}".format(
            self.database_username, self.database_password, self.database_host, self.database_port, self.database_name)
