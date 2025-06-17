# flake8: noqa
import os
from typing import Annotated
import google.generativeai as genai
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
GOOGLE_API_KEY= os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
client=genai.GenerativeModel()



class ClassifyMessageResponse(BaseModel):
    is_coding_question: bool

class State(TypedDict):
    user_query: str
    llm_result: str |None
    accuracy_percentage: str | None
    is_coding_question: bool | None
    
def classify_message(state: State):
    query=state['user_query']
    SYSTEM_PROMPT="""
        You are an AI assistant. Your job is to detect if the user's query is related 
        to the coding question or not.
        Return the response in specified JSON boolean only.
    """
    response=client.generate_content(
        model="google_genai:  gemini-2.0-flash",
        # response_format= ClassifyMessageResponse,
        system_instructions= SYSTEM_PROMPT,
        contents=[
            {"parts":[{"text":query}],"role": "user"}
        ],
        config={
            "response_schema": ClassifyMessageResponse
        }
    )
    # print(response.text)
    result= response.text
    state["is_coding_question"]= result
    return state
