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
  roomlist = [];
  memberlist =[];
  offerlist=[];
  is_tutor = false;
  peerlistconnections = []
  //#region  connect 후처리 
  socket.on('connected', (data)=> { // 연결되었을때 방 리스트 받음
    console.log(`connect ${socket.id}`);
    console.log(data);
    roomlist = data;
  });
  //#endregion
  //#region  join room 이벤트 후처리 이벤트 
  socket.on('roomadd',(roomname)=>{
    console.log('roomadd');
    roomlist.push(roomname);
  });

  socket.on('istutor',()=>{
    console.log('you are tutor');
    is_tutor = true;
  });

  socket.on('roomconnected',(roomlistdata)=>{
    console.log('roomconnected');
    memberlist  = roomlistdata;
  })

  socket.on('user_connect',(sid)=>{
    console.Console;log(`user_connected_room  ${sid}`);
    memberlist.push(sid);
  });
  //#endregion
  //#region  disconnect 후처리 
  socket.on('disconnect',  () => {
    console.log(`disconnect ${socket.id}`);
    console.log('server disconnected')
  });

  socket.on('user-disconnect',  (sid) => {
    console.log(`disconnect ${socket.id}`);
    memberlist.pop(sid);
  });
  socket.on('roomremove',(nameroom)=>
  {
    console.log('roomdeleted');
    roomlist.pop(nameroom);
  });
  //#endregions

  socket.on('hello', (a, b, c) => {
    console.log(a, b, c);
  });
 

})();