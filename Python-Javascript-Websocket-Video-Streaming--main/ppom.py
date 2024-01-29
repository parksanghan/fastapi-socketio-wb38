
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
import dddd3
import ssl
 
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

sio.instrument(
               {'username':'WB38' , 'password':os.environ['WB38']}
                     )
 

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# ssl_context.load_cert_chain('/path/to/cert.pem', keyfile='/path/to/key.pem')
combined_asgi_app = socketio.ASGIApp(sio, app)
manager = sio.manager
#clientsocket = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
#host = '127.0.0.1'
#port =  6000
#clientsocket.connect((host,port))

 
rooms = defaultdict(dict) # 방에 대한 모든 정보를 담음 rooms[room] 에서 키를 뽑아서 sid 리스트 획득
#rooms =  defaultdict(dict) # rooms[roomnname][sid] = name    candidate , ice  
sid_2_rooms=  {}  # sid 를 통한 방 추적  sid_2_rooms[sid] = roomname
sid_2_tutor = []
             
file_lock = threading.Lock()

#==============================get============================================
def get_room_list():  # 저장 된 방 리스트 반환
    return list(rooms.keys())
 
def get_roommember_list(roomname): #저장된 방에 있는  멤버 sid 리스트 반환
    if roomname in get_room_list():
        return list(rooms[roomname].keys())
    else:
        getrooms=rooms[roomname] = []
        return getrooms

def get_room_sid_offer(roomname, sid): #저장된 방에 있는 멤버 sid 에 있는 정보 반환
    if sid in get_roommember_list(roomname):
        return rooms[roomname][sid]
    else:
        return None

def get_room_sid(sid):   # sid를통한 방 추출 
    if sid in sid_2_rooms.keys():
        return sid_2_rooms[sid]
    else:
        return None
 
def get_all_offers(roomname): # sid 는 offer 와 매핑 되어 있음 room[roomname][sid] = offfer 
    if len([inner_dict.values() for inner_dict in rooms.get(roomname)]):
        all_values = [value for inner_dict in rooms.values() for value in inner_dict.values()]  # 수정된 부분
        return all_values
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
    
    return FileResponse('codecfile.html')
 
@sio.on('connect')
async def coonnected(sid,*args, **kwargs):     
 
    await sio.emit("connected", get_room_list(),to=sid) # 접속 시 모든 방에 대한 리스트 줌 방 보기  

  # 같을파일에 대해서 접근시 lock 걸고 다른 파일에 대해서는 새로운 쓰레드를 통해 제어 
# @sio.on('voice')
# async def handle_voice(sid,data): # blob 으로 들어온 데이터 
#    await control_voice(sid,data) 
#    #asyncio.run(control_voice(sid,data)) #정상 수행

# async def control_voice(sid,data):
#     try:
#      # BytesIO를 사용하여 메모리 상에서 오디오 데이터를 로드
#         audio_segment:AudioSegment = AudioSegment.from_file(io.BytesIO(data), format="webm")
#     #audio_segment = AudioSegment.from_file()
#     # 오디오 파일로 저장
#         directory = str("dddd")
#         if not os.path.exists(directory):
#             os.makedirs(directory)
#         file_path = os.path.join(directory, f'{sid}.wav')
#         file_chunk_path = os.path.join(directory, f'{sid}chunk.wav')
#     # 오디오 파일로 저장
#     # 아래의 파일저장부분 
#         if not os.path.exists(file_path): # 처음 보낸 chunk 의 경우 
#             async with await get_file_lock(file_path=file_path): # 파일을 통한 딕셔너리로 lock 형태 지정
#                 audio_segment.export(file_path, format='wav')
#                 #await write_wav_func(file_path,audio_segment) # lock은 코드블럭을 나가면 해제 

#         else:                             # 처음 이외에 보내는 chunk의 경우 .wav 파일에 대한 합성 
#         #audio_segment.export(file_chunk_path,format='wav')
#             async with await get_file_lock(file_path=file_chunk_path):
#                 audio_segment.export(file_path, format='wav')
#                 # 파일 쓰기가 완료 된 뒤에 파일 합치기
#                 handle_audio_chunk(directory,filepath=file_path,chukpath=file_chunk_path)
#         print('오디오{sid} 파일 저장 완료')
#     except Exception as esl:
#         print(esl,sid,"파일 처리 중 에러 발생")
        
        
# # 아래함수를 쓰레드 함수로 만들가 
# async def handle_audio_chunk(directory,filepath,chukpath):
    
#     infiles = [filepath,
#                 chukpath]
#     outfile =  os.path.join(directory, "reuslt_"+filepath) 


#     data= []
#     for infile in infiles:
#         w = wave.open(os.getcwd()+'\\'+infile, 'rb')
#         data.append([w.getparams(), w.readframes(w.getnframes())])
#         w.close()
    
#     output = wave.open(outfile, 'wb')

#     output.setparams(data[0][0])

#     for i in range(len(data)):
#         output.writeframes(data[i][1])
#     output.close()

# async def get_file_lock(file_path):
#     if file_path not in lock_threading:        
#         lock_threading[file_path] = asyncio.Lock()
#     return lock_threading[file_path]

# async def write_wav_func(file_path, audio_segment:AudioSegment):
   
#     task= asyncio.create_task(write_file(file_path, ad=audio_segment))
    
#     # 작업이 완료되면 콜백 호출
#     task.add_done_callback(lambda fut: file_write_callback(fut))

# async def write_file(file_path, ad:AudioSegment):

#     async with aiofiles.open(file_path, 'wb') as file:
#         await file.write(ad.raw_data)

# def file_write_callback(future):
#     # 파일 쓰기 작업이 완료되면 실행되는 콜백 함수
#     if future.exception() is not None:
#         print(f"파일 쓰기 중 에러 발생: {future.exception()}")
#     else:
#         print("파일 쓰기 완료")

lock_threading = {}
async def get_file_lock(file_path):
    if file_path not in lock_threading:        
        lock_threading[file_path] = asyncio.Lock()
    return lock_threading[file_path]


@sio.on('voice')
async def voice_received(sid,data):
    task = asyncio.create_task(handle_voice(sid,data))
async def handle_voice(sid,data): # blob 으로 들어온 데이터 
    # BytesIO를 사용하여 메모리 상에서 오디오 데이터를 로드
  
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
       async with await get_file_lock(file_path=file_path): #
        loop =  asyncio.get_event_loop()
        audio_segment:AudioSegment =await loop.run_in_executor
        (None, AudioSegment.from_file, io.BytesIO(data), "webm")
        loop.run_in_executor(None,audio_segment.export,file_path,format='wav')
        #audio_segment:AudioSegment =
        #  AudioSegment.from_file(io.BytesIO(data), format="webm")
        #audio_segment.export(file_path,format='wav')
       #await write_file(file_path=file_path, audio_segment=audio_segment)
    else:                             # 처음 이외에 보내는 chunk의 경우 .wav 파일에 대한 합성
        async with await get_file_lock(file_path=file_path):
            loop =  asyncio.get_event_loop()
            audio_segment:AudioSegment =await loop.run_in_executor
            (None, AudioSegment.from_file, io.BytesIO(data), "webm")
            #audio_segment:AudioSegment = 
            #AudioSegment.from_file(io.BytesIO(data), format="webm")
            #audio_segment.export(file_path,format='wav')
            loop.run_in_executor(None,audio_segment.export,file_chunk_path,format='wav') 
            loop.run_in_executor(None,handle_audio_chunk,file_path,file_chunk_path)  
    print('오디오 파일 저장 완료')
# 아래함수를 쓰레드 함수로 만들가 async
def handle_audio_chunk(filepath,chukpath):
    
    infiles = [ filepath,
                chukpath]
    outfile = os.path.join(filepath) 
    data= []
    for infile in infiles:

        w = wave.open(os.getcwd()+'/'+infile, 'rb') #  동기 
        data.append([w.getparams(), w.readframes(w.getnframes())])
        w.close()
    output = wave.open(outfile, 'wb')#동기 
    output.setparams(data[0][0])
    for i in range(len(data)):
        output.writeframes(data[i][1])
    output.close()

# async def write_  file(file_path,audio_segment:AudioSegment):
#     async with aiofiles.open(file_path,'wb')as file:
#         await file.write(audio_segment.raw_data)


# @sio.on('voice')
# async def handle_voice(sid,data): # blob 으로 들어온 데이터 
#     # BytesIO를 사용하여 메모리 상에서 오디오 데이터를 로드
#     audio_segment:AudioSegment = AudioSegment.from_file(io.BytesIO(data), format="webm")
#     #audio_segment = AudioSegment.from_file()
#     # 오디오 파일로 저장
#     directory = str("dddd")
#     if not os.path.exists(directory):
#         os.makedirs(directory)
#     file_path = os.path.join(directory, f'{sid}.wav')
#     file_chunk_path = os.path.join(directory,f'{sid}chunk.wav')
#     # 오디오 파일로 저장
#     # 아래의 파일저장부분 
#     if not os.path.exists(file_path): # 처음 보낸 chunk 의 경우 
#         audio_segment.export(file_path, format='wav')
#     else:                             # 처음 이외에 보내는 chunk의 경우 .wav 파일에 대한 합성 
#         audio_segment.export(file_chunk_path,format='wav')
#         await handle_audio_chunk(directory,file_path,file_chunk_path)
    
# #아래함수를 쓰레드 함수로 만들가 
# async def handle_audio_chunk(directory,filepath,chukpath):
    
#     infiles = ['\\' + filepath,
#                 '\\'+chukpath]
#     outfile = ['\\'+filepath]


#     data= []
#     for infile in infiles:
#         w = wave.open(os.getcwd()+'/'+infile, 'rb')
#         data.append([w.getparams(), w.readframes(w.getnframes())])
#         w.close()
    
#     output = wave.open(outfile, 'wb')

#     output.setparams(data[0][0])

#     for i in range(len(data)):
#         output.writeframes(data[i][1])
#     output.close()
 
 
@sio.on('join_room')
def joinroom(sid,*args, **kwargs): #1 인자 : 방이름 , #2인자 자료 없음
    if args[0] not in get_room_list(): # 없는 방이라면 생성되니 add 이벤트 
        sio.emit('roomadd',args[0])  #  모든 유저들에게 "방"이 추가되었음을 통지  
        sid_2_tutor.append(sid)
        sio.emit('istutor',to=sid) # 첫유저일때 해당 sid 에게 튜터임을 이벤트 전송
    if args[0] in get_room_list(): # 있는 방이라면 방유저들에게 연결 이벤트 처리 
        sio.emit('user_connect', sid, room=args[0]) # 기존 유저들이 sid 를 추가           하기 위한  자들어올때 방이름 받고   방에 없으면 안감
        
    sio.emit('roomconnected',get_roommember_list(args[0]), to= sid) # 해당 방안에 있는 리스트 모든 클라이언트 리스트  # 함수내부 있으면 방 리스트 리턴 없으면 생성 후 공백배열 리턴 
    rooms[args[0]][sid] = None # 초대장?  추가 (rooms[방이름][sid번호] =  클라이언트 정보 )
    sid_2_rooms[sid] = args[0] # sid  to  room 추가 (sid 를 통한 방이름 추출 ) 
    sio.enter_room(sid=sid ,  room= args[0]) # 방안에 넣기  맨 나중에 한 이유는 리스트를 줄때 본인을 제외하고 주기 위함 
  
     
    
@sio.on('disconnect')
def disconnected(sid,*args, **kwargs):
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
    if sid in sid_2_tutor: 
        sid_2_tutor.remove(sid) # 교수가 나갓을때 ai 서버와 통신하여 트레이닝 시작
        # 리스트는 팝이안됨 
    
""" disconnect 로직 구성        
    if sid  in get_roommember_list(args[0]):
       sio.leave_room(sid=sid , room=sid_2_rooms) # 나간사람 연결 강퇴
    socketio 에서는 연결  끊길시 해당 방 나가게 자동으로 처리 

rooms 내부 로직은 메모리 상에 올라가 있는데 클라이언트 하나가 접속되어 있는 것도 사실상 하나의 방임
그레서 private room 은 sid 크랙 값을 가지고 
방이름과 sid 값이 같다면 priaate 이고 
room id 를 socket id 에서 찾을 수 있다면 private room 
room id 를 socket id 에서 찾을 수 없다면 public room  
"""

""" WebRTC 구동 방식
peer to peer 과정 
send offer   - > send answer 
candidate   -> candidate    
"""

# 서버가 offer 이벤트를 받는 시점 : 클라이언트 측에서 roomjoin에서 신규 사용자를 추가시킬때 
# 클라에서는 room-join 이벤트를 받는데이때 방에 들어가면서 자신의 offer 를 전달함 
@sio.on('offer')    
async def offer(sid,*args, **kwargs):
    offer  = args[0]  # 클라이언트에서 받아온  offer
    roomname   = sid_2_rooms.get(sid)  # 방이름 
    sio.emit('offer',get_all_offers(roomname), to=sid) 
    # offer를 발생시킨 sid 에게 현재 저장되어 있는 offer 리스트 반환 
    # get_roommember_list 반환추가 -> get_all_offers 와 get_roommember_list 해당 함수들이 인덱스값을 공유하므로 
    # offer 할당 시 콜백으로 해당 객체의 주인인 sid를 보내 icecandidate 를 보내기 위함
    save_rooms_info(roomname,sid,offer)# 자신을 제외하고 전달하기 위해 이벤트 후 저장
    sio.emit('offeradd',offer, sid,room=roomname,skip_sid=sid) # 현재 접속된 방에서의 사람들은 해당 offer 만 받고 리스트에 추가
    # sid 추가 -> offer 와 그 정보를 주인인 sid 도 보냄
    #근데 이미 방에는 들어 있어서 sid 제외 해줘야 함
 
""" 클라이언트에서의 offer 처리 
 클라이언트 측 :
 자신의 offer 생성  이거는 방들어갈때 자신의 걸 가져옴
   const offer = await myPeerConnection.createOffer();
   // 로컬에 offer 설정
   myPeerConnection.setLocalDescription(offer);
   console.log("sent the offer");
   // 상대방에게 offer 전송
   socket.emit("offer", offer, roomName);
   
   그걸 서버가 받고 방에 offer 전송 
  클라에서도 또 socket.on('offer') 이벤트 받고 peer to peer 연결 처리 
 클라에서의 socketio.on('offer') =>
 {mypeerconnection.setRemoteDescription(offer)} 
 클라이언트측은
    offer 이벤트 받을시 리스트에 할당  mypeerconnections = []
    offeradd 이벤트 받을 시 저장된 리스트에 추가 후 프레임로드 

"""
""" 클라이언트에서의 offer 이벤트 처리 로직 구성 예시

socket.on("welcome", async () => {
  const offer = await myPeerConnection.createOffer();
  myPeerConnection.setLocalDescription(offer);
  console.log("sent the offer");
  socket.emit("offer", offer, roomName);
});

peerConnectionlist = []
peer_sid_list = []
socket.on("offer", async (offerlist,member_sid_list) => {
    peer_sid_list  = member_sid_list
  for (const offer of offerlist AND const memsid of member_sid_list) {
    const peerConnection = new RTCPeerConnection(configuration);
    peerconnection.eventlistener('icecandidate', icecallback(memsid) )
    peerConnectionlist.push(peerConnection);
    await peerConnection.setRemoteDescription(offer); 
    #해당 함수 호출후 icecandidate 이벤트 발생 
    그래서 인덱스 구하고 그 인덱스에 있는 sid 에게 보내는것도 가능하고 이 
    for문내부에서 하나씩할당하기에 괜찮을듯? 
    
  }
});

socket.on("offeradd", async (offer,sid) => {
  const peerConnection = new RTCPeerConnection(configuration);
  peerConnection.listener('icecandidate',icecllaback(sid) )
  peerConnectionlist.push(peerConnection);  // 리스트에 Peer Connection 추가
  peerConnection.setRemoteDescription(offer);
   
});

 

"""


""" icecandidate 
offer 를 모두 가지고 그걸 받는 걸 모두 끝냈을 때 
peer to peer 연결의 양쪽에서 icecandidate 라는 이벤트를 실행 
-> 사실상 add
그 icecandidate 정보를 서로 주고 받아야함 근데 어떻게 특정해 시발
그건 그렇다쳐 
이제 발생되었을때 보내면 상대는 addicecandidate 를 하고 다시 자신의 걸 보냄
그 러고 보낸 클라에게 다시 자신의 ice를 보내 그 클라는 addicecandidate 를 하고
이제 서로의 ice 를 알고 있을때 addIceStream 이벤트가 발생 
"""
sio.on('ice')  # offer를 받고 해당 offer를 
def ice(sid, *args, **kwargs):
    ice  = args[0]
    targetsid = args[1]
    roomname=sid_2_rooms.get(targetsid)
    if targetsid in get_roommember_list(roomname):
         sio.emit('ice',ice,sid,to=targetsid)

""" ice를 처리하기 위한 socket.on("offer") 이벤트 처리 클라이언트 구현 방식 offerlist , getmemberlist 형식 
  peerconnectionlist =  []
  function makeaddconnection(sid) #=> offeradd 즉 , offer 주는 클라이언트 추가시 마다 반복 
 {
    const peerconnection   = new RTCPeerConnection(configure);
    peerConnectionlist.push(peerconnection);
    myPeerConnection.addEventListener("icecandidate", handleIce(sid));
    myPeerConnection.addEventListener("addstream", handleAddStream);# 상대 peer 에게서 스트림 트랙을받았을때 발생
    # -> 상대가 아래의 코드를실행해줘야 addstream 이벤트가 발생함  
     myStream
    .getTracks()
    .forEach((track) => myPeerConnection.addTrack(track, myStream)); # 자신의 스트림 트랙을 이 connection 상대에게 전송함
     return peerconnection
 }
  socket.on("offer",(offerlist, memberlist)=>{
    for(let i = 0; i< Math.min(offerlist.length,memberlist.length); i++){
    const offer = offerlist[i];
    const sid = memberlist[i];
    peerconnection = await makeaddconnection(sid) # 참조임
    peerconnection.setRemoteDescrition(offer) # 이벤트 발생 
    }
  })

  function handleice(sid){
    #=> setRemoteDescrtion 에 의해 icecandidate 이벤트가 발생 
    icecandidate=data.candidate
    socket.emit('ice',icecanddiate, sid) # 해당 sid 는 객체의 주인인 sid 소켓 번호임 
 }
    fuctnion handleAddStream(){
    => 상대가 나에게 본인의 스트림 트랙을 addtrack 해주었을때 발생되는 이벤트 
    const streamBox = document.createElement("div");
    streamBox.className = "streamBox";

    // 스트림 적용
    const peerFace = document.createElement("video");
    peerFace.srcObject = data.stream;
 

    // 네모칸에 스트림 추가
    streamBox.appendChild(peerFace);
    streamContainer.appendChild(streamBox);
 } 


"""
""" ice를 처리하기 위한 socket.on("offeradd")이벤트 처리 클라이언트 구현 방식 
 클라이언트에서 offeradd 시 
 peerconnectionlist =  []
  function makeaddconnection(sid) #=> offeradd 즉 , offer 주는 클라이언트 추가시 마다 반복 
 {
    const peerconnection   = new RTCPeerConnection(configure);
    peerConnectionlist.push(peerconnection);
     myPeerConnection.addEventListener("icecandidate", handleIce(sid));
    myPeerConnection.addEventListener("addstream", handleAddStream);# 상대 peer 에게서 스트림 트랙을받았을때 발생
    # -> 상대가 아래의 코드를실행해줘야 addstream 이벤트가 발생함  
     myStream
    .getTracks()
    .forEach((track) => myPeerConnection.addTrack(track, myStream)); # 자신의 스트림 트랙을 이 connection 상대에게 전송함
    return peerconnection
 }
 socket.on('offeradd',async (offer,sid)=>
 {
    peerconnection = await makeaddconnection(sid);  
    peerconnection.setRemoteDescrition(offer); #이때 icecanddiate 이벤트가 발생함   
 })

 function handleice(sid){
    #=> setRemoteDescrtion 에 의해 icecandidate 이벤트가 발생 
    icecandidate=data.candidate
    socket.emit('ice',icecanddiate, sid) # 해당 sid 는 객체의 주인인 sid 소켓 번호임 
 }
    fuctnion handleAddStream(){
    => 상대가 나에게 본인의 스트림 트랙을 addtrack 해주었을때 발생되는 이벤트 
    const streamBox = document.createElement("div");
    streamBox.className = "streamBox";

    // 스트림 적용
    const peerFace = document.createElement("video");
    peerFace.srcObject = data.stream;
 

    // 네모칸에 스트림 추가
    streamBox.appendChild(peerFace);
    streamContainer.appendChild(streamBox);
 } 

"""

sio.on('iceanswer')# ice 이벤트로만으로도 처리가 잘되면 필요없음 
def icecallback(sid ,*args, **kwargs):
    ice = args[0]
    targetsid  = args[1]
    roomname=sid_2_rooms.get(targetsid)
    if targetsid in get_roommember_list(roomname):
        sio.emit('iceanswer',ice,sid,to=targetsid)
""" icecandidate 데이터를 받았을때 
 


"""   
    
# @sio.on('roomchange') # 필요하다면 구현 
# async def roomchanged(sid,*args, **kwargs):
# return "D"
    
     
@sio.on('sendtext')
async def sendwav(sid,*args, **kwargs):# 10초마다 음성파일 줘
    text = args[0]
    roomanedir  = sid_2_rooms(sid)
    filename = sid
    if sid in sid_2_tutor: # 튜터인 경우  
        with file_lock:
            directory_path = os.path.join(os.getcwd(), roomanedir)
            os.makedirs(directory_path, exist_ok=True)
            file_path = os.path.join(directory_path, f"{filename}.txt")
            with open(file_path, 'ab') as f: #서버에서 저장할 폴더에 이제 sid 이름으로 이게 첫 유저면 저장 
               await f.write(text)
    
if __name__ == '__main__':

    uvicorn.run(combined_asgi_app, host='127.0.0.1', port=5000  #, ssl= ssl_context
              )