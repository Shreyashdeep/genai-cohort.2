from pdb import run
from dotenv import load_dotenv
import os
import google.generativeai as genai
from datetime import datetime
import json
import requests

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY") 
def run_command(cmd_input):
    # Extract command from dictionary if input is a dictionary
    if isinstance(cmd_input, dict):
        cmd = cmd_input.get('cmd', '')
    else:
        cmd = str(cmd_input)
    result = os.system(cmd)
    return f"Command executed with exit code: {result}"
def get_weather(city: str):
    url= f"https://wttr.in/{city}?format=%C+%t"
    response= requests.get(url)
    if response.status_code == 200:
        return f"the weather in {city} is {response.text}"
    # else:
    #     return "something went wrong"

available_tools={
    "get_weather": get_weather,
    "run_command": run_command
}

SYSTEM_PROMPT = """You are a helpful ai assistant who is specialised in resolving user query.
You work on start, plan, action, observe mode. 
For the given user query and available tools,plan the step by step execute , based on the planning, select the relevant tool from the available tool.
Wait for the observation and based on the observation from the tool call resolve the user query.

Rules:
-follow the output JSON Format.
-Always perform one step at a time and wait for the next input.
-Carefully analyze the user query.

Available Tools:
1. get_weather(city: str) -> str: Takes a city name as an input and returns the current weather for the city.
2. run_command(cmd: str) -> str: Takes linux command as a string and executes the command and returns the output after execution.

Output JSON Format:
    {{
    "step": "string",
    "content":"string",
    "function": "The name of function if the step is action",
    "input": "The input parameter for the function"
    }}

Example:
User Query: What is the weather of New York?
    Output: {{"step": "plan" , "content": "the user is interested in weather data of New York"}}
    Output: {{"step": "plan" , "content": "From the available tools I should call get_weather "}}
    Output: {{"step": "action" ,  "function": "get_weather", "input": {"city": "New York"}}}
    Output: {{"step": "observe" , "content": "12 degree C"}}
    Output: {{"step": "output" , "content": "The weather for new york seems to be 12 degrees."}}
"""
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)

messages=[
    # {"role": "system", "parts": [ SYSTEM_PROMPT]}
]


while True:

   query= input("> ")
   messages.append({"role": "user", "parts": [query]})
   while True:
    response= model.generate_content(
        contents=messages,
        generation_config=genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
    )
    messages.append({"role": "assistant", "parts": [response.text]})
    parsed_response= json.loads(response.text)
    if parsed_response.get("step") == "plan":
        print("=", parsed_response.get("content"))
        continue
    if parsed_response.get("step") == "action":
        tool_name= parsed_response.get("function")
        tool_input= parsed_response.get("input")

        print(f"Tool Name: {tool_name} with input {tool_input}")

        if available_tools.get(tool_name) != False:
            output= available_tools[tool_name](tool_input) 
            messages.append({"role": "user", "parts": json.dumps({"step" : "observe", "output": output})})
            continue

    if parsed_response.get("step") == "output":
        print("=", parsed_response.get("content"))
        break
    
        
        




# response= model.generate_content(
#     # response_mime_type="application/json",
#     contents=[
#         {"parts" : [{"text" :"What is the weather in New York?"}], "role": "user"},
#         {"parts": [{"text": json.dumps({
#             "step": "plan",
#             "content": "The user wants to know the current weather in New York"
#         })}], "role": "assistant"},
#         {"parts": [{"text": json.dumps({
#             "step": "plan",
#             "content": "I need to use the get_weather function to retrieve the weather information for New York."
#         })}], "role": "assistant"},
#         {"parts": [{"text": json.dumps({"step": "action", "function": "get_weather", "input": {"city": "New York"}})}], "role": "assistant"},
#         {"parts": [{"text": json.dumps({"step": "observe", "output": "-10"})}], "role": "user"}
#     ],
#     generation_config=genai.types.GenerationConfig(
#         response_mime_type="application/json"
#     )
# )

# print(response.text) 