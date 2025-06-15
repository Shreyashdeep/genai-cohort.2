# flake8: noqa
import uvicorn
from .server import app
from dotenv import load_dotenv
import os
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def main():
    uvicorn.run(app, port=8000, host="0.0.0.0")



main()