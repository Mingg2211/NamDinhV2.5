from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bot_brain import bot_searching, mingg
from pydantic import BaseModel
import uvicorn


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    value: str

@app.post("/bot_searching")
def ranking_utter(item: Item):
    if item!='' and item:
        
        result = bot_searching(item.value)
    else:
        result = "Nhập lại nhé"
    return {"ranking_answer": result}

if __name__ == "__main__":
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)