from typing import Union

from fastapi import FastAPI , Query

app = FastAPI()


@app.get("/")
def chat():
    return {"status": "server is up and running"}


@app.post('/chat')
def chat(
    query: str =Query(..., desciption="Chat Message")
):
    pass    