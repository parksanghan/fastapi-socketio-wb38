
from fastapi import FastAPI ,Cookie, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import socketio
import socket 
import uvicorn
from collections import  defaultdict
import os
import threading 
app : FastAPI = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
 # (admin)
sio : socketio.AsyncServer = socketio.AsyncServer(async_mode='asgi',  
                          credits=True,
                           cors_allowed_origins = [
                            
                           
                           'http://localhost:5000',
                           'https://admin.socket.io',
                           'http://127.0.0.1:5000'  # 추가: Socket.IO 서버의 주소를 명시]
                           
                           ])  

sio.instrument(# auth=True,
               {'username':'WB38' , 'password':os.environ['WB38']}
                     )

 #WB38                           your_password

combined_asgi_app = socketio.ASGIApp(sio, app)

manager = sio.manager
#clientsocket = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
#host = '127.0.0.1'
#port =  6000
#clientsocket.connect((host,port))

rooms : defaultdict[str, dict[str, str]] = defaultdict(dict[str, str]) # 방에 대한 모든 정보를 담음 rooms[room] 에서 키를 뽑아서 sid 리스트 획득
#rooms =  defaultdict(dict) # rooms[roomnname][sid] = name    candidate , ice  

sid_2_rooms : dict[str, str] = {}  # sid로 등록된 방 이름을 받아옴
tutors : list[str] = [] #튜터들의 sid를 List로 저장

file_lock : threading.Lock = threading.Lock()

#==============================get============================================
def get_room_list():  # 저장된 방들의 이름들을 리스트로 반환
    return list(rooms.keys())
 
def get_roommember_list(roomname): #해당 방 안에 있는 sid들을 리스트로 반환
    if not roomname in get_room_list():
        rooms[roomname] = []
    return list(rooms[roomname].keys())

#공사중
def get_room_sid_ice(roomname, sid): #저장된 방에 있는 멤버 sid 에 있는 정보 반환
    if sid in get_roommember_list(roomname):
        return rooms[roomname][sid]
    else:
        return None

def get_roomname_by_sid(sid):   # sid를통한 방 추출 
    return sid_2_rooms[sid]

#==============================set============================================
def save_offer_in_room(roomname , sid , offer):
    rooms[roomname][sid] = offer

#==============================control=============================================

#delete method
def remove_user_from_room(roomname, sid):
    room_data = rooms.get(roomname)
    if not room_data and sid in room_data: # roomname을 가진 room이 존재 and 해당 room에 sid이 존재.
        return 0
    
    del room_data[sid]
 

#==============================socketio property===============================
@app.get('/')
async def index():
    return FileResponse('fiddle.html')

@sio.on('connect')
async def connected(sid,*args, **kwargs):     
    await sio.emit("fuckshit", list(rooms),to=sid) # 접속 시 모든 방에 대한 리스트 줌 방 보기  
    
    
@sio.on('join_room')
def joinroom(sid,*args, **kwargs): #1 인자 : 방이름 , #2인자 자료 
    roomName : str = args[0]

    # 방 있는지 없는지 없으면 생성
    if roomName not in get_room_list(): # 없는 방이라면 생성되니 add 이벤트 
        sio.emit('roomadd',roomName) 
        tutors.append(sid)
    else : # 있는 방이라면 방유저들에게 연결 이벤트 처리 
        sio.emit('user-connect', sid, room=roomName) # 기존 유저들이 sid 를 추가 하기 위한  자들어올때 방이름 받고   방에 없으면 안감
    
    #후처리
    sio.emit('connected',get_roommember_list(roomName), to = sid) # 해당 방안에 있는 리스트 모든 클라이언트 리스트  # 함수내부 있으면 방 리스트 리턴 없으면 생성 후 공백배열 리턴 
    rooms[roomName][sid] = None # 초대장?  추가 (rooms[방이름][sid번호] =  클라이언트 정보 )
    sid_2_rooms[sid] = roomName # sid  to  room 추가 (sid 를 통한 방이름 추출 ) 
    sio.enter_room(sid=sid ,  room= roomName) # 방안에 넣기  맨 나중에 한 이유는 리스트를 줄때 본인을 제외하고 주기 위함 
     
    
