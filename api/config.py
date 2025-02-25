# data for environment variables from .env file

import os

from dotenv import load_dotenv

class Config:
    PORT_API = 5000
    JWT_SECRET = 'secret'
    USER_LOGIN = 'admin'
    USER_PASSWORD = 'admin'
    
    def __init__(self):
        self.load_from_env_file()
        # check if the environment variables are set up
        if not self.PORT_API:
            raise ValueError('PORT_API is not set')
        if not self.JWT_SECRET:
            raise ValueError('JWT_SECRET is not set')
        if not self.USER_LOGIN:
            raise ValueError('USER_LOGIN is not set')
        if not self.USER_PASSWORD:
            raise ValueError('USER_PASSWORD is not set')
            

    def load_from_env_file(self):
        # set .env file path
        load_dotenv()
        # get the environment variables
        self.PORT_API = os.getenv('PORT_API')
        self.JWT_SECRET = os.getenv('JWT_SECRET')
        self.USER_LOGIN = os.getenv('USER_LOGIN')
        self.USER_PASSWORD = os.getenv('USER_PASSWORD')
        