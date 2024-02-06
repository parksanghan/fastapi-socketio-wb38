async function uploadFile(sid, file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`/upload/${sid}`, {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      console.log("File uploaded successfully");
    } else {
      console.error("Failed to upload file");
    }
  } catch (error) {
    console.error("Error during file upload:", error);
  }
}

document
  .getElementById("file-upload-btn")
  .addEventListener("click", function () {
    document.getElementById("file-upload-dialog").style.display = "block";
  });

document
  .getElementById("close-dialog-btn")
  .addEventListener("click", function () {
    document.getElementById("file-upload-dialog").style.display = "none";
  });

var dropZone = document.getElementById("drop_zone");

dropZone.addEventListener("dragover", function (e) {
  e.stopPropagation();
  e.preventDefault();
  e.dataTransfer.dropEffect = "copy";
});

dropZone.addEventListener("drop", function (e) {
  e.stopPropagation();
  e.preventDefault();
  var files = e.dataTransfer.files;

  console.log("dragover");

  document.getElementById("file-input").files = files;
});

document.getElementById("file-input").addEventListener("change", function (e) {
  var files = e.target.files;
});

document.getElementById("submit-btn").addEventListener("click", function () {
  // 'Submit' 버튼 클릭 시 수행할 작업을 여기에 작성하세요.

  const sid = myID; // 실제 sid 값을 적용해야 합니다.
  /**
   * @type {FileList}
   */
  const fileInput = document.getElementById("file-input").files; // 파일 입력 요소의 ID에 맞게 변경해야 합니다.

  console.log("submit-btn-click" + String(fileInput.item(0)));

  if (fileInput.item(0)) {
    uploadFile(sid, fileInput.item(0));
  } else {
    console.error("No file selected");
  }
});

document.getElementById("record-start").addEventListener("click", function () {
  if (navigator.mediaDevices) {
    console.log("getUserMedia supported.");
    this.style.background = "red";
    this.style.color = "black";

    recordStartButton.style.color = "black";
    recordStopButton.style.background = "white";

    const constraints = {
      audio: true,
    };
    let chunks = [];
    navigator.mediaDevices
      .getUserMedia(constraints)
      .then((stream) => {
        mediaRecorder = new MediaRecorder(stream);

        chkHearMic.onchange = (e) => {
          if (e.target.checked == true) {
            audioCtx.resume();
            makeSound(stream);
          } else {
            audioCtx.suspend();
          }
        };
        mediaRecorder.start(1000);
        console.log(mediaRecorder.state);
        mediaRecorder.onstop = (e) => {
          console.log("onstop happen!");

          if (chunks.length >= 9) {
            console.log("data available after MediaRecorder.stop() called.");
            const bb = new Blob(chunks, { type: "audio/wav" });
            socket.emit("voice", bb);
          }
          chunks = [];
        };
        mediaRecorder.ondataavailable = function (e) {
          chunks.push(e.data);
          console.log("add " + String(chunks.length));

          if (chunks.length >= 10) {
            mediaRecorder.stop();
            //const bloddb = new Blob(chunks, { 'type' : 'audio/wav' })
            //socket.emit('voice', bloddb)

            //chunks = []
            mediaRecorder.start(1000);
            //console.log("end " + String(chunks.length))
          }

          mediaRecorder.sendData = function (buffer) {
            const bloddb = new Blob(buffer, { type: "audio/wav" });
            socket.emit("voice", bloddb);

            console.log("end " + String(chunks.length));
          };
        };

        // Call makeSound() function here
      })
      .catch((err) => {
        console.log("The following error occurred: " + err);
      });
  } else {
    console.error("getUserMedia not supported on your browser!");
  }
});

document.getElementById("record-stop").addEventListener("click", function () {
  if (navigator.mediaDevices) {
    console.log("STOP INIT!");
    this.style.background = "red";
    this.style.color = "black";

    recordStartButton.style.background = "white";

    const constraints = {
      audio: true,
    };

    navigator.mediaDevices
      .getUserMedia(constraints)
      .then((stream) => {
        mediaRecorder.stop(1000);
        console.log(mediaRecorder.state);

        mediaRecorder.onstop = (e) => {
          console.log("STOP EXEC!");

          if (chunks.length > 1) {
            console.log("STOP SEND!");
            const bb = new Blob(chunks, { type: "audio/wav" });
            socket.emit("voice", bb);
          }
          chunks = [];
        };

        mediaRecorder.ondataavailable = (e) => {};
        // Call makeSound() function here
      })
      .catch((err) => {
        console.log("The following error occurred: " + err);
      });
  } else {
    console.error("getUserMedia not supported on your browser!");
  }
});

document.getElementById("user-send-btn").addEventListener("click", function () {
  var inputElement = document.getElementById("user-chat-input");
  var message = inputElement.value;
  socket.emit("chat", message); // 메세지 전송 후
  inputElement.value = ""; // 입력란을 공백으로 초기화
});
document.getElementById('ai-send-btn').addEventListener('click', function(){
  let count = 1;
  let dots = ".";
  var inputElement = document.getElementById('ai-chat-input');
  var message = inputElement.value;
  var messageList = document.getElementById('ai-chat-messages'); // 요소를 가져옵니다.
  var newMessage = document.createElement('li'); // 새로운 리스트 아이템을 생성합니다.
  var textNode = document.createTextNode("나 : "+message); // 텍스트 노드를 생성합니다.
  newMessage.appendChild(textNode); // 리스트 아이템에 텍스트 노드를 추가합니다.
  messageList.appendChild(newMessage); // 요소에 리스트 아이템을 추가합니다.
  var newNodeMessage = document.createElement('li'); // 새로운 리스트 아이템을 생성합니다.
  var newtextNode = document.createTextNode("흙PT 답변 생성 중.."); // 텍스트 노드를 생성합니다.
  newNodeMessage.appendChild(newtextNode); // 리스트 아이템에 텍스트 노드를 추가합니다.
  messageList.appendChild(newNodeMessage); // 요소에 리스트 아이템을 추가합니다.
  socket.emit('question', message); // 메세지 전송 후 
  inputElement.value = ""; // 입력란을 공백으로 초기화
  let showEllipsis = true;
  ellipsisInterval = setInterval(() => {
      let displayedDots = dots.repeat(count);
      // 마지막 메시지를 가져옵니다.
      let lastMessage = messageList.lastChild;
      // 마지막 메시지의 텍스트를 업데이트합니다.
      lastMessage.textContent = "흙PT 답변 중 : " + displayedDots;
      count = (count % 4) + 1; // 1부터 3까지 순환
  }, 1000);
});
document.addEventListener("tutor", function () {
  // 라벨과 오디오 체크박스를 버튼들의 옆에 배치합니다.
  labelmic.style.display = "inline-block";

  checkBoxAudio.style.display = "inline-block";

  // 버튼들을 세로로 나열합니다.
  fileuploadButton.style.display = "inline-block";
  recordStartButton.style.display = "inline-block";
  recordStopButton.style.display = "inline-block";
});