@sio.on('disconnect')
def disconnected(sid,*args, **kwargs) :
    # 방안에 있는 확인해본다.
    isInRoom : bool = sid_2_rooms.get(sid) is not None
    roomname = sid_2_rooms.get(sid)

    # 방안에 있었다면 브로드 캐스트
    if isInRoom: 
        #나간 사람 통지 방에 있는 사람들에게
        sio.emit('user-disconnect', sid, to=roomname) 
        
        #sid를 roomname에서 내보냄
        sio.leave_room(sid, roomname)
        remove_user_from_room(roomname=roomname, sid= sid)
        sid_2_rooms.pop(sid,None)

        if len(rooms[roomname].keys())== 0:
            rooms.pop(roomname,None)
            manager.close_room(room=roomname)
            sio.emit('roomremove',roomname)

    # 없어도 해준데요~
    rooms[roomname].pop(sid,None)
    sid_2_rooms.pop(sid,None)
    #sid_2_tutor.pop(sid,None)
           
    #if sid  in get_roommember_list(args[0]):
    #    sio.leave_room(sid=sid , room=sid_2_rooms) # 나간사람 연결 강퇴
    # socketio 에서는 연결  끊길시 해당 방 나가게 자동으로 처리 

# rooms 내부 로직은 메모리 상에 올라가 있는데 클라이언트 하나가 접속되어 있는 것도 사실상 하나의 방임
# 그레서 private room 은 sid 크랙 값을 가지고 
# 방이름과 sid 값이 같다면 priaate 이고 
# room id 를 socket id 에서 찾을 수 있다면 private room 
# room id 를 socket id 에서 찾을 수 없다면 public room  
 

# peer to peer 과정 
# send offer   - > send answer 
# candidate   -> candidate 
#offer 는 서버가 필요한 이유는 offer를 주고 받기 위함
@sio.on('offer')
def offer(sid,*args, **kwargs):
    offer  = args[0]  # 클라이언트에서 받아온  offer
    roomname   = args[1]  # 방이름  
    data  = args[2]
    rooms[roomname][sid]
    if sid in tutors: # 튜터인 경우  
        with file_lock:
            with open(f'{sid}.wav', 'ab') as f: #서버에서 저장할 폴더에 이제 sid 이름으로 이게 첫 유저면 저장 
                f.write(data)
                
    #save_rooms_info[roomname][sid] = offer #  sid 에 따른 offer 할당 바인딩 필요시사용
    sio.emit('offer',offer,room=roomname) #해당 방에 있는 사람들에게  필요하다면 offerlist로 주기 
    

# 클라이언트 측 :
# 자신의 offer 생성
#   const offer = await myPeerConnection.createOffer();
#   // 로컬에 offer 설정
#   myPeerConnection.setLocalDescription(offer);
#   console.log("sent the offer");
#   // 상대방에게 offer 전송
#   socket.emit("offer", offer, roomName);
    
#   그걸 서버가 받고 방에 offer 전송 

#  클라에서도 또 socket.on('offer') 이벤트 받고 peer to peer 연결 처리 


@sio.on('answer')
def answer(sid,*args, **kwargs):
    answer= args[0]
    roomname = args[1]
    sio.emit('answer',answer,room= roomname)

sio.on('ice')
def ice(sid, *args, **kwargs):
    ice  = args[0]
    roomname = args[1]
    sio.emit('ice',ice,room=roomname)
    
@sio.on('roomchange') # 필요하다면 구현 
async def roomchanged(sid,*args, **kwargs):
    return "D"


if __name__ == '__main__':
    uvicorn.run(combined_asgi_app, host='127.0.0.1', port=5000)