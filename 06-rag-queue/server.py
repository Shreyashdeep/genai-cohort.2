

from fastapi import FastAPI, Query
from .queue.connection import queue
from .queue.worker import process_query

app = FastAPI()


@app.get("/")
def root():
    return {"status": "server is up and running"}


@app.post('/chat')
def chat(
    query: str = Query(..., desciption="Chat Message")
):
    job = queue.enqueue(process_query, query)
    return {"status": "queued", "job_id": job.id}     


#job_id=2bf702b0-d587-4369-9626-ae3c0dd681c0
#job_id=3accbbda-3a64-4d0e-a0a6-ea0c5082c379