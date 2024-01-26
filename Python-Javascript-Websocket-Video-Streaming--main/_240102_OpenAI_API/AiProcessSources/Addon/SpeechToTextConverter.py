 
import os
from google.cloud import speech, storage
from datetime import datetime, timedelta

from Addon.CustomConsolePrinter import printError,printNor, printProcess, printSucceed,printWarning


class SpeechToTextConverter() :
    def __init__(self) :
        self.sttClient = speech.SpeechClient()
        self.bucketName = "kamos_speech_to_text"
        
        # ���� ���丮�� Ŭ���̾�Ʈ ��ü ����
        self.stoClient = storage.Client()
        self.sttBucket = self.stoClient.bucket(self.bucketName)
        
        
        

    def upload_file(self, source_file) :
        
        printProcess("���� ������ ���ε� ���Դϴ�.")
        
        current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S');
        file_extension = os.path.splitext(source_file)[1]
        

        new_blob = self.sttBucket.blob(current_time_str + file_extension)

        new_blob.upload_from_filename(source_file)
        
        bucket_name = "kamos_speech_to_text"
        
    
        gsutil_url = f"gs://{bucket_name}/{current_time_str + file_extension}"
        printSucceed(f"���������� ���� ������ ���ε��߽��ϴ�. gsutil : {gsutil_url}")
        
        return gsutil_url
        

    def transcribe_gcs(self, gcs_uri: str) -> str:
        sttClient = self.sttClient

        audio = speech.RecognitionAudio(uri=gcs_uri)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz= 48000,
            language_code="ko-KR", 
        )

        operation = sttClient.long_running_recognize(config=config, audio=audio)

        printProcess("SpeechToText �۾��� �����մϴ�...")
        response = operation.result(timeout=3600)

        transcript_builder = []
        # Each result is for a consecutive portion of the audio. Iterate through
        # them to get the transcripts for the entire audio file.
        for result in response.results:
            # The first alternative is the most likely one for this portion.
            transcript_builder.append(f"\nTranscript: {result.alternatives[0].transcript}")
            transcript_builder.append(f"\nConfidence: {result.alternatives[0].confidence}")
        
        transcript = ""
        for result in response.results :
            transcript += result.alternatives[0].transcript + "\n"
            
    
        printSucceed("���������� SpeechToText������ �������Ǿ����ϴ�.")
    
        return transcript