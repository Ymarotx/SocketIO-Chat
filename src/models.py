from pydantic import BaseModel


class User(BaseModel):
    room: str
    name: str
    messages: str

class Message(BaseModel):
    text: str
    author: str