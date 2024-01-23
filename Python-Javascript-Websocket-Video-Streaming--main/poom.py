
from fastapi import FastAPI ,Cookie, File, UploadFile,APIRouter, Request,Response
from fastapi.responses import FileResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socketio
import wave
import uvicorn
import time
from io import BytesIO
from pydub import AudioSegment
from collections import  defaultdict
import os
from fastapi.middleware.cors import CORSMiddleware
import threading 
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI, Request, Depends, HTTPException, Cookie
from typing import Optional
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

#매니저 가져오기
manager = sio.manager
 #WB38                           your_password
users_in_room = {} # users_in_room[room_id] =[] sid]
rooms_sid = {} # rooms_sid[sid] = room_id
names_sid = {} # names_sid[sid] = client_name
sessions = {}# 사용자 정보를 저장할 딕셔너리
combined_asgi_app = socketio.ASGIApp(sio, app)
 
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
        "join.html", {"request": request,"room_id": room_id, "display_name": sessions[room_id]["name"], "mute_audio": sessions[room_id]["mute_audio"], "mute_video": sessions[room_id]["mute_video"]})
    return response
# @app.post("/file")
# async def upload_file(file:UploadFile,request:Request,
#                       dirname:Optional[str]=None,filename:Optional[str]=None):
#     content = await file.read()
#     filenamed = f"{str(filename)}.jpg"  # uuid로 유니크한 파일명으로 변경
#     with open(os.path.join(dirname, filenamed), "wb") as fp:
#         fp.write(content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)
 
#     return {"filename": filename}
#     # 한번에 받고 한번에 처리하는 방식

# @sio.on('voice')
# def handle_voice(sid,data): # blob 으로 들어온 데이터 
#     # BytesIO를 사용하여 메모리 상에서 오디오 데이터를 로드
#     audio_segment = AudioSegment.from_file(BytesIO(data), format="wav")
 
#     # 오디오 파일로 저장
#     directory = str(names_sid.get(sid))
#     if not os.path.exists(directory):
#         os.makedirs(directory)
 
#     # 오디오 파일로 저장
#     file_path = os.path.join(directory, f'{sid}.wav')
#     audio_segment.export(file_path, format='wav')
    
#     print('오디오 파일 저장 완료')
#     # sockeTIO 한번에 받고 한번에 처리하는 방식 

# # chunk for file 
# @sio.on('wave')
# def get_chunk(sid,chunk):  # BytesIO를 사용하여 메모리 상에서 오디오 데이터를 로드
#     audio_segment = AudioSegment.from_file(BytesIO(chunk), format="wav")
 
#     # 오디오 파일로 저장
#     directory = str(names_sid.get(sid))
#     if not os.path.exists(directory):
#         os.makedirs(directory)
 
#     # 오디오 파일로 저장
#     file_path = os.path.join(directory, f'{sid}.wav')
#     audio_segment.export(file_path, format='wav')
    
#     print('오디오 파일 저장 완료')
#     # sockeTIO 한번에 받고 한번에 처리하는 방식 



@sio.on("connect")
async def connected(sid,*args, **kwargs):     
     # 접속 시 모든 방에 대한 리스트 줌 방 보기  
     print("New socket connected ", sid)
      
@sio.on("join-room")
async def on_join_room(sid,data):
    room_id = data["room_id"]
    display_name = sessions[room_id]["name"]
    
    await sio.enter_room(room=room_id,sid=sid)
    rooms_sid[sid] = room_id
    names_sid[sid] = display_name
    ####
    print("[{}] New member joined: {}<{}>".format(room_id, display_name, sid))
    await sio.emit("user-connect",{"sid":sid, "name":display_name},room=room_id,skip_sid=sid)
    if room_id not in users_in_room:
        users_in_room[room_id] = [sid]
        await sio.emit("user-list", {"my_id": sid},to=sid)  # send own id only
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

    users_in_room[room_id].remove(sid)
    if len(users_in_room[room_id]) == 0:
        users_in_room.pop(room_id,None)

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
 



if __name__ == '__main__':

    uvicorn.run(combined_asgi_app, host='127.0.0.1', port=5000)