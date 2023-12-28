'use strict';
/*
const socket = io('http://127.0.0.1:5000'); // 이거 주소 지워야할수도

[Request]
socket.emit('someEvent', 'Hello, client!');

[Response]
socket.on('connect', (data) => {
    console.log(`connect ${socket.id}`);
    console.log(data);
});
*/

const socket = io('http://127.0.0.1:5000'); // 이거 주소 지워야할수도

socket.emit('Message', 'Hello, client!');


socket.on('Enter', (data) => {
    console.log(`Recieved : ${data}`);
});

function executeCode() {
    var textBox = document.getElementById("myTextBox");
    var enteredText = textBox.value;

    socket.emit('Message', "inserted : " + enteredText);

    window.location.href = '/navigate';
}

function toP2P()
{
    window.location.href = '/p2pPage';
}