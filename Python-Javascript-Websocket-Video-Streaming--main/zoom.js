'use strict';
 // 해당 버전은 peerlist가 리스트인 버전입니다. 
(function() {
  let myStrdeam;
  const socket = io('http://127.0.0.1:5000'); // 이거 주소 지워야할수도 
  const myFace = document.getElementById("myFace");
  const muteBtn = document.getElementById("mute");
  const cameraBtn = document.getElementById("camera");
  const camerasSelect = document.getElementById("cameras");
  const call = document.getElementById("call");

  call.hidden = true;

let myStream;;
let muted = false;
let cameraOff = false;
let myPeerConnection;
var PC_CONFIG = {
  iceServers: [
      {
          urls: ['stun:stun.l.google.com:19302', 
                  'stun:stun1.l.google.com:19302',
                  'stun:stun2.l.google.com:19302',
                  'stun:stun3.l.google.com:19302',
                  'stun:stun4.l.google.com:19302'
              ]
      },
  ]
};

async function getCameras() {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const cameras = devices.filter((device) => device.kind === "videoinput");
      const currentCamera = myStream.getVideoTracks()[0];
      cameras.forEach((camera) => {
        const option = document.createElement("option");
        option.value = camera.deviceId;
        option.innerText = camera.label;
        if (currentCamera.label === camera.label) {
          option.selected = true;
        }
        camerasSelect.appendChild(option);
      });
    } catch (e) {
      console.log(e);
    }
  }                         
  async function getMedia(deviceId) {
    const initialConstrains = {
      audio: true,
      video: { facingMode: "user" },
    };
    const cameraConstraints = {
      audio: true, 
      video: { deviceId: { exact: deviceId } },
    };
    try {
      myStream = await navigator.mediaDevices.getUserMedia(
        deviceId ? cameraConstraints : initialConstrains
      );
      myFace.srcObject = myStream;
      if (!deviceId) {
        await getCameras();
      }
    } catch (e) {
      console.log(e);
    }
  }
   

  function handleMuteClick() {
    myStream
      .getAudioTracks()
      .forEach((track) => (track.enabled = !track.enabled));
    if (!muted) {
      muteBtn.innerText = "Unmute";
      muted = true;
    } else {
      muteBtn.innerText = "Mute";
      muted = false;
    }
  }

  function handleCameraClick() {
    myStream
      .getVideoTracks()
      .forEach((track) => (track.enabled = !track.enabled));
    if (cameraOff) {
      cameraBtn.innerText = "Turn Camera Off";
      cameraOff = false;
    } else {
      cameraBtn.innerText = "Turn Camera On";
      cameraOff = true;
    }
  }
  async function handleCameraChange() {
    await getMedia(camerasSelect.value);
    if (myPeerConnection) {
      const videoTrack = myStream.getVideoTracks()[0];
      const videoSender = myPeerConnection
        .getSenders()
        .find((sender) => sender.track.kind === "video");
      videoSender.replaceTrack(videoTrack);
    }
  }
  muteBtn.addEventListener("click", handleMuteClick);
  cameraBtn.addEventListener("click", handleCameraClick);
  camerasSelect.addEventListener("input", handleCameraChange);


  // socket.emit join room은 버튼핸들러로 하는거임 
  // 아래부터는 emit 에 대한 이벤트 동작은 joinroom 이후 임 
 
 let memberlist =[] 
 let offerlist=[];
 let is_tutor = false;
 let peerlistconnections = [];
 let roomList  = document.getElementById('roomlist');
 
  //#region  connect 후처리 
  socket.on('connected', async(data)=> { // 연결되었을때 방 리스트 받음
    console.log(`connected ${socket.id}`);
     
    roomList.innerHTML = ''; // 기존 내용 초기화

    for (var i = 0; i < data.length; i++) {
        var option = document.createElement('option');
        option.value = data[i];
        option.text = data[i];
        roomList.add(option);
    }
     
  });
  //#endregion
  //#region  join room 이벤트 후처리 이벤트
  //완료  
  socket.on('roomadd',(roomname)=>{ // 방추가 알림 
    console.log('roomadd');
    var option = document.createElement('option');
        option.value = roomname;
        option.text = roomname;
        roomList.add(option);
  });
  // 완료
  socket.on('istutor',()=>{
    console.log('you are tutor');
    is_tutor = true; 
  });
  is_tutor.addEventListener('change',tutorWavhandler); // 값이 바뀌면 true 임 즉 tutor 이므로
  // 이벤트 발생시 함수로 다른쓰레드로 setinterval로 10초마다 서버로 업데이트
  function tutorWavhandler(){ // 추가작업 나중에 필요 
  // internal  을통한 10초마다 버퍼를 통한 음성 스트리밍을 전달 

  }
  // 완료 
  socket.on('roomconnected',async(sidlist)=>{
    console.log('roomconnected');
    memberlist  = sidlist;
    const myoffer  = await myPeerConnection.createOffer();// 자신의 offer 생성
    myPeerConnection.setLocalDescription(myoffer); // 이건 자신의 offer를 만들어서 전달
    console.log(`send my offer to server`);
    socket.emit(' offer',myoffer);
  })
  //완료 
  socket.on('user_connect',(sid)=>{
    console.log(`user_connected_room  ${sid}`);
    memberlist.push(sid);
  });
  //#endregion
  //#region  disconnect 후처리 
  //완료 
  socket.on('disconnect',  () => {
    console.log(`disconnect ${socket.id}`);
    console.log('server disconnected')
  });
  // 완료
  socket.on('user-disconnect',  (sid) => {
    console.log(`user-disconnect ${socket.id}`);
    removeSidFromMemberList(sid);
  });
  //완료
  function removeSidFromMemberList(sid) {
    memberlist = memberlist.filter((value) => value !== sid);
  }
  //완료
  socket.on('roomremove',(nameroom)=>
  {
    console.log('roomdeleted');
    removeOptionByRoomName(nameroom); 
  });
  // 완료 
  function removeOptionByRoomName(valueToRemove) {
    var options = roomList.options;
    // 원본데이터 삭제후 html 띄워진것도 삭제 
    for (var i = 0; i < options.length; i++) {
        if (options[i].value === valueToRemove) {
            options[i].remove();
            break;
        }
    }
}
 
  //#endregions
  //#region offer 송수신 부분
// 문제야기 
// socketio 가 너무빨라서 모시깽이해서 전역으로 둔거로 아는데
// 리스트를 쓰면서 게속 전역데이터를 가져오는데 
// 전역에서 이미 push 된 데이터를 참조해서 가져와서 변형하기에 이상하게 될거같은데
// 완료 
async function makeaddconnection(sid) 
//#=> offeradd 즉 , offer 주는 클라이언트 추가시 마다 반복 
{
  const peerconnection   = new RTCPeerConnection(PC_CONFIG);
    
   peerConnectionlist.push(peerconnection);
   peerconnection.addEventListener("icecandidate", (data)=>
   {
    handleice(data, sid);
  });
   // 등록된 sid 값으로 이벤트 발동됨 
   peerconnection.addEventListener("track", handleAddStream);
   //# 상대 peer 에게서 스트림 트랙을받았을때 발생
   //-> 상대가 아래의 코드를실행해줘야 addstream 이벤트가 발생함  
    myStream
   .getTracks()
   .forEach((track) => peerconnection.addTrack(track, myStream));
   // # 자신의 스트림 트랙을 이 connection 상대에게 전송함
    return peerconnection;
} 
// 완료
function handleice(data,sid){ //해당 setRemoteDescrition을 한 객체를 한 sid 에게 
  // 주기 위해 
  //#=> setRemoteDescrtion 에 의해 icecandidate 이벤트가 발생 
  socket.emit('ice',data.candidate, sid); // 보내야할 sid 
  // # 해당 sid 는 객체의 주인인 sid 소켓 번호임 
}
//완료 
function handleAddStream(data){
  //=> 상대가 나에게 본인의 스트림 트랙을 addtrack 해주었을때 발생되는 이벤트 
  const streamBox = document.createElement("div");
  streamBox.className = "streamBox";

  // 스트림 적용
  const peerFace = document.createElement("video");
  peerFace.srcObject = data.streams[0];


  // 네모칸에 스트림 추가
  streamBox.appendChild(peerFace);
  streamContainer.appendChild(streamBox);
} 
  //완료  
  socket.on('offer',async(offerarray)=>{
    offerlist = offerarray;
    for(let i = 0; i< Math.min(offerlist.length,memberlist.length); i++){
      const offer = offerlist[i];
      const sid = memberlist[i];
      const peerconnection = await makeaddconnection(sid); 
      //# 참조로 가져옴
      peerconnection.setRemoteDescrition(offer); //아이스 캔디 이벤트,발생시점 
        //) # 이벤트 발생 
      }
  });
  // 완료 
  socket.on('offeradd',async(offer,sid)=>{

    const peerconnection = await makeaddconnection(sid);
    peerconnection.setRemoteDescrition(offer); // 아이스 캔디 이벤트 발생시점 

  }); 
  // 완료
  socket.on('ice',(icedata,sid)=>{
     const index = findIndexInList(sid);
     if(index >= 0 ){
      peerindex =peerlistconnections[index];
      peerindex.addIceCandidate(icedata);
      // addIcecandidate 이거하는 
      //순간 addstream 이벤트가 발생되나 ? 
     }
  });
  // 완료
  function findIndexInList(targetValue) {
    for (let i = 0; i < memberlist.length; i++) {
        if (memberlist[i] === targetValue) {
            return i;
        }
    }
    return -1; // 값이 리스트에 없을 경우 -1을 반환합니다.
}
  
   
  //#endregion
  //#region  ice 이벤트  후 처리 

  //#endregion

})();