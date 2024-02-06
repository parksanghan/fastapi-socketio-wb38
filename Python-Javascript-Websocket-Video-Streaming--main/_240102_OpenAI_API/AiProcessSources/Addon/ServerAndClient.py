
# -*- coding: cp949 -*-
import socket
import sys, os, signal
import threading
from time import sleep


onDebug : bool = False;

parseMarker : str = "0@$-"

class Server ():
    # callback => (Socket s, string str) => {}
    def __init__(self, ip, port, callback) :
        # 서버 설정
        self.host = ip
        self.port = port
        # 소켓 생성
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #클라이언트 저장소
        self.readThreads = []
        self.clients = []
        self.callback = callback
        
    def Deploy(self) :
        # 주소와 포트를 소켓에 바인딩
        self.server_socket.bind((self.host, self.port))

        # 연결 대기
        self.server_socket.listen()

        print(f"서버가 {self.host}:{self.port}에서 대기 중입니다.")
        
        self.acceptThread = threading.Thread(target = self.AcceptThread)
        self.acceptThread.start()
        
    def Send(self, msg) :
        self.clients[0].send((msg + parseMarker).encode('utf-8'))
        if(onDebug): print("[SEND] : " + msg)
    
    def AcceptThread(self) :
        
        print("서버 - AcceptThread 실행")
        while True :
            # 클라이언트 연결 수락

            print("서버 - 연결 대기중...")
            client_socket, client_address = self.server_socket.accept()
            print(f"{client_address}가 연결되었습니다.")
            
            self.clients.append(client_socket)
            
            thread = threading.Thread(target = self.ReadThread, args=[client_socket])
            self.readThreads.append(thread)
            thread.start()

    def ReadThread(self, client_socket : socket) :
        while True :
            try :
                # 클라이언트로부터 데이터 받기
                data = client_socket.recv(1024 * 16).decode('utf-8')
                #print(f"서버가 수신한 데이터: {data}")
                spDatas = data.split(parseMarker)
                for spData in spDatas :
                    if(onDebug): print("[RECV] : " + spData)
                    self.callback(client_socket, spData)
            except ConnectionResetError as ex :
                # 연결이 비정상적으로 종료된 경우의 처리.
                # 서버에서 현재 소켓에 대한 정보 말소

                if threading.current_thread() in self.readThreads:
                    self.readThreads.remove(threading.current_thread())
                    
                if client_socket in self.clients :
                    self.clients.remove(client_socket)
                    
                client_socket.close()
                
                break; # 스레드 종료
    
            
    def __del__ (self) :
        # 연결 종료
        self.client_socket.close()
        self.server_socket.close()


def ExitCode() :
    
    user_documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
    saveDirectory = "WB38"
    filePath = f"{user_documents_path}\\{saveDirectory}"
    
    if os.path.exists(f"{user_documents_path}\\{saveDirectory}"):
        pass
    else : os.makedirs();
    
    with open(f"{filePath}\\communication_file.txt", "w") as file:
        file.write("EXIT_CODE");
        file.close()
    
    sleep(5)
    os._exit(0)
    

class Client ():
    # callback => (string str) => {}
    def __init__(self, ip, port, callback) :
        # 서버 설정
        self.host = ip
        self.port = port
        # 소켓 생성
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #서버 저장소
        self.callback = callback
        
    def Connect(self) :
        
        try :
            # 서버에 연결
            self.client_socket.connect((self.host, self.port))
            print(f"서버에 연결되었습니다.")

            self.readThread = threading.Thread(target = self.ReadThread)
            self.readThread.start()
        except  ConnectionRefusedError:
            ExitCode();
        
    def Send(self, msg) :
        self.client_socket.send((msg + parseMarker).encode('utf-8'))
        if(onDebug): print("[SEND] : " + msg)
    
    def ReadThread(self) :
        while True :
            try :
                # 클라이언트로부터 데이터 받기
                data = self.client_socket.recv(1024 * 16).decode('utf-8')
                # print(f"클라이언트가 수신한 데이터: {data}")
                spDatas = data.split(parseMarker)
                for spData in spDatas :
                    if(onDebug): print("[RECV] : " + spData)
                    self.callback(spData)
            except  ConnectionResetError:
                ExitCode();

            
    def __del__ (self) :
        # 연결 종료
        self.client_socket.close()





