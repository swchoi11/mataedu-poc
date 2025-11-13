import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GEMINI_MODEL = "gemini-2.5-pro"

        self.POSTGRES_USER = os.getenv("POSTGRES_USER")
        self.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
        self.POSTGRES_HOST = "db"
        self.POSTGRES_DB = os.getenv("POSTGRES_DB")
        
        self.connection_string = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}"

        self.MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
        self.MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
        self.MINIO_BUCKET = os.getenv("MINIO_BUCKET_NAME")
        self.MINIO_HOST = os.getenv("MINIO_HOST")
        self.minio_connection_string = f"http://{self.MINIO_HOST}:9000"

config = Config()