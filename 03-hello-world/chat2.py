import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize the client with your API key
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the client
genai.configure(api_key=GOOGLE_API_KEY)

# Set up the model
SYSTEM_PROMPT = """You are an AI expert in coding. You only know Python and nothing else.
You help users in solving their Python doubts only and nothing else.
If a user tries to ask something else apart from Python, you roast them.


EXAMPLES:
User: how to make a tea?
text: what makes you think I am a chef you piece of crap.
"""

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",  # Using a more stable model
    system_instruction=SYSTEM_PROMPT
)

response = model.generate_content(
    contents=[
        {"parts": [{"text": "How to make a tea?"}], "role": "user"}
    ]
)

# Print the response
print(response.text)