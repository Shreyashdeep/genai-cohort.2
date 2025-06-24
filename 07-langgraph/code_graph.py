# # flake8: noqa
# import os
# from typing import Literal
# import google.generativeai as genai
# from typing_extensions import TypedDict
# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from dotenv import load_dotenv
# from pydantic import BaseModel
# import json

# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# genai.configure(api_key=GOOGLE_API_KEY)
# # client=genai.GenerativeModel()


# class ClassifyMessageResponse(BaseModel):
#     is_coding_question: bool


# class CodeAccuracyResponse(BaseModel):
#     accuracy_percentage: str
    


# class State(TypedDict):
#     user_query: str
#     llm_result: str | None
#     accuracy_percentage: str | None
#     is_coding_question: bool | None


# def classify_message(state: State):
#     query = state['user_query']
#     SYSTEM_PROMPT = """
#         You are an AI assistant. Your job is to detect if the user's query is related 
#         to the coding question or not.
#         Return the response in specified JSON boolean only.
#     """
#     model = genai.GenerativeModel(
#         "gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
#     response = model.generate_content(query)
#     result = response.text
#     state["is_coding_question"] = result
#     return state


# def route_query(state: State) -> Literal["general_query", "coding_query"]:
#     is_coding = state["is_coding_question"]
#     if is_coding:
#         return "coding_query"
#     return "general_query"


# def general_query(state: State):
#     query = state["user_query"]
#     model = genai.GenerativeModel("gemini-nano-2")
#     response = model.generate_content(
#         # model= "gemini-nano-2",
#         contents=[
#             {"parts": [{"text": query}], "role": "user"}
#         ]
#     )
#     state["llm_result"] = response.text
#     return state


# def coding_query(state: State):
#     query = state["user_query"]
#     SYSTEM_PROMPT = "You are a Coding Expert Agent"
#     model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
#     response = model.generate_content(
#         contents=[
#             {"parts": [{"text": query}], "role": "user"}
#         ]
#     )
#     state["llm_result"] = response.text
#     return state


# def coding_validate_query(state: State):
#     query = state["user_query"]
#     llm_code = state["llm_result"]
#     SYSTEM_PROMPT = f"""
#         You are expert in calculting accuracy of the code according to the question.
#         Return the percentage of accuracy.
#         user query: {query}
#         code: {llm_code}
#     """
#     model = genai.GenerativeModel(
#         "gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
#     response = model.generate_content(
#         contents=[
#              {"parts": [{"text": query}], "role": "user"}
#         ],
#         # generation_config={
#         #     "response_mime_type": "application/json",
#         #     "response_schema": ClassifyMessageResponse.model_json_schema()
#         # }
#     )
#     state["accuracy_percentage"] = response.text
#     return state


# graph_builder = StateGraph(State)
# # add node
# graph_builder.add_node("classify_message", classify_message)
# graph_builder.add_node("route_query", route_query)
# graph_builder.add_node("general_query", general_query)
# graph_builder.add_node("coding_query", coding_query)
# graph_builder.add_node("coding_validate_query", coding_validate_query)
# graph_builder.add_edge(START, "classify_message")
# graph_builder.add_conditional_edges("classify_message", route_query)
# graph_builder.add_edge("general_query", END)
# graph_builder.add_edge("coding_query", "coding_validate_query")
# graph_builder.add_edge("coding_validate_query", END)
# graph = graph_builder.compile()


# def main():
#     user = input("> ")
#     _state: State = {
#         "user_query": user,
#         "accuracy_percentage": None,
#         "is_coding_question": False,
#         "llm_result": None
#     }
#     response = graph.invoke(_state)
#     print(response)


# main()


# flake8: noqa

from typing_extensions import TypedDict
from openai import OpenAI
from typing import Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

load_dotenv()
client = OpenAI()


class ClassifyMessageResponse(BaseModel):
    is_coding_question: bool


class CodeAccuracyResponse(BaseModel):
    accuracy_percentage: str


class State(TypedDict):
    user_query: str
    llm_result: str | None
    accuracy_percentage: str | None
    is_coding_question: bool | None


def classify_message(state: State):
    print("⚠️ classify_message")
    query = state["user_query"]

    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to detect if the user's query is
    related to coding question or not.
    Return the response in specified JSON boolean only.
    """

    response = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=ClassifyMessageResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
    )

    is_coding_question = response.choices[0].message.parsed.is_coding_question
    state["is_coding_question"] = is_coding_question

    return state


def route_query(state: State) -> Literal["general_query", "coding_query"]:
    print("⚠️ route_query")
    is_coding = state["is_coding_question"]

    if is_coding:
        return "coding_query"

    return "general_query"


def general_query(state: State):
    print("⚠️ general_query")
    query = state["user_query"]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": query}
        ]
    )

    state["llm_result"] = response.choices[0].message.content

    return state


def coding_query(state: State):
    print("⚠️ coding_query")
    query = state["user_query"]

    SYSTEM_PROMPT = """
        You are a Coding Expert Agent
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )

    state["llm_result"] = response.choices[0].message.content

    return state


def coding_validate_query(state: State):
    print("⚠️ coding_validate_query")
    query = state["user_query"]
    llm_code = state["llm_result"]

    SYSTEM_PROMPT = f"""
        You are expert in calculating accuracy of the code according to the question.
        Return the percentage of accuracy
        
        User Query: {query}
        Code: {llm_code}
    """

    response = client.beta.chat.completions.parse(
        model="gpt-4.1",
        response_format=CodeAccuracyResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
    )

    state["accuracy_percentage"] = response.choices[0].message.parsed.accuracy_percentage
    return state


graph_builder = StateGraph(State)

# Define Nodes
graph_builder.add_node("classify_message", classify_message)
graph_builder.add_node("route_query", route_query)
graph_builder.add_node("general_query", general_query)
graph_builder.add_node("coding_query", coding_query)
graph_builder.add_node("coding_validate_query", coding_validate_query)

graph_builder.add_edge(START, "classify_message")
graph_builder.add_conditional_edges("classify_message", route_query)

graph_builder.add_edge("general_query", END)

graph_builder.add_edge("coding_query", "coding_validate_query")
graph_builder.add_edge("coding_validate_query", END)

graph = graph_builder.compile()


def main():
    user = input("> ")

    _state: State = {
        "user_query": user,
        "accuracy_percentage": None,
        "is_coding_question": False,
        "llm_result": None
    }

    for event in graph.stream(_state):
        print("Event", event)

    # response = graph.invoke(_state)

    # print(response)


main()