
from fastapi import FastAPI ,Cookie, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import socketio
import socket 
import uvicorn
from collections import  defaultdict
import os
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
 # (admin)
sio = socketio.AsyncServer(async_mode='asgi',  
                          credits=True,
                           cors_allowed_origins = [
                            
                           
                           'http://localhost:5000',
                           'https://admin.socket.io',
                           'http://127.0.0.1:5000'  # 추가: Socket.IO 서버의 주소를 명시]
                           
                           ])  

sio.instrument(auth=False
               #{'username':'WB38' , 'password':os.environ['WB38']}
                     )
 

 #WB38                           your_password

combined_asgi_app = socketio.ASGIApp(sio, app)
 
manager = sio.manager
#clientsocket = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
#host = '127.0.0.1'
#port =  6000
#clientsocket.connect((host,port))

 
rooms = defaultdict(dict) # 방에 대한 모든 정보를 담음 rooms[room] 에서 키를 뽑아서 sid 리스트 획득
#rooms =  defaultdict(dict) # rooms[roomnname][sid] = name    candidate , ice  
sid_2_rooms=  {}  # sid 를 통한 방 추적  sid_2_rooms[sid] = roomname

 

#==============================get============================================
def get_room_list():  # 저장 된 방 리스트 반환
    return list(rooms.keys())
 
def get_roommember_list(roomname): #저장된 방에 있는  멤버 sid 리스트 반환
    if roomname in get_room_list():
        return list(rooms[roomname].keys())
    else:
        getrooms=rooms[roomname] = []
        return getrooms

def get_room_sid_ice(roomname, sid): #저장된 방에 있는 멤버 sid 에 있는 정보 반환
    if sid in get_roommember_list(roomname):
        return rooms[roomname][sid]
    else:
        return None

def get_room_sid(sid):   # sid를통한 방 추출 
    if sid in sid_2_rooms.keys():
        return sid_2_rooms[sid]
    else:
        return None

#==============================set============================================
def save_rooms_info(roomname , sid , file):
    rooms[roomname][sid] = file

def save_roomuser_sid(roomname , sid): # sid 에 따른 방이름 저장
    sid_2_rooms[sid] = roomname
 

#==============================control=============================================

#delete method
def remove_user_from_room( roomname, sid):
    room_data = rooms.get(roomname)
    if room_data and sid in room_data:
        del room_data[sid]




#==============================socketio property===============================
@app.get('/')
async def index():
    
    return FileResponse('fiddle.html')

@sio.on('connect')
async def coonnected(sid,*args, **kwargs):     
    await sio.emit("fuckshit", get_room_list(),to=sid) # 접속 시 모든 방에 대한 리스트 줌 방 보기  

    
@sio.on('join_room')
def joinroom(sid,*args, **kwargs): #1 인자 : 방이름 , #2인자 자료 
    if args[0] not in get_room_list(): # 없는 방이라면 생성되니 add 이벤트 
        sio.emit('roomadd',args[0]) # roomadd # roomname
    if args[0] in get_room_list(): # 있는 방이라면 방유저들에게 연결 이벤트 처리 
        sio.emit('user-connect', sid, room=args[0]) # 기존 유저들이 sid 를 추가 하기 위한  자들어올때 방이름 받고   방에 없으면 안감
    sio.emit('connected',get_roommember_list(args[0]), to= sid) # 해당 방안에 있는 리스트 모든 클라이언트 리스트  # 함수내부 있으면 방 리스트 리턴 없으면 생성 후 공백배열 리턴 
    rooms[args[0]][sid] = args[1] # 초대장?  추가 (rooms[방이름][sid번호] =  클라이언트 정보 )
    sid_2_rooms[sid] = args[0] # sid  to  room 추가 (sid 를 통한 방이름 추출 ) 
    sio.enter_room(sid=sid ,  room= args[0]) # 방안에 넣기  맨 나중에 한 이유는 리스트를 줄때 본인을 제외하고 주기 위함 
    sio.manager.rooms
     
    
@sio.on('disconnect')
def coonnected(sid,*args, **kwargs):
    sio.emit('user-disconnect',sid,to=sid_2_rooms[sid]) #나간사람 통지 방에 있는 사람들에게
    roomname = sid_2_rooms.get(sid)
    if roomname: 
        sio.leave_room(sid=sid,room=roomname)
        remove_user_from_room(roomname=roomname, sid= sid)
        sid_2_rooms.pop(sid,None)
        if len(rooms[roomname].keys())== 0:
            rooms.pop(roomname,None)
            manager.close_room(room=roomname)
            sio.emit('roomdelete',roomname)
    #if sid  in get_roommember_list(args[0]):
    #    sio.leave_room(sid=sid , room=sid_2_rooms) # 나간사람 연결 강퇴
    # socketio 에서는 연결  끊길시 해당 방 나가게 자동으로 처리 

# rooms 내부 로직은 메모리 상에 올라가 있는데 클라이언트 하나가 접속되어 있는 것도 사실상 하나의 방임
# 그레서 private room 은 sid 크랙 값을 가지고 
# 방이름과 sid 값이 같다면 priaate 이고 
# room id 를 socket id 에서 찾을 수 있다면 private room 
# room id 를 socket id 에서 찾을 수 없다면 public room  
@sio.on('offer')
def offer(sid,*args, **kwargs):
    sio


sio.on('ice')
def ice(sid, *args, **kwargs):
    sio
    
@sio.on('roomchange')
async def roomchanged(sid,*args, **kwargs):
    return "D"
    
     

    
if __name__ == '__main__':

    uvicorn.run(combined_asgi_app, host='127.0.0.1', port=5000)