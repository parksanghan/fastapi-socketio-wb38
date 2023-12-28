
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
app.mount('/static', StaticFiles(directory='kamos_static'), name='kamos_static')

# 비동기 서버 생성
sio : socketio.AsyncServer = socketio.AsyncServer(async_mode='asgi',  
                          credits=True,
                           cors_allowed_origins = [
                            
                           
                           'http://localhost:5000',
                           'https://admin.socket.io',
                           'http://127.0.0.1:5000'  # 추가: Socket.IO 서버의 주소를 명시]
                           
                           ])  

#관리자 모드 인증 설정
# sio.instrument(auth=False) # 권한 없이 접속하기
sio.instrument({'username':'WB38' , 'password':os.environ['WB38']})

#socketIO와 FastAPI를 합치기
combined_asgi_app = socketio.ASGIApp(sio, app)

#매니저 가져오기
manager = sio.manager

# 방, 참여자, 참여자 정보를 2중 딕셔너리로 저장
rooms : defaultdict[str, dict[str, str]] = defaultdict(dict[str, str]) 
# rooms[roomnname][sid] = offer
# roomnname : 방이름 (사용자지정 문자열)
# sid : 소켓 id (해쉬값 문자열)
# offer : 소켓 정보?

# sid값으로 해당 소켓이 참여중인 방의 이름을 바로 알 수 있게 저장
sid_2_rooms : dict[str, str] = {}  
# 강의자는 별도로 저장해두기 
tutors : list[str] = []

# 공유자원 처리하려고 만든거라는데 필요 없다나? 신경 ㄴㄴ
file_lock : threading.Lock = threading.Lock()

#==============================get============================================
def get_room_list():  # X > 리스트(모든 방의 이름)
    return list(rooms.keys())
 
def get_roommember_list(roomname): # 방 이름 > 리스트(그 방의 모든 참여자 ID)
    if not roomname in get_room_list():
        rooms[roomname] = []
    return list(rooms[roomname].keys())

#공사중
def get_room_sid_ice(roomname, sid): #저장된 방에 있는 멤버 sid 에 있는 정보 반환
    if sid in get_roommember_list(roomname):
        return rooms[roomname][sid]
    else:
        return None

def get_roomname_by_sid(sid):   # 참여자 ID > 참여중인 방 이름 
    return sid_2_rooms[sid]

#==============================set============================================
def save_offer_in_room(sid , offer): # 참여자 아이디에 해당하는 참여자 정보 저장
    rooms[sid_2_rooms[sid]][sid] = offer

#==============================control=============================================

#delete method
def remove_user_from_room(roomname, sid): # 방이름으로 방 안의 참여자 제거.
    room = rooms.get(roomname)
    if room is None: # roomname을 가진 room이 존재 and 해당 room에 sid이 존재.
        return False
    if not sid in room :
        return False
    
    del room[sid]
    return True
 

#==============================socketio property===============================
@app.get('/')
async def index():
    return FileResponse('kamos.html')

@sio.on('connect')
async def connected(sid,*args, **kwargs):     
    await sio.emit("fuckshit", list(rooms),to=sid) # 접속 시 모든 방에 대한 리스트 줌 방 보기  
    
    
@sio.on('join_room')
def joinroom(sid,*args, **kwargs): #1 인자 : 방이름 
    # 방이름 받아옴
    roomName : str = args[0]

    # 방 있는지 없는지 없으면 생성
    if roomName not in get_room_list(): # 없는 방이라면 생성되니 add 이벤트 
        sio.emit('roomadd',roomName) 
        tutors.append(sid)
    else : # 있는 방이라면 방유저들에게 연결 이벤트 처리 
        sio.emit('user-connect', sid, room=roomName) # 기존 유저들이 sid 를 추가 하기 위한  자들어올때 방이름 받고   방에 없으면 안감
    
    # [후처리]
    # 해당 방안에 있는 리스트 모든 클라이언트 리스트 
    # 함수내부 있으면 방 리스트 리턴 없으면 생성 후 공백배열 리턴 
    sio.emit('connected', get_roommember_list(roomName), to = sid) 
    # 초대장?  추가 (rooms[방이름][sid번호] =  클라이언트 정보 )
    rooms[roomName][sid] = None 
    # sid  to  room 추가 (sid 를 통한 방이름 추출 ) 
    sid_2_rooms[sid] = roomName 
    # 방안에 넣기  맨 나중에 한 이유는 리스트를 줄때 본인을 제외하고 주기 위함 
    sio.enter_room(sid=sid ,  room= roomName) 
     
    
@sio.on('disconnect')
def disconnected(sid,*args, **kwargs) :
    # 방안에 있는지 확인해본다.
    isInRoom : bool = sid_2_rooms.get(sid) is not None
    roomname = sid_2_rooms.get(sid)

    # 방안에 있었다면
    if isInRoom: 
        #방에 남은 사람들에게 해당 유저의 퇴장을 통지
        sio.emit('user-disconnect', sid, to=roomname) 
        
        #sid를 roomname에서 내보냄
        sio.leave_room(sid, roomname)
        remove_user_from_room(roomname=roomname, sid= sid)
        sid_2_rooms.pop(sid,None)

        if len(rooms[roomname].keys())== 0:
            rooms.pop(roomname,None)
            manager.close_room(room=roomname)
            sio.emit('roomremove',roomname)

    # roomname이 없어도 해준데요~
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
    
