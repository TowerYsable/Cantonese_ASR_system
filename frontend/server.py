from flask import Flask, render_template, request, send_from_directory, url_for
from file_handler import FileHandler
import json

from flask_cors import *

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('speech_recognition.html')


@app.route('/asr', methods=['POST'])
def asr():
    res = []
    for f in request.files:
        if f.startswith('audio_blob') and FileHandler.check_format(request.files[f]):

            response_code, filename, response = FileHandler.get_recognized_text(request.files[f])
            print('filename--->',filename, response)
            if response_code == 0:
                response_audio_url = url_for('media_file', filename=filename)
                response_se_audio_url = url_for('se_media_file', filename='enhance.wav')
                response_raw_2d_url = url_for('images_file', filename='raw_2d.png')
                response_raw_3d_url = url_for('images_file', filename='raw_3d.png')
                response_se_2d_url = url_for('images_file', filename='se_2d.png')
                response_se_3d_url = url_for('images_file', filename='se_3d.png')
                print('*'*100)
                print(response_raw_2d_url, response_raw_3d_url, response_se_2d_url, response_se_3d_url)
            else:
                response_audio_url = None
                response_se_audio_url = None
                response_raw_2d_url, response_raw_3d_url, response_se_2d_url, response_se_3d_url =None,None,None,None

            res.append({
                'response_audio_url': response_audio_url,
                'response_se_audio_url': response_se_audio_url,
                'response_code': response_code,
                'response': response,
                'response_raw_2d_url': response_raw_2d_url,
                'response_raw_3d_url': response_raw_3d_url,
                'response_se_2d_url': response_se_2d_url,
                'response_se_3d_url': response_se_3d_url,
            })
    return json.dumps({'r': res}, ensure_ascii=False)


@app.route('/media/<path:filename>', methods=['GET'])
def media_file(filename):
    return send_from_directory('./records', filename, as_attachment=False)


@app.route('/media_en/<path:filename>', methods=['GET'])
def se_media_file(filename):
    return send_from_directory('./web_servers/FullSubNet-plus/outputs', filename, as_attachment=False)

@app.route('/images/<path:filename>', methods=['GET'])
def images_file(filename):
    return send_from_directory('./images', filename, as_attachment=False)

if __name__ == '__main__':
    print('启动中...')
    app.run(port=5074,host='127.0.0.1')