
from fastapi import FastAPI ,Cookie, File, UploadFile,APIRouter, Request,Response
from fastapi.responses import FileResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socketio
import wave
import uvicorn
import time
import asyncio
from io import BytesIO
from pydub import AudioSegment
from collections import  defaultdict
import os
from fastapi.middleware.cors import CORSMiddleware
import threading 
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI, Request, Depends, HTTPException, Cookie
from typing import Optional
from AiModuleProcess import AiModuleProcess
import aiofiles
import socket
import io
import os, threading, time, subprocess
 
 
app : FastAPI = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# 비동기 서버 생성
sio : socketio.AsyncServer = socketio.AsyncServer(async_mode='asgi',  
                          credits=True,
                           cors_allowed_origins = [
                            
                           "*",
                           'http://localhost:5000',
                           'https://admin.socket.io',
                           'http://127.0.0.1:5000'  # 추가: Socket.IO 서버의 주소를 명시]
                        
                           ])  
app.add_middleware( ##
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5000',
        'https://admin.socket.io',
        'http://127.0.0.1:5000'
       
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#관리자 모드 인증 설정
# sio.instrument(auth=False) # 권한 없이 접속하기
sio.instrument({'username':'WB38' , 'password':os.environ['WB38']})
 
#socketIO와 FastAPI를 합치기
combined_asgi_app = socketio.ASGIApp(sio, app)
ai = None
#매니저 가져오기
manager = sio.manager
 #WB38                           your_password
users_in_room = {} # users_in_room[room_id] =[] sid]
rooms_sid = {} # rooms_sid[sid] = room_id
names_sid = {} # names_sid[sid] = client_name
sessions = {}# 사용자 정보를 저장할 딕셔너리
is_turtor =  {} # 최초 개설자 즉 튜터 : 튜터에게서 voice 이벤트를 받음 
lock_threading = {}
combined_asgi_app = socketio.ASGIApp(sio, app)
 
@app.get('/')
async def index():
 
  
    return FileResponse('fiddle.html')

@app.get('/rr')
async def inindex():
 
    return FileResponse('codecfile.html')
 
@app.get('/join',response_class=HTMLResponse,name='join')
async def index(request:Request,
          room_id:Optional[str]=None,
          display_name:Optional[str]=None,
          mute_audio:Optional[str]=None,
          mute_video:Optional[str]=None
 
            ):
    # display_name = request.query_params.get('display_name')
    # mute_audio = request.query_params.get('mute_audio')  # 1 or 0
    # mute_video = request.query_params.get('mute_video')  # 1 or 0
    # room_id = request.query_params.get('room_id')
    sessions[room_id]= {"name": display_name,
                        "mute_audio": mute_audio, "mute_video": mute_video}
    # 세션에 사용자 정보 저장
    response =   templates.TemplateResponse(
        "join.html", {"request": request,"room_id": room_id, "display_name": sessions[room_id]["name"],
                       "mute_audio": sessions[room_id]["mute_audio"], "mute_video": sessions[room_id]["mute_video"]})
    return response


@app.post("/upload")
async def upload_file(sid,file: UploadFile = File(...)):
    # 파일 확장자 확인
    directory = "upload"
    file_ext = file.filename.split(".")[-1].lower()
    if not os.path.exists(directory):
        os.makedirs(directory)
    # 파일 확장자가 txt 또는 pdf인지 확인
  
    if file_ext == "txt":
        filepath = os.path.join(directory,f'{sid}.wav')
        task = asyncio.create_task(save_uploaded_file(file,filepath))
        task.add_done_callback(callback_with_txt(rooms_sid.get(sid),filepath))
    elif file_ext == "pdf":
        filepath = os.path.join(directory,f'{sid}.pdf')
        task = asyncio.create_task(save_uploaded_file(file,filepath))
        task.add_done_callback(callback_with_pdf(rooms_sid.get(sid),filepath))
    else :
        raise HTTPException(status_code=400, detail="Only txt or pdf files are allowed")
    # 파일 저장
    
async def save_uploaded_file(file: UploadFile, target_path: str):
    async with aiofiles.open(target_path, 'wb') as out_file:
        content     = await file.read()
        await out_file.write(content)

def callback_with_txt(lecture,filepath):
    ai.DoSendDataTxt(lecture,filepath) #txt 전송 # 파인튜닝 버퍼에 넣기 

def callback_with_pdf(lectire,filepath):
    ai.DoSendDataPdf((lectire,filepath))# pdf 전송  # 파인튜닝 버퍼에 넣기 
  
     
def callback_turtor_exit(lectrue,filepath):
    ai.DoSendDataWav(lectrue,filepath) # wav 파일 전송 #파인튜닝 버퍼에 넣기 
    ai.DoFineTuneCreate(lecture=lectrue) #파인튜닝 시작
    
 

async def save_done_wav_file(sid):
    room_id = rooms_sid.get(sid)
    filepath = os.path.join(room_id,f'{sid}.wav')
    ai.DoSendDataWav((room_id,filepath))

@sio.on('question') # 사용자가 보낸 Questiob Request 
def handle_question(sid,message):
   ai.DoGetAnswer(sid,rooms_sid.get(sid),message)
@sio.on('voice1')
def handle_voice(sid,data): # blob 으로 들어온 데이터 
    # BytesIO를 사용하여 메모리 상에서 오디오 데이터를 로드
    audio_segment = AudioSegment.from_file(BytesIO(data), format="webm")
    directory = "dddd"
    # 오디오 파일로 저장
    #directory = str(names_sid.get(sid))
    if not os.path.exists(directory):
        os.makedirs(directory)
 
    # 오디오 파일로 저장
    file_path = os.path.join(directory, f'{sid}.wav')
    audio_segment.export(file_path, format='wav') 
    print('오디오 파일 저장 완료')
    # sockeTIO 한번에 받고 한번에  처리하는 방식 

async def get_file_lock(file_path):
    if file_path not in lock_threading:        
        lock_threading[file_path] = asyncio.Lock()
    return lock_threading[file_path]


@sio.on('voice')
async def voice_received(sid,data):
    asyncio.create_task(handle_voice(sid,data))
async def handle_voice(sid,data): # blob 으로 들어온 데이터 
    # BytesIO를 사용하여 메모리 상에서 오디오 데이터를 로드
  
    #audio_segment = AudioSegment.from_file()
    # 오디오 파일로 저장
    directory = str(rooms_sid.get(sid))
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, f'{sid}.wav')
    file_chunk_path = os.path.join(directory,f'{sid}chunk.wav')
    # 오디오 파일로 저장
    # 아래의 파일저장부분 
    if not os.path.exists(file_path): # 처음 보낸 chunk 의 경우 
       async with await get_file_lock(file_path=file_path):
        audio_segment:AudioSegment = AudioSegment.from_file(io.BytesIO(data), format="webm")
        audio_segment.export(file_path,format='wav')
       #await write_file(file_path=file_path, audio_segment=audio_segment)
    else:                             # 처음 이외에 보내는 chunk의 경우 .wav 파일에 대한 합성
        async with await get_file_lock(file_path=file_path):
            audio_segment:AudioSegment = AudioSegment.from_file(io.BytesIO(data), format="webm")
            audio_segment.export(file_chunk_path,format='wav')
       
            await handle_audio_chunk(file_path,file_chunk_path)
    print('오디오 파일 저장 완료')
