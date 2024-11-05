import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
AI_DEVS_SERVER = os.environ.get("AI_DEVS_SERVER")
AI_DEVS_USER_TOKEN = os.environ.get("AI_DEVS_USER_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
