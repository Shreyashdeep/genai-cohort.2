# flake8:noqa
import json
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.types import Command, interrupt
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver

load_dotenv()   
@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]
tools=[human_assistance]
class State(TypedDict):
    messages: Annotated[list, add_messages]
    
llm= init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tools= llm.bind_tools(tools=tools)

def chatbot(state: State):
    message= llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}

tool_node=ToolNode(tools=tools)

graph_builder= StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)
def user_chat():
    DB_URI="mongodb://admin:admin@mongodb:27017"
    config={"configurable": {"thread_id": "21"}}
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo= create_chat_graph(mongo_checkpointer)
        while True:
            user_input= input("> ")
            state= State(
                messages=[{"role": "user", "content":user_input}]
            )
            for event in graph_with_mongo.stream(state, config, stream_mode="values"):
                if "messages" in event :
                    event["messages"][-1].pretty_print()
                
# user_chat()

def admin_call():
    DB_URI="mongodb://admin:admin@mongodb:27017"
    config={"configurable": {"thread_id": "21"}}
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo= create_chat_graph(mongo_checkpointer)
        state= graph_with_mongo.get_state(config=config)
        # print("last state", state)
        last_message= state.values['messages'][-1]
        # print("last message", last_message)
        tool_calls= last_message.additional_kwargs.get("tool_calls", [])
        # print("Tool call", tool_calls)
        user_query= None
        for call in tool_calls:
            if call.get("function", {}).get("name") == "human_assistance" :
                args= call["function"].get("arguments", "{}")
                try:
                    args_dict= json.loads(args)
                    user_query= args_dict.get("query")
                    # print("Got user querry", user_query)
                except json.JSONDecodeError:
                    print("Failed to decode function arguments.")
                    
        print("User has a querry", user_query)
        solution= input("> ")
        
        resume_command= Command(resume={"data": solution})
        for event in graph_with_mongo.stream(resume_command, config, stream_mode="values"):
            if "message" in event:
                event["message"][-1].pretty_print()
# admin_call()
user_chat()