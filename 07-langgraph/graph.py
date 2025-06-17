# flake8: noqa
import os
from typing import Annotated
import google.generativeai as genai
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY= os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

model=genai.GenerativeModel("gemini-1.5-flash")
class State(TypedDict):
    query: str   
    llm_result: str | None
    
def chat_bot(state: State):
    query= state['query']
    #gemini calll
    #llm call
    llm_response= model.generate_content(
        contents=[
            {"parts": [{"text": query}], "role": "user"}
        ]
    )
    result=llm_response.text
    state["llm_result"]= result
    return state
    


graph_builder = StateGraph(State)
graph_builder.add_node("chat_bot", chat_bot )
graph_builder.add_edge(START, "chat_bot")
graph_builder.add_edge("chat_bot", END)


graph= graph_builder.compile()

def main():
    user= input("> ")
    _state= {
        "query": user,
        "llm_result": None
    }
    graph_result=graph.invoke(_state)
    print("Graph result", graph_result)
    
main()