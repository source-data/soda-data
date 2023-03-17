import os

from dotenv import load_dotenv

from src.soda_data.sdneo.db import Instance

load_dotenv()
SD_API_URL = os.getenv("SD_API_URL")
SD_API_USERNAME = os.getenv("SD_API_USERNAME")
SD_API_PASSWORD = os.getenv("SD_API_PASSWORD")

NEO_URI = os.getenv("NEO_URI")
NEO_USERNAME = os.getenv("NEO_USERNAME")
NEO_PASSWORD = os.getenv("NEO_PASSWORD")

DB = Instance(NEO_URI, NEO_USERNAME, NEO_PASSWORD)
