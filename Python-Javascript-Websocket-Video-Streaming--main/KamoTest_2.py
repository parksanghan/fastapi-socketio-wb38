from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from socketio import AsyncServer, AsyncNamespace
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

app = FastAPI()

# Socket.IO configuration
sio = AsyncServer(cors_allowed_origins="*")

# Socket.IO namespace for data channel
class DataChannelNamespace(AsyncNamespace):
    async def on_connect(self, sid, environ):
        print(f"Client connected: {sid}")

    async def on_disconnect(self, sid):
        print(f"Client disconnected: {sid}")

# Register the namespace
sio.register_namespace(DataChannelNamespace)

# WebSocket route
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print(f"Received data: {data}")

# Attach the Socket.IO server to the app
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)