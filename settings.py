# settings.py
import os
from dotenv import load_dotenv
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
todoist_token = os.getenv("TODOIST_TOKEN")
