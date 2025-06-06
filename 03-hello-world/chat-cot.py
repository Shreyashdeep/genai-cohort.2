import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize the client with your API key
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the client
genai.configure(api_key=GOOGLE_API_KEY)

# Set up the model
SYSTEM_PROMPT = """You are an helpfull ai assistant who is specialized in resolving user query.
For the given user input , analyze the input and break down the problem step by step .
The steps are you get a user input , then you analyze , think , you think again and think several times and then return the output with and explanation .
Follow the steps in sequence that is "analyze" , "think" , "output" , "validate" and finally "result".

Rules:
1. Follow the strict JSON output as per schema .
2. Always perform one step at a time and wait for the next input.
3. Carefully analyze the user querry.

Output format:
{{"step": "string", "content": "string"}}

EXAMPLES:
Input: What is 2+2
OUtput: {{"step": "analyze", "content": "Alright ! The user is interestd in maths queries and he is askig a basic arithmetic problem"}}
Output: {{"step": "think", "content": "To perform this additon , I must go from left to right and add all the operands."}}
Output: {{"step": "output", "content": "4"}}
Output: {{"step": "validate", "content": "seems like 4 is correct answer for 2+2"}}
Output: {{"step": "result", "content": "2+2=4 and this is calculatd by adding all the numbers "}}
"""

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT,
)

response = model.generate_content(
    contents=[
        {"parts": [{"text": "What is 5 / 2 *3 to the power 4"}], "role": "user"}
    ]
)

# Print the response
print(response.text)