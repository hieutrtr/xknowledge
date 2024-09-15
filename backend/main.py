import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage
from pydantic import BaseModel
from typing import List, Dict
from graph.graph import main_graph
from config import config
import uuid

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

def _print_event(message: dict, max_length=1500) -> str:
    # current_state = event.get("dialog_state")
    # if current_state:
    #     print("Currently in: ", current_state[-1])
    # if message:
    #     print("\nmessage structure:")
    #     print(f"Type: {type(message[-1])}")
    #     print(f"Attributes: {dir(message[-1])}")
    #     print(f"Content: {message[-1]}")
    #     if isinstance(message, list):
    #         message = message[-1]
        # check if the message is a AIMessage
    print("message:", message)
    msg_repr = message.content if message.content else ""
    msg_repr = f"{msg_repr}"
    return msg_repr

async def stream_graph_response(messages: List[Dict[str, str]]):
    thread_id = str(uuid.uuid4())

    graph_config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }
    for chunk in main_graph.stream({"messages": messages}, config=graph_config, stream_mode="values"):
        message = chunk.get("messages")
        if isinstance(message, list):
            message = message[-1]
        if isinstance(message, AIMessage) and message.content:
            yield _print_event(message)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    messages = [{"role": "user", "content": msg.content} for msg in request.messages]
    return StreamingResponse(stream_graph_response(messages), media_type="text/event-stream")

@app.get("/health")
async def health_check():
    return {"status": "ok", "model": config.ASSISTANT_MODEL}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)