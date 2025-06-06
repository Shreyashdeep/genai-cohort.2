import os
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file
load_dotenv()

# Initialize the client with the API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Make the API call
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=["How does AI work?"]
)
print(response.text)
