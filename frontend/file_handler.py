import os
import subprocess
import time
import logging
import uuid
from opencc import OpenCC
import requests,json
from audio_visualization import audio_vis

complex_to_simple = OpenCC('t2s')

def text_process(text, subject):
    text_process_api = 'http://127.0.0.1:5073/get_text_process'
    headers = {'Content-Type':'application/json'}
    data = {
        "textId": '1',
        "textString": text,
        "subject": subject,
    }
    resp = requests.post(text_process_api, headers = headers, json = data)
    res = json.loads(resp.content)
    return res['text_res'][0]

def text_punc(text):
    punc_api = 'http://127.0.0.1.45:5072/get_punc_restore'
    headers = {'Content-Type':'application/json'}
    data = {
        "textId": '1',
        "textString": text
    }
    resp = requests.post(punc_api, headers = headers, json = data)
    res = json.loads(resp.content)
    return res['punc_res_text']

def speech_enhancement_info(converted_record_path):
    speech_enhancement_info_api = 'http://127.0.0.1:5071/get_speech_enhancement'
    headers = {'Content-Type':'application/json'}
    converted_record_path =  '../../' + converted_record_path.replace('./','')
    data = {
        "textId": '1',
        'path': converted_record_path,
    }
    resp = requests.post(speech_enhancement_info_api, headers = headers, json = data)
    res = json.loads(resp.content)
    if res['code'] == 200:
        return 200
    return 404

def speech_recognizer(audio_path):
    asr_info_api = 'http://127.0.0.1:5070/get_asr_text'
    headers = {'Content-Type':'application/json'}
    data = {
        "textId": '1',
        'path': audio_path,
    }
    resp = requests.post(asr_info_api, headers = headers, json = data)
    res = json.loads(resp.content)
    return res['asr_text']

class FileHandler:
    @staticmethod
    def get_recognized_text(blob):
        try:
            filename = str(uuid.uuid4())
            os.makedirs('./records', exist_ok=True)
            new_record_path = os.path.join('./records', filename + '.webm')
            blob.save(new_record_path)
            new_filename = filename + '.wav'
            converted_record_path = FileHandler.convert_to_wav(new_record_path, new_filename)
            response_models_result = FileHandler.get_models_result(converted_record_path)
            return 0, new_filename, response_models_result
        except Exception as e:
            logging.exception(e)
            return 1,  None, str(e)

    @staticmethod
    def convert_to_wav(webm_full_filepath, new_filename):
        converted_record_path = os.path.join('./records', new_filename)
        subprocess.call('ffmpeg -i {0} -ar 16000 -b:a 256k -ac 1 -sample_fmt s16 {1}'.format(
                webm_full_filepath, converted_record_path
            ),
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        os.remove(webm_full_filepath)
        return converted_record_path

    @staticmethod
    def check_format(files):
        return (files.mimetype.startswith('audio/') or [
            files.filename.endswith(audio_format) for audio_format in [
                'mp3', 'ogg', 'acc', 'flac', 'au', 'm4a', 'mp4', 'mov', 'avi', 'wmv', '3gp', 'flv', 'mkv'
            ]
        ])
        return True

    @staticmethod
    def get_models_result(converted_record_path, delimiter='<br>'):
        results = []
        start = time.time()
        print('开始识别...')
        if speech_enhancement_info(converted_record_path) == 200:
            se_wav_path = './outputs/enhance.wav'
            audio_vis(converted_record_path, 'raw')
            audio_vis(se_wav_path, 'se')
            audio_vis_info = True
        else:
            se_wav_path = ''
            audio_vis_info = False

        complex_se_text = speech_recognizer(se_wav_path)
        complex_text = speech_recognizer(converted_record_path)

        without_punc_text = complex_text.replace('，','').replace('。','').replace('！','').replace('？','')
        without_punc_se_text = complex_se_text.replace('，','').replace('。','').replace('！','').replace('？','')
        
        text = complex_to_simple.convert(complex_text)
        se_text = complex_to_simple.convert(complex_se_text)

        # text = text_punc(text)
        itn_text = text_itn(text,'化学')

        # se_text = text_punc(se_text)
        se_itn_text = text_itn(se_text,'化学')

        end = time.time()
        results.append(
            {
                'text': text + '<br>' + se_text,
                'time': round(end - start, 3),
                'confidence': 'decoder_result.score',
                'words': 'decoder_result.words',
                'complex_text': text + '<br>' + se_text,
                'itn_text': itn_text + '<br>' + se_itn_text,
                'without_punc_text': without_punc_text + '<br>' + without_punc_se_text,
                'audio_vis_info': audio_vis_info,
            }
        )
        print('--'*20)
        print(results)
        print('--'*20)
        return results
