from django.shortcuts import render
from django.shortcuts import HttpResponse
import json
import mindslab.KoreanTTS_client as tts
from cloopin.settings import BASE_DIR, MINDSLAB_STATIC_WAV_DIR
from shutil import move
import os


def index(request):
    return render(request, 'mindslab/index.html')


def run_tts_audio(request):
    if request.method == 'POST':
        tts_data = request.POST.get('tts_data')
        wav_fname = tts.KoreanTTS_client(tts_data)
        resp_data = {}
        if wav_fname:
            move(os.path.join(BASE_DIR, wav_fname),
                 os.path.join(BASE_DIR, MINDSLAB_STATIC_WAV_DIR, wav_fname))
            # resp_data['wav_url'] = os.path.join(BASE_DIR, MINDSLAB_STATIC_WAV_DIR, wav_fname)
            resp_data['wav_url'] = os.path.join('../static/mindslab/wav', wav_fname)
        else:
            resp_data['wav_url'] = 'Fail'

        return HttpResponse(
            json.dumps(resp_data),
            content_type="application/json"
        )
    else:
        print("\n @ Error: request method is NOT post.\n")
        return HttpResponse(
            json.dumps({'url': 'Fail'}),
            mimetype="application/json"
        )
