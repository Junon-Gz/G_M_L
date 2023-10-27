from fastapi import FastAPI
from front.great_dio import demo
import gradio as gr
import uvicorn
app = FastAPI()



@app.get("/")
def read_main():
    return {"message": "This is your main app"}

app = gr.mount_gradio_app(app, demo, path="/gradio")

if __name__ == "__main__":
    uvicorn.run("start:app",port=9001,reload=True)