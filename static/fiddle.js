'use strict';

(function() {

  const socket = io();

  socket.on('connect', data,() => {
    console.log(`connect ${socket.id}`);
    console.log(data)
  });

  socket.on('disconnect', () => {
    console.log(`disconnect ${socket.id}`);
  });

  socket.on('hello', (a, b, c) => {
    console.log(a, b, c);
  });
  socket.on('fuckshit', (a) => {
    console.log(a);
  });


})();