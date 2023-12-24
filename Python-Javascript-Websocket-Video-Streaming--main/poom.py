#!/usr/bin/env python
from fastapi import FastAPI ,Cookie, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import socketio

import uvicorn
from collections import  defaultdict
import os
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
 # (a)dmin)
sio = socketio.AsyncServer(async_mode='asgi',  cors_allowed_origins = ['https://admin.socket.io'])  
sio.instrument(auth={'username':'WB38' , 'password':os.environ['WB38']})
combined_asgi_app = socketio.ASGIApp(sio, app)


rooms =  {} # 방에 대한 모든 정보를 담음 rooms[room] 에서 키를 뽑아서 sid 리스트 획득
rooms =  defaultdict(dict) # rooms[roomnname][sid] = name    candidate , ice  
sid_2_rooms=  {}  # sid 를 통한 방 추적  sid_2_rooms[sid] = roomname

 

#==============================get============================================
def get_room_list():  # 저장 된 방 리스트 반환
    return list(rooms.keys)
 
def get_roommember_list(roomname): #저장된 방에 있는  멤버 sid 리스트 반환
    return list(rooms[roomname])

def get_room_sid_ice(roomname, sid): #저장된 방에 있는 멤버 sid 에 있는 정보 반환
    return rooms[roomname][sid]

def get_room_sid(sid):   # sid를통한 방 추출 
    return sid_2_rooms[sid]

#==============================set============================================
def save_rooms_info(roomname , sid , file):
    rooms[roomname][sid] = file

def save_roomuser_sid(roomname , sid): # sid 에 따른 방이름 저장
    sid_2_rooms[sid] = roomname
 
#==============================socketio property===============================
@app.get('/')
async def index():
    
    return FileResponse('fiddle.html')

@sio.on('connect')
async def coonnected(sid,*args, **kwargs):
    await sio.emit("fuckshit",list(rooms),to=sid) # 접속 시 모든 방에 대한 리스트 줌 방 보기  
    
@sio.on('join_room')
def joinroom(sid,*args, **kwargs):
    
    sio.emit('user-connect',sid,room=args[0]) # 추가 하기 위한 
    sio.emit('connected',get_roommember_list(args[0]), to= sid) # 해당 방안에 있는 리스트 주기 
    rooms[args[0]][sid] = args[1] # 초대장?  추가 
    sid_2_rooms[sid] = args[0] # sid  to  room 추가  
    sio.enter_room(sid=sid ,  room= args[0]) # 방안에 넣기  맨 나중에 한 이유는 리스트를 줄때 본인을 제외하고 주기 위함 
    
     
    
@sio.on('disconnect')
async def coonnected(sid,*args, **kwargs):
    sio.emit('user-disconnect',sid,room=sid_2_rooms) #나간사람 통지 
    sio.leave_room(sid=sid)
    rooms[args[0]][sid] = args[1] # 초대장?  추가 
    if sid  in get_roommember_list(args[0]):
        sio.leave_room(sid=sid , room=sid_2_rooms) # 나간사람 연결 강퇴
 
   
@sio.on('roomchange')
    
     

    
if __name__ == '__main__':

    uvicorn.run(combined_asgi_app, host='127.0.0.1', port=5000,reload=True)