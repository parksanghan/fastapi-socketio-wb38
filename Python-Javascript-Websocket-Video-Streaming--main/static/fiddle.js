'use strict';
 
(function() {

  const socket = io('http://127.0.0.1:5000'); // 이거 주소 지워야할수도 

  socket.on('connect', (data)=> {
    console.log(`connect ${socket.id}`);
    console.log(data);
     
  });

  socket.on('connected',(data)=>{
    console.log('you are connected');
    console.log(data);
  })
  socket.on('disconnect',  () => {
    console.log(`disconnect ${socket.id}`);
    socket.emit
  });
  

  socket.on('hello', (a, b, c) => {
    console.log(a, b, c);
  });
  socket.on('fuckshit', (a) => {
    console.log(a);
  });


})();