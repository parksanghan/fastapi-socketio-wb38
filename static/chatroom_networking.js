var myID;
var _peer_list = {};

// socketio 
var protocol = window.location.protocol;
var socket = io('https://127.0.0.1:5000');
//var socket = io('http://127.0.0.1:5000');

document.addEventListener("DOMContentLoaded", (event)=>{
    startCamera();
});

var camera_allowed=false; 
var mediaConstraints = {
    audio: true,
    video: {
        height: 360
    }
};

function startCamera()
{
    navigator.mediaDevices.getUserMedia(mediaConstraints)
    .then((stream)=>{
        myVideo.srcObject = stream;
        camera_allowed = true;
        setAudioMuteState(audioMuted);                
        setVideoMuteState(videoMuted);
        //start the socketio connection
        socket.connect();
    })
    .catch((e)=>{
        console.log("getUserMedia Error! ", e);
    });
}



socket.on("connect", ()=>{
    console.log("socket connected....");
    console.log(myRoomID);
    socket.emit("join-room", {"room_id": myRoomID});
});
socket.on("user-connect", (data)=>{
    console.log("user-connect ", data);
    let peer_id = data["sid"];
    let display_name = data["name"];
    _peer_list[peer_id] = undefined; // add new user to user list
    addVideoElement(peer_id, display_name);
});
socket.on("user-disconnect", (data)=>{
    console.log("user-disconnect ", data);
    let peer_id = data["sid"];
    closeConnection(peer_id);
    removeVideoElement(peer_id);
});
socket.on("user-list", (data)=>{
    console.log("user list recvd ", data);
    myID = data["my_id"];
    console.log("myid",myID);
    if( "list" in data) // not the first to connect to room, existing user list recieved
    {
        let recvd_list = data["list"];  
        // add existing users to user list
        for(peer_id in recvd_list)
        {
            display_name = recvd_list[peer_id];
            _peer_list[peer_id] = undefined;
            addVideoElement(peer_id, display_name);
        } 
        start_webrtc();
    }    
});

function closeConnection(peer_id)
{
    if(peer_id in _peer_list)
    {
        _peer_list[peer_id].onicecandidate = null;
        _peer_list[peer_id].ontrack = null;
        _peer_list[peer_id].onnegotiationneeded = null;

        delete _peer_list[peer_id]; // remove user from user list
    }
}

function log_user_list()
{
    for(let key in _peer_list)
    {
        console.log(`${key}: ${_peer_list[key]}`);
    }
}

//---------------[ webrtc ]--------------------    

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

function log_error(e){console.log("[ERROR] ", e);}
function sendViaServer(data){socket.emit("data", data);}

socket.on("chatrespond",(data)=>{ 
    var index = 0;
    let name  = data["name"]
    let message =  data["message"]
    var messageList = document.getElementById('user-chat-messages'); // 요소를 가져옵니다.
    var newMessage = document.createElement('li'); // 새로운 리스트 아이템을 생성합니다.
    var textNode = document.createTextNode(name + ": " ); // 텍스트 노드를 생성합니다.
    newMessage.appendChild(textNode); // 리스트 아이템에 텍스트 노드를 추가합니다.
    messageList.appendChild(newMessage); // 요소에 리스트 아이템을 추가합니다.
    var interval = setInterval(function() {
        // 텍스트의 모든 글자를 출력했는지 확인
        if (index < message.length) {
            // 다음 글자를 텍스트 요소에 추가
            messageList.lastChild.textContent += message[index];
            // 다음 글자로 이동
            index++;
        } else {
            // 모든 글자를 출력한 경우 interval을 멈춤
            clearInterval(interval);
        }
    }, 25); // 0.1초(100밀리초)마다 실행
});

   
socket.on("tutor",()=>{
    var event = new Event("tutor");
    document.dispatchEvent(event);
});

socket.on("GetAnswer",(data)=>{
    var index= 0;
    console.log(data);
    //인터벌 함수 중지 
    clearInterval(ellipsisInterval);
    var messageList = document.getElementById('ai-chat-messages'); // 요소를 가져옵니다.
    // 인터벌 메세지 지우기 
    // messageList.removeChild(messageList.lastChild);

    var newMessage = document.createElement('li'); // 새로운 리스트 아이템을 생성합니다.
    var textNode = document.createTextNode("흙PT : "); // 텍스트 노드를 생성합니다.
    newMessage.appendChild(textNode); // 리스트 아이템에 텍스트 노드를 추가합니다.
    messageList.appendChild(newMessage); // 요소에 리스트 아이템을 추가합니다.
    var interval = setInterval(function() {
        // 텍스트의 모든 글자를 출력했는지 확인
        if (index < data.length) {
            // 다음 글자를 텍스트 요소에 추가
            messageList.lastChild.textContent += data[index];
            // 다음 글자로 이동
            index++;
        } else {
            // 모든 글자를 출력한 경우 interval을 멈춤
            clearInterval(interval);
        }
    }, 20); // 0.1초(100밀리초)마다 실행
});
socket.on("GetAnswer_Add",(data)=>{
    messageList = document.getElementById('ai-chat-messages')
    clearInterval(ellipsisInterval);
    messageList.removeChild(messageList.lastChild);
    var blob = new Blob([data], { type: 'image/png' }); // 전달된 바이트 데이터를 Blob으로 변환
    var imageUrl = URL.createObjectURL(blob); // Blob을 URL로 변환하여 이미지로 사용

    // 이미지를 보여줄 ul 요소를 선택합니다.
    var ulElement = document.getElementById('ai-chat-messages');

    // 이미지를 보여줄 li 요소를 생성하고 이미지를 추가합니다.
    var liElement = document.createElement('li');
    var imgElement   = document.createElement('img');
    imgElement.src = imageUrl;
    liElement.appendChild(imgElement);
    ulElement.appendChild(liElement);
});
socket.on("FineTuneStart",(data)=>{
    is_started =  data
    done_message = ""
    if (is_started  == true){
        done_message = "성공"
    }
    else {
        done_message = "실패"
    }
    var messageList = document.getElementById('ai-chat-messages'); // 요소를 가져옵니다.
    var newMessage = document.createElement('li'); // 새로운 리스트 아이템을 생성합니다.
    var textNode = document.createTextNode("해당강좌의 파인튜닝 시작이 "+done_message+" 하였습니다"); // 텍스트 노드를 생성합니다.
    newMessage.appendChild(textNode); // 리스트 아이템에 텍스트 노드를 추가합니다.
    messageList.appendChild(newMessage); // 요소에 리스트 아이템을 추가합니다.
});// data true or fasle 
socket.on("FineTuneEnd",(data)=>{
    is_started =  data
    done_message = ""
    if (is_started  == true){
        done_message = "성공"
    }
    else {
        done_message = "실패"
    }
    var messageList = document.getElementById('ai-chat-messages'); // 요소를 가져옵니다.
    var newMessage = document.createElement('li'); // 새로운 리스트 아이템을 생성합니다.
    var textNode = document.createTextNode("해당강좌의 파인튜닝 완료가"+done_message+" 입니다"); // 텍스트 노드를 생성합니다.
    newMessage.appendChild(textNode); // 리스트 아이템에 텍스트 노드를 추가합니다.
    messageList.appendChild(newMessage); // 요소에 리스트 아이템을 추가합니다.
});// data true or fasle 
socket.on("data", (msg)=>{
    switch(msg["type"])
    {
        case "offer":
            handleOfferMsg(msg);
            break;
        case "answer":
            handleAnswerMsg(msg);
            break;
        case "new-ice-candidate":
            handleNewICECandidateMsg(msg);
            break;
    }
});

function start_webrtc()
{
    // send offer to all other members
    for(let peer_id in _peer_list)
    {
        invite(peer_id);
    }
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function invite(peer_id)
{
    if(_peer_list[peer_id]){console.log("[Not supposed to happen!] Attempting to start a connection that already exists!")}
    else if(peer_id === myID){console.log("[Not supposed to happen!] Trying to connect to self!");}
    else
    {
        console.log(`Creating peer connection for <${peer_id}> ...`);
        createPeerConnection(peer_id);
        await sleep(2000);
        let local_stream = myVideo.srcObject;
        console.log(myVideo.srcObject);
        local_stream.getTracks().forEach((track)=>{_peer_list[peer_id].addTrack(track, local_stream);});
        console.log(myVideo.srcObject);
    }
}

function createPeerConnection(peer_id)
{
    _peer_list[peer_id] = new RTCPeerConnection(PC_CONFIG);

    _peer_list[peer_id].onicecandidate = (event) => {handleICECandidateEvent(event, peer_id)};
    _peer_list[peer_id].ontrack = (event) => {handleTrackEvent(event, peer_id)};
    _peer_list[peer_id].onnegotiationneeded = () => {handleNegotiationNeededEvent(peer_id)};
}


function handleNegotiationNeededEvent(peer_id)
{
    _peer_list[peer_id].createOffer()
    .then((offer)=>{return _peer_list[peer_id].setLocalDescription(offer);})
    .then(()=>{
        console.log(`sending offer to <${peer_id}> ...`);
        sendViaServer({
            "sender_id": myID,
            "target_id": peer_id,
            "type": "offer",
            "sdp": _peer_list[peer_id].localDescription
        });
    })
    .catch(log_error);
} 

function handleOfferMsg(msg)
{   
    peer_id = msg['sender_id'];

    console.log(`offer recieved from <${peer_id}>`);
    
    createPeerConnection(peer_id);
    let desc = new RTCSessionDescription(msg['sdp']);
    _peer_list[peer_id].setRemoteDescription(desc)
    .then(()=>{
        let local_stream = myVideo.srcObject;
        local_stream.getTracks().forEach((track)=>{_peer_list[peer_id].addTrack(track, local_stream);});
    })
    .then(()=>{return _peer_list[peer_id].createAnswer();})
    .then((answer)=>{return _peer_list[peer_id].setLocalDescription(answer);})
    .then(()=>{
        console.log(`sending answer to <${peer_id}> ...`);
        sendViaServer({
            "sender_id": myID,
            "target_id": peer_id,
            "type": "answer",
            "sdp": _peer_list[peer_id].localDescription
        });
    })
    .catch(log_error);
}

function handleAnswerMsg(msg)
{
    peer_id = msg['sender_id'];
    console.log(`answer recieved from <${peer_id}>`);
    let desc = new RTCSessionDescription(msg['sdp']);
    _peer_list[peer_id].setRemoteDescription(desc)
}


function handleICECandidateEvent(event, peer_id)
{
    if(event.candidate){
        sendViaServer({
            "sender_id": myID,
            "target_id": peer_id,
            "type": "new-ice-candidate",
            "candidate": event.candidate
        });
    }
}

function handleNewICECandidateMsg(msg)
{
    console.log(`ICE candidate recieved from <${peer_id}>`);
    var candidate = new RTCIceCandidate(msg.candidate);
    _peer_list[msg["sender_id"]].addIceCandidate(candidate)
    .catch(log_error);
}


function handleTrackEvent(event, peer_id)
{
    console.log(`track event recieved from <${peer_id}>`);
    
    if(event.streams)
    {
        getVideoObj(peer_id).srcObject = event.streams[0];
    }
}