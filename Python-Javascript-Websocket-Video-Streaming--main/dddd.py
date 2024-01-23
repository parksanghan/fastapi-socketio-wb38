
from fastapi import FastAPI ,Cookie, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import socketio
import socket 
import numpy as np
import base64
import uvicorn
import io 
import asyncio
import soundfile
import ffmpeg 
import aiofiles
import wave
from pydub import AudioSegment
from collections import  defaultdict,UserDict,OrderedDict
import os
import threading 
import time
ddf="F:\fastapi-socketio-wb38\dddd\TDxOtYZ3ODS9v8LjAAAF.wav"
ddw="F:\fastapi-socketio-wb38\dddd\TDxOtYZ3ODS9v8LjAAAF.wav"
infiles = ["dddd\TDxOtYZ3ODS9v8LjAAAF.wav", "dddd\TDxOtYZ3ODS9v8LjAAAF_chunk.wav"]
outfile = "dddd\TDxOtYZ3ODS9v8LjAAAF.wav"
# 비동기적으로 파일 쓰기를 처리하는 함수
async def write_wav_async(file_path, audio_segment):
    async with aiofiles.open(file_path, 'wb') as file:
        await file.write(audio_segment.raw_data)

# 파일 쓰기가 완료된 후 호출될 콜백 함수
def on_file_write_complete(file_path):
    print(f'파일 쓰기 완료: {file_path}')
    # 추가로 수행할 작업을 여기에 추가하십시오.

# 메인 로직을 처리하는 함수
async def main_logic():
    # 예시로 사용할 AudioSegment 객체 생성
    audio_segment = AudioSegment.from_file(io.BytesIO(ddf), format='wav')

    # 파일 경로 설정
     

    # 파일 쓰기 작업을 비동기로 실행
    write_task = asyncio.create_task(write_wav_async(ddw, audio_segment))

    # 작업 완료 후 콜백을 등록
    write_task.add_done_callback(lambda task: on_file_write_complete(ddw))

    # 메인 로직 계속 진행
    print("다른 메인 로직 수행 중...")

    # 메인 로직이 계속 실행됩니다.

 
loop = asyncio.get_event_loop()
loop.run_until_complete(main_logic())
loop.close()
if __name__ == '__main__':
    
    main_logic()
    time.sleep(10)