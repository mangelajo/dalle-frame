from flask import Flask, request, jsonify
from threading import Thread
import dalleframe
import os

last_prompt = None
last_filename = None

app = Flask(__name__,
            static_url_path='/static/',
            static_folder='static',
            template_folder='templates')

@app.route("/")
def hello():
    return "Hello!"


@app.route("/generate")
def generate():
    global last_prompt
    prompt = request.args.get('prompt')
    wait = request.args.get('wait', "false").lower() in ['true', '1']
    last_prompt = prompt
    return generate_image(prompt, wait)


def generate_image(prompt, wait):
    global last_filename
    if wait:
        filename = dalleframe.request_image(prompt)
        last_filename = filename
        dalleframe.display_eink_image(filename)
        return '<img src="'+ filename + '"/>'
    else:
        def threaded_task(prompt):
            global last_filename
            filename = dalleframe.request_image(prompt)
            last_filename = filename
            dalleframe.display_eink_image(filename)

        thread = Thread(target=threaded_task, args=(prompt,))
        thread.daemon = True
        thread.start()

        return jsonify({'thread_name': str(thread.name),
                'started': True})

@app.route("/regenerate")
def regenerate():
    global last_prompt
    wait = request.args.get('wait', "false").lower() in ['true', '1']
    return generate_image(last_prompt, wait)


SAVE_DIR="/mnt/nas/saved"

@app.route("/save")
def save():
    global last_filename
    os.system("cp " + last_filename + " " + SAVE_DIR)
    return "done"

if __name__ == "__main__":
    app.run()

