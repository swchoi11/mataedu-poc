import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GEMINI_MODEL = "gemini-2.5-pro"

config = Config()