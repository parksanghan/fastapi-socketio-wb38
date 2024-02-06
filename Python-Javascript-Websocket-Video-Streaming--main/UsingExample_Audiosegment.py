from pydub import AudioSegment
import os
import wave
import aiofiles
import asyncio
import io
lock_threading = {} # 같을파일에 대해서 접근시 lock 걸고 다른 파일에 대해서는 새로운 쓰레드를 통해 제어 
#@sio.on('voice')
async def handle_voice(sid,data): # blob 으로 들어온 데이터 
   control_voice(sid,data) 

async def control_voice(sid,data):
    try:
     # BytesIO를 사용하여 메모리 상에서 오디오 데이터를 로드
        audio_segment:AudioSegment = AudioSegment.from_file(io.BytesIO(data), format="webm")
    #audio_segment = AudioSegment.from_file()
    # 오디오 파일로 저장
        directory = str("dddd")
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, f'{sid}.wav')
        file_chunk_path = os.path.join(directory,f'{sid}chunk.wav')
    # 오디오 파일로 저장
    # 아래의 파일저장부분 
        if not os.path.exists(file_path): # 처음 보낸 chunk 의 경우 
            async with get_file_lock(file_path=file_path): # 파일을 통한 딕셔너리로 lock 형태 지정
        #audio_segment.export(file_path, format='wav')
                write_wav_func(file_path,audio_segment) # lock은 코드블럭을 나가면 해제 

        else:                             # 처음 이외에 보내는 chunk의 경우 .wav 파일에 대한 합성 
        #audio_segment.export(file_chunk_path,format='wav')
            async  with get_file_lock(file_path=file_chunk_path):
                await write_wav_func(file_chunk_path,audio_segment)
                # 파일 쓰기가 완료 된 뒤에 파일 합치기
                handle_audio_chunk(directory,filepath=file_path,chukpath=file_chunk_path)
        print('오디오 파일 저장 완료')
    except:
        print("파일 처리 중 에러 발생")
        
# 아래함수를 쓰레드 함수로 만들가 
async def handle_audio_chunk(directory,filepath,chukpath):
    
    infiles = [directory+ '\\' + filepath,
                directory+'\\'+chukpath]
    outfile = [directory+'\\'+filepath]


    data= []
    for infile in infiles:
        w = wave.open(os.getcwd()+'/'+infile, 'rb')
        data.append([w.getparams(), w.readframes(w.getnframes())])
        w.close()
    
    output = wave.open(outfile, 'wb')

    output.setparams(data[0][0])

    for i in range(len(data)):
        output.writeframes(data[i][1])
    output.close()

async def get_file_lock(file_path):
    if file_path not in lock_threading:        
        lock_threading[file_path] = asyncio.Lock()
    return lock_threading[file_path]

async def write_wav_func(file_path, audio_segment:AudioSegment):
    # 파일 쓰기를 비동기적으로 진행
    task= asyncio.create_task(write_file(file_path, audio_segment.raw_data))
    
    # 작업이 완료되면 콜백 호출
    task.add_done_callback(lambda fut: file_write_callback(fut))

async def write_file(file_path, raw_data):

    async with aiofiles.open(file_path, 'wb') as file:
        await file.write(raw_data)

def file_write_callback(future):
    # 파일 쓰기 작업이 완료되면 실행되는 콜백 함수
    if future.exception() is not None:
        print(f"파일 쓰기 중 에러 발생: {future.exception()}")
    else:
        print("파일 쓰기 완료")