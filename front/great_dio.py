import gradio as gr
from backend.apis import get_ans


with gr.Blocks() as demo:
    question = gr.Textbox(label="问题")
    answer = gr.Textbox(label="回复")
    btn = gr.Button(value="提交")
    with gr.Accordion(label='可能感兴趣的问题') as ac:
        with gr.Column(variant='panel'):
            with gr.Accordion(label='',open=False,visible=False) as lab1:
                md1 = gr.Markdown(value='')
            with gr.Accordion(label='',open=False,visible=False) as lab2:
                md2 = gr.Markdown(value='')
            with gr.Accordion(label='',open=False,visible=False) as lab3:
                md3 = gr.Markdown(value='')
            with gr.Accordion(label='',open=False,visible=False) as lab4:
                md4 = gr.Markdown(value='')

    btn.click(fn=get_ans,inputs=question,outputs=[answer,lab1,md1,lab2,md2,lab3,md3,lab4,md4,ac])

if __name__ == "__main__":
    demo.launch(server_port=8081)