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

sio = socketio.AsyncServer(async_mode='asgi' )
combined_asgi_app = socketio.ASGIApp(sio, app)


rooms =  {} # 방에 대한 모든 정보를 담음 rooms[room] 에서 키를 뽑아서 sid 리스트 획득
rooms =  defaultdict(dict) # rooms[roomnname][sid] = name    candidate , ice  

 

sid_2_rooms=  {}  # sid 를 통한 방 추적 
 

@app.get('/')
async def index():
    return FileResponse('fiddle.html')

@sio.on('connect')
async def coonnected(sid,*args, **kwargs):
    await sio.emit("fuckshit","helloworld",to=sid, )
    



@sio.on('disconnect')
async def coonnected(sid,*args, **kwargs):
    sio.emit("fuckshit","{sid}is disconnected",room=sid_2_rooms[sid])
    sio.disconnect(sid=sid)

    
if __name__ == '__main__':

    uvicorn.run(combined_asgi_app, host='127.0.0.1', port=5000)