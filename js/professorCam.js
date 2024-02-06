 
    // DOMContentLoaded 이벤트가 발생하면 실행되는 코드
    var myRoomID = "{{room_id}}";
    var myName = "{{display_name}}";
    var audioMuted = "{{mute_audio}}" == "1";
    var videoMuted = "{{mute_video}}" == "1";
    console.log(">> {{mute_audio}}, {{mute_video}}", audioMuted, videoMuted);
    console.log(myName, myRoomID);
    var checkBoxAudio = document.getElementById("chk-hear-mic");
    var recordStartButton = document.getElementById("record-start");
    var recordStopButton = document.getElementById("record-stop");
    var fileuploadButton = document.getElementById("file-upload-btn");
    var labelmic = document.querySelector('label[for="chk-hear-mic"]');
    checkBoxAudio.style.display = "none";
    recordStartButton.style.display = "none";
    recordStopButton.style.display = "none";
    fileuploadButton.style.display = "none";
    labelmic.style.display = "none";
 