# 아래함수를 쓰레드 함수로 만들가 
async def handle_audio_chunk(filepath,chukpath):
    
    infiles = [ filepath,
                chukpath]
    outfile = os.path.join(filepath) 


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
 


@sio.on("connect")
async def connected(sid,*args, **kwargs):     
     # 접속 시 모든 방에 대한 리스트 줌 방 보기
 
    print("New socket connected ", sid)
      
@sio.on("join-room")
async def on_join_room(sid,data):
    room_id = data["room_id"]
    display_name = sessions[room_id]["name"]
    
    await sio.enter_room(room=room_id,sid=sid)
    ai.DoLectureCreate(room_id) # room id 로 강의 생성 
    rooms_sid[sid] = room_id
    names_sid[sid] = display_name
    ####
    print("[{}] New member joined: {}<{}>".format(room_id, display_name, sid))
    await sio.emit("user-connect",{"sid":sid, "name":display_name},room=room_id,skip_sid=sid)
    if room_id not in users_in_room:
        users_in_room[room_id] = [sid]
        is_turtor[sid] = rooms_sid.get(sid)
        await sio.emit("user-list", {"my_id": sid},to=sid)  # send own id only
        await sio.emit("tutor",to=sid)
    else:
        usrlist = {u_id: names_sid[u_id]
                   for u_id in users_in_room[room_id]}
        await sio.emit("user-list", {"list": usrlist, "my_id": sid},to=sid)
         # add new member to user list maintained on server
        users_in_room[room_id].append(sid) # 인식안되는데 됨 
        print("\nusers: ", users_in_room, "\n")

@sio.on("disconnect")
async def on_disconnect(sid,*args, **kwargs):
    room_id =  rooms_sid.get(sid)
    display_name =  names_sid.get(sid)

    print("[{}] Member left: {}<{}>".format(room_id, display_name, sid))
    await sio.emit("user-disconnect",{"sid": sid} 
                   ,room=room_id,skip_sid=sid)
    if room_id and users_in_room.get(room_id) and users_in_room[room_id].get(sid):
        users_in_room[room_id].remove(sid)
    if  room_id and users_in_room.get(room_id) and len(users_in_room[room_id]) == 0:
        users_in_room.pop(room_id,None)
        ai.DoLectureDelete(rooms_sid.get(sid))
        ai.DoSessionDelete(sid,rooms_sid.get(sid)) 
 
    if is_turtor.get(sid):
        directory = "upload"
        callback_turtor_exit(rooms_sid.get(sid),os.path.join
                            (directory+f'{sid}.wav'))
    is_turtor.pop(sid,None)
    rooms_sid.pop(sid,None)
    names_sid.pop(sid,None)
    
    await sio.leave_room(sid=sid,room=room_id)
    print("\nusers: ", users_in_room, "\n")

@sio.on("data")
async def on_data(sid,data):
    sender_sid = data['sender_id']
    target_sid = data['target_id']
    if sender_sid != sid:
        print("[Not supposed to happen!] request.sid and sender_id don't match!!!")

    if data["type"] != "new-ice-candidate":
        print('{} message from {} to {}'.format(
            data["type"], sender_sid, target_sid))
    await sio.emit('data', data, to=target_sid)
# 요청에 대한 콜백 부분 
 
if __name__ == '__main__':
  
    ai = AiModuleProcess(sio=sio)
    uvicorn.run(combined_asgi_app, host='127.0.0.1', port=5000)
  
    
    
    
 