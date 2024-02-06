const chkHearMic = document.getElementById("chk-hear-mic");
const audioCtx = new (window.AudioContext || window.webkitAudioContext)(); // 오디오 컨텍스트 정의
const analyser = audioCtx.createAnalyser();

let mediaRecorder;
let chunks = [];
function makeSound(stream) {
  const source = audioCtx.createMediaStreamSource(stream);
  source.connect(analyser);
  analyser.connect(audioCtx.destination);
}
