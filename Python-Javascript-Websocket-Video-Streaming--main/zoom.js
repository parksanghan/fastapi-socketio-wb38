'use strict';
 
(function() {

  const socket = io('http://127.0.0.1:5000'); // 이거 주소 지워야할수도 
  const myFace = document.getElementById("myFace");
  const muteBtn = document.getElementById("mute");
  const cameraBtn = document.getElementById("camera");
  const camerasSelect = document.getElementById("cameras");
  const call = document.getElementById("call");

  call.hidden = true;

let myStream;
let muted = false;
let cameraOff = false;
let roomName;
let myPeerConnection;
let myDataChannel;


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
  roomlist = [];
  memberlist =[];
  offerlist=[];
  is_tutor = false;
  peerlistconnections = [];
  roomlist  = document.getElementById('roomlist');
  function updateListBox(data) {
    if (Array.isArray(data)) {
        // 리스트 형태의 데이터인 경우 초기화 후 추가
        listBox.innerHTML = ''; // 기존 내용 초기화

        for (var i = 0; i < data.length; i++) {
            var option = document.createElement('option');
            option.value = data[i];
            option.text = data[i];
            listBox.add(option);
        }
    } else {
        // 값이 하나인 경우 기존 내용에 추가
        var option = document.createElement('option');
        option.value = data;
        option.text = data;
        listBox.add(option);
    } }
  listbox.addEventListener('change',updateListBox)
  //#region  connect 후처리 
  socket.on('connected', async(data)=> { // 연결되었을때 방 리스트 받음
    console.log(`connected ${socket.id}`);
    roomlist =  data; // updatelistbox 이벤트핸들러 호출됨  change 이벤트 발생으로 
    
    for (var i = 0; i < data.length; i++) {
      var option = document.createElement('option');
      option.value = data[i];
      option.text = data[i];
      listBox.add(option);
  }
    
  });
  //#endregion
  //#region  join room 이벤트 후처리 이벤트 
  socket.on('roomadd',(roomname)=>{ // 방추가 알림 
    console.log('roomadd');
    roomlist.push(roomname); // change 이벤트, 발생  
    var option = document.createElement('option');
    option.value = data[i];
    option.text = data[i];
    listBox.add(option);
  });

  socket.on('istutor',()=>{
    console.log('you are tutor');
    is_tutor = true;  
  });
  is_tutor.addEventListener('change') // 값이 바뀌면 true 임 즉 tutor 이므로
  // 이벤트 발생시 함수로 다른쓰레드로 setinterval로 10초마다 서버로 업데이트 

  socket.on('roomconnected',async(sidlist)=>{
    console.log('roomconnected');
    memberlist  = sidlist;
    const myoffer  = await myPeerConnection.createOffer();
    myPeerConnection.setLocalDescription(myoffer);
    console.log(`send my offer to server`);
    socket.emit(' offer',myoffer);
  })

  socket.on('user_connect',(sid)=>{
    console.log(`user_connected_room  ${sid}`);
    memberlist.push(sid);
  });
  //#endregion
  //#region  disconnect 후처리 
  socket.on('disconnect',  () => {
    console.log(`disconnect ${socket.id}`);
    console.log('server disconnected')
  });

  socket.on('user-disconnect',  (sid) => {
    console.log(`user-disconnect ${socket.id}`);
    memberlist.pop(sid); // for 문처리 필요 
  });
  socket.on('roomremove',(nameroom)=>
  {
    console.log('roomdeleted');
    removeOptionByRoomName(nameroom);// 웹에서만 지움 
  });
  function removeOptionByRoomName(valueToRemove) {
    var options = listBox.options;

    for (var i = 0; i < options.length; i++) {
        if (options[i].value === valueToRemove) {
            options[i].remove();
            
            // 만약에 valueToRemove를 가진 데이터가 있다면, 그 데이터도 원본 배열에서 제거합니다.
            var indexInDataArray = originalData.indexOf(valueToRemove);
            if (indexInDataArray !== -1) {
                originalData.splice(indexInDataArray, 1);
            }

            break;  // 찾은 후에는 더 이상 반복할 필요가 없으므로 루프를 종료합니다.
        }
    }
}
 
  //#endregions
  //#region offer 송수신 부분

async function makeaddconnection(sid) 
//#=> offeradd 즉 , offer 주는 클라이언트 추가시 마다 반복 
{
  const peerconnection   = new RTCPeerConnection(configure);
   peerConnectionlist.push(peerconnection);
   peerconnection.addEventListener("icecandidate", handleice(sid));
   // 등록된 sid 값으로 이벤트 발동됨 
   peerconnection.addEventListener("track", handleAddStream(sid));
   //# 상대 peer 에게서 스트림 트랙을받았을때 발생
   //-> 상대가 아래의 코드를실행해줘야 addstream 이벤트가 발생함  
    myStream
   .getTracks()
   .forEach((track) => peerconnection.addTrack(track, myStream));
   // # 자신의 스트림 트랙을 이 connection 상대에게 전송함
    return peerconnection;
}
function handleice(sid){
  //#=> setRemoteDescrtion 에 의해 icecandidate 이벤트가 발생 
  icecandidate=data.candidate
  socket.emit('ice',icecanddiate, sid)
  // # 해당 sid 는 객체의 주인인 sid 소켓 번호임 
}
function handleAddStream(){
  //=> 상대가 나에게 본인의 스트림 트랙을 addtrack 해주었을때 발생되는 이벤트 
  const streamBox = document.createElement("div");
  streamBox.className = "streamBox";

  // 스트림 적용
  const peerFace = document.createElement("video");
  peerFace.srcObject = data.stream;


  // 네모칸에 스트림 추가
  streamBox.appendChild(peerFace);
  streamContainer.appendChild(streamBox);
} 

  socket.on('offer',async(offerarray,)=>{
    for(let i = 0; i< Math.min(offerlist.length,memberlist.length); i++){
      const offer = offerlist[i];
      const sid = memberlist[i];
      peerconnection = await makeaddconnection(sid); 
      //# 참조로 가져옴
      peerconnection.setRemoteDescrition(offer); //아이스 캔디 이벤트,발생시점 
        //) # 이벤트 발생 
      }
  });
  
  socket.on('offeradd',async(offer,sid)=>{

    peerconnection = await makeaddconnection(sid) ;
    peerconnection.setRemoteDescrition(offer); // 아이스 캔디 이벤트 발생시점 

  });

  socket.on('ice',(icedata,sid)=>{
     index = findIndexInList(sid);
     if(index => 0 ){
      peerindex =peerlistconnections[index];
      peerindex.addIceCandidate(icedata);
     }
  });
 
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