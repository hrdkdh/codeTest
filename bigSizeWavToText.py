"""
러닝타임이 긴 long size wav파일에서 텍스트 추출
"""

import os

from google.cloud import storage
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "GongamSTT-fdaf5c0f2661.json"

CREDENTIALS_FILE = 'GongamSTT-fdaf5c0f2661.json'
BUCKETNAME="gongamsttaudiofile"

clientStorage=storage.Client.from_service_account_json(CREDENTIALS_FILE)
bucket=clientStorage.get_bucket(BUCKETNAME)

clientSpeech = speech.SpeechClient()

filename=withposco_po_with_20181210.wav
audio = types.RecognitionAudio(uri="gs://"+BUCKETNAME+"/"+filename)
config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code='ko-KR')

operation = clientSpeech.long_running_recognize(config, audio)

print('Waiting for operation to complete...')
response = operation.result(timeout=60*60) #제한시간 1시간

# Each result is for a consecutive portion of the audio. Iterate through
# them to get the transcripts for the entire audio file.
resultsStr=""
for result in response.results:
    # The first alternative is the most likely one for this portion.
    resultsStr=resultsStr+" "+result.alternatives[0].transcript
    print(u'Transcript: {}'.format(result.alternatives[0].transcript))
    print('Confidence: {}'.format(result.alternatives[0].confidence))

f=open('output.txt','w')
f.write(resultsStr)
f.close()
