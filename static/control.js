function initializeMicrophoneTest() {
    
    const record = document.getElementById("record-start");
    
   
    const chkHearMic = document.getElementById("chk-hear-mic");

    const audioCtx = new (window.AudioContext || window.webkitAudioContext)(); // 오디오 컨텍스트 정의

    const analyser = audioCtx.createAnalyser();

    function makeSound(stream) {
        const source = audioCtx.createMediaStreamSource(stream);
        
        source.connect(analyser);
        analyser.connect(audioCtx.destination);
    }

    if (navigator.mediaDevices) {
        console.log('getUserMedia supported.');

        const constraints = {
            audio: true
        };
        let chunks = [];

        navigator.mediaDevices.getUserMedia(constraints)
            .then(stream => {
                const mediaRecorder = new MediaRecorder(stream);

                chkHearMic.onchange = e => {
                    if (e.target.checked == true) {
                        audioCtx.resume();
                        makeSound(stream);
                    } else {
                        audioCtx.suspend();
                    }
                };

                record.onclick = () => {
                    mediaRecorder.start(1000);
                    console.log(mediaRecorder.state);
                    console.log("recorder started");
                    record.style.background = "red";
                    record.style.color = "black";
                };

                stop.onclick = () => {
                    mediaRecorder.stop();
                    console.log(mediaRecorder.state);
                    console.log("recorder stopped");
                    record.style.background = "";
                    record.style.color = "";
                };

                mediaRecorder.onstop = e => {
                    console.log("data available after MediaRecorder.stop() called.");
                    const bb = new Blob(chunks, { 'type': 'audio/wav' });
                    socket.emit('voice', bb);
                    const clipName = prompt("오디오 파일 제목을 입력하세요.", new Date());

                    const clipContainer = document.createElement('article');
                    const clipLabel = document.createElement('p');
                    const audio = document.createElement('audio');
                    const deleteButton = document.createElement('button');

                    clipContainer.classList.add('clip');
                    audio.setAttribute('controls', '');
                    deleteButton.innerHTML = "삭제";
                    clipLabel.innerHTML = clipName;

                    clipContainer.appendChild(audio);
                    clipContainer.appendChild(clipLabel);
                    clipContainer.appendChild(deleteButton);
                    soundClips.appendChild(clipContainer);

                    audio.controls = true;
                    const blob = new Blob(chunks, {
                        'type': 'audio/ogg codecs=opus'
                    });

                    chunks = [];
                    const audioURL = URL.createObjectURL(blob);
                    audio.src = audioURL;
                    console.log("recorder stopped");

                    deleteButton.onclick = e => {
                        evtTgt = e.target;
                        evtTgt.parentNode.parentNode.removeChild(evtTgt.parentNode);
                    };
                };

                mediaRecorder.ondataavailable = function (e) {
                    chunks.push(e.data);
                    if (chunks.length >= 5) {
                        const bloddb = new Blob(chunks, { 'type': 'audio/wav' });
                        socket.emit('voice', bloddb);

                        chunks = [];
                    }
                };
            })
            .catch(err => {
                console.log('The following error occurred: ' + err);
            });
    }
}
