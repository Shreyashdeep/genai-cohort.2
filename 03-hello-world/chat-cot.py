import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
load_dotenv()

# Initialize the client with your API key
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the client
genai.configure(api_key=GOOGLE_API_KEY)
model= genai.GenerativeModel("gemini-1.5-flash")

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
EXAMPLES:
Input: What is 2+2*5/3
OUtput: {{"step": "analyze", "content": "Alright ! The user is interestd in maths queries and he is askig a basic arithmetic problem"}}
Output: {{"step": "think", "content": "To perform this additon , I must use BODMAS rule."}}
Output: {{"step": "validate", "content": "correct, using bodmas is the right approach"}}
Output: {{"step": "output", "content": "10/3"}}
Output: {{"step": "validate", "content": "seems like 10/3 is correct answer for 2+2*5/3"}}
Output: {{"step": "result", "content": "2+2*5/3=10/3 and this is calculatd by adding all the numbers "}}
"""
chat_history= []
query= input("> ")
chat_history.append({"role": "user", "parts": [SYSTEM_PROMPT + "\n\n" + query] })

while True:
    response=model.generate_content(
        contents=chat_history,
        generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Keep temperature low for deterministic behavior
                response_mime_type='application/json' # Request JSON output directly
            )

    )
    chat_history.append({"role": "assistant", "parts": [response.text]})
    parsed_responses = json.loads(response.text)
    # Handle both single response (dict) and multiple responses (list)
    responses = parsed_responses if isinstance(parsed_responses, list) else [parsed_responses]
    
    for resp in responses:
        if resp.get("step") != "result":
            print("=", resp.get("content"))
            continue
        # else:
        #     print("Result: ", resp.get("content"))
        #     break
    print("Result: ", resp.get("content"))
    break