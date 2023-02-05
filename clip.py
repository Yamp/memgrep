from share_btn import community_icon_html, loading_icon_html, share_js

import os, subprocess
import torch

def setup():
    install_cmds = [
        ['pip', 'install', 'ftfy', 'gradio', 'regex', 'tqdm', 'transformers==4.21.2', 'timm', 'fairscale', 'requests'],
        ['pip', 'install', 'open_clip_torch'],
        ['pip', 'install', '-e', 'git+https://github.com/pharmapsychotic/BLIP.git@lib#egg=blip'],
        ['git', 'clone', '-b', 'open-clip', 'https://github.com/pharmapsychotic/clip-interrogator.git']
    ]
    for cmd in install_cmds:
        print(subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8'))

setup()

# download cache files
print("Download preprocessed cache files...")
CACHE_URLS = [
    'https://huggingface.co/pharma/ci-preprocess/resolve/main/ViT-H-14_laion2b_s32b_b79k_artists.pkl',
    'https://huggingface.co/pharma/ci-preprocess/resolve/main/ViT-H-14_laion2b_s32b_b79k_flavors.pkl',
    'https://huggingface.co/pharma/ci-preprocess/resolve/main/ViT-H-14_laion2b_s32b_b79k_mediums.pkl',
    'https://huggingface.co/pharma/ci-preprocess/resolve/main/ViT-H-14_laion2b_s32b_b79k_movements.pkl',
    'https://huggingface.co/pharma/ci-preprocess/resolve/main/ViT-H-14_laion2b_s32b_b79k_trendings.pkl',
]
os.makedirs('cache', exist_ok=True)
for url in CACHE_URLS:
    print(subprocess.run(['wget', url, '-P', 'cache'], stdout=subprocess.PIPE).stdout.decode('utf-8'))

import sys
sys.path.append('src/blip')
sys.path.append('clip-interrogator')

import gradio as gr
from clip_interrogator import Config, Interrogator

config = Config()
config.device = 'cuda' if torch.cuda.is_available() else 'cpu'
config.blip_offload = False if torch.cuda.is_available() else True
config.chunk_size = 2048
config.flavor_intermediate_count = 512
config.blip_num_beams = 64

ci = Interrogator(config)

def inference(image, mode, best_max_flavors):
    image = image.convert('RGB')
    if mode == 'best':

        prompt_result = ci.interrogate(image, max_flavors=int(best_max_flavors))

        print("mode best: " + prompt_result)

        return prompt_result, gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)

    elif mode == 'classic':

        prompt_result = ci.interrogate_classic(image)

        print("mode classic: " + prompt_result)

        return prompt_result, gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)

    else:

        prompt_result = ci.interrogate_fast(image)

        print("mode fast: " + prompt_result)

        return prompt_result, gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)

title = """
    <div style="text-align: center; max-width: 500px; margin: 0 auto;">
        <div
        style="
            display: inline-flex;
            align-items: center;
            gap: 0.8rem;
            font-size: 1.75rem;
            margin-bottom: 10px;
        "
        >
        <h1 style="font-weight: 600; margin-bottom: 7px;">
            CLIP Interrogator 2.1
        </h1>
        </div>
        <p style="margin-bottom: 10px;font-size: 94%;font-weight: 100;line-height: 1.5em;">
        Want to figure out what a good prompt might be to create new images like an existing one?
        <br />The CLIP Interrogator is here to get you answers!
        <br />This version is specialized for producing nice prompts for use with Stable Diffusion 2.0 using the ViT-H-14 OpenCLIP model!
        </p>
    </div>
"""

article = """
<div style="text-align: center; max-width: 500px; margin: 0 auto;font-size: 94%;">

    <p>
    Server busy? You can also run on <a href="https://colab.research.google.com/github/pharmapsychotic/clip-interrogator/blob/open-clip/clip_interrogator.ipynb">Google Colab</a>
    </p>
    <p>
    Has this been helpful to you? Follow Pharma on twitter
    <a href="https://twitter.com/pharmapsychotic">@pharmapsychotic</a>
    and check out more tools at his
    <a href="https://pharmapsychotic.com/tools.html">Ai generative art tools list</a>
    </p>
</div>
"""

css = '''
#col-container {max-width: 700px; margin-left: auto; margin-right: auto;}
a {text-decoration-line: underline; font-weight: 600;}
.animate-spin {
    animation: spin 1s linear infinite;
}
@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}
#share-btn-container {
    display: flex; padding-left: 0.5rem !important; padding-right: 0.5rem !important; background-color: #000000; justify-content: center; align-items: center; border-radius: 9999px !important; width: 13rem;
}
#share-btn {
    all: initial; color: #ffffff;font-weight: 600; cursor:pointer; font-family: 'IBM Plex Sans', sans-serif; margin-left: 0.5rem !important; padding-top: 0.25rem !important; padding-bottom: 0.25rem !important;
}
#share-btn * {
    all: unset;
}
#share-btn-container div:nth-child(-n+2){
    width: auto !important;
    min-height: 0px !important;
}
#share-btn-container .wrap {
    display: none !important;
}
'''

with gr.Blocks(css=css) as block:
    with gr.Column(elem_id="col-container"):
        gr.HTML(title)

        input_image = gr.Image(type='pil', elem_id="input-img")
        with gr.Row():
            mode_input = gr.Radio(['best', 'classic', 'fast'], label='Select mode', value='best')
            flavor_input = gr.Slider(minimum=2, maximum=24, step=2, value=4, label='best mode max flavors')

        submit_btn = gr.Button("Submit")

        output_text = gr.Textbox(label="Description Output", elem_id="output-txt")

        with gr.Group(elem_id="share-btn-container"):
            community_icon = gr.HTML(community_icon_html, visible=False)
            loading_icon = gr.HTML(loading_icon_html, visible=False)
            share_button = gr.Button("Share to community", elem_id="share-btn", visible=False)

        examples=[['images/meme1.png', "best",4], ['images/meme2.png',"fast",4]]
        ex = gr.Examples(examples=examples, fn=inference, inputs=[input_image, mode_input, flavor_input], outputs=[output_text, share_button, community_icon, loading_icon], cache_examples=True, run_on_click=True)
        ex.dataset.headers = [""]

        gr.HTML(article)

    submit_btn.click(fn=inference, inputs=[input_image,mode_input,flavor_input], outputs=[output_text, share_button, community_icon, loading_icon], api_name="clipi2")
    share_button.click(None, [], [], _js=share_js)

server_name = '0.0.0.0'
port = 8989
block.queue(max_size=32,concurrency_count=20).launch(show_api=False, debug=True, show_error=True, port=port, server_name=server, share=False)
