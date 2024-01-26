
 
import socket
import sys, os, signal
import threading
from time import sleep


onDebug : bool = False;

parseMarker : str = "0@$-"

class Server ():
    # callback => (Socket s, string str) => {}
    def __init__(self, ip, port, callback) :
        # ���� ����
        self.host = ip
        self.port = port
        # ���� ����
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Ŭ���̾�Ʈ �����
        self.readThreads = []
        self.clients = []
        self.callback = callback
        
    def Deploy(self) :
        # �ּҿ� ��Ʈ�� ���Ͽ� ���ε�
        self.server_socket.bind((self.host, self.port))

        # ���� ���
        self.server_socket.listen()

        print(f"������ {self.host}:{self.port}���� ��� ���Դϴ�.")
        
        self.acceptThread = threading.Thread(target = self.AcceptThread)
        self.acceptThread.start()
        
    def Send(self, msg) :
        self.clients[0].send((msg + parseMarker).encode('utf-8'))
        if(onDebug): print("[SEND] : " + msg)
    
    def AcceptThread(self) :
        
        print("���� - AcceptThread ����")
        while True :
            # Ŭ���̾�Ʈ ���� ����

            print("���� - ���� �����...")
            client_socket, client_address = self.server_socket.accept()
            print(f"{client_address}�� ����Ǿ����ϴ�.")
            
            self.clients.append(client_socket)
            
            thread = threading.Thread(target = self.ReadThread, args=[client_socket])
            self.readThreads.append(thread)
            thread.start()

    def ReadThread(self, client_socket : socket) :
        while True :
            try :
                # Ŭ���̾�Ʈ�κ��� ������ �ޱ�
                data = client_socket.recv(1024 * 16).decode('utf-8')
                #print(f"������ ������ ������: {data}")
                spDatas = data.split(parseMarker)
                for spData in spDatas :
                    if(onDebug): print("[RECV] : " + spData)
                    self.callback(client_socket, spData)
            except ConnectionResetError as ex :
                # ������ ������������ ����� ����� ó��.
                # �������� ���� ���Ͽ� ���� ���� ����

                if threading.current_thread() in self.readThreads:
                    self.readThreads.remove(threading.current_thread())
                    
                if client_socket in self.clients :
                    self.clients.remove(client_socket)
                    
                client_socket.close()
                
                break; # ������ ����
    
            
    def __del__ (self) :
        # ���� ����
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
        # ���� ����
        self.host = ip
        self.port = port
        # ���� ����
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #���� �����
        self.callback = callback
        
    def Connect(self) :
        
        try :
            # ������ ����
            self.client_socket.connect((self.host, self.port))
            print(f"������ ����Ǿ����ϴ�.")

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
                # Ŭ���̾�Ʈ�κ��� ������ �ޱ�
                data = self.client_socket.recv(1024 * 16).decode('utf-8')
                # print(f"Ŭ���̾�Ʈ�� ������ ������: {data}")
                spDatas = data.split(parseMarker)
                for spData in spDatas :
                    if(onDebug): print("[RECV] : " + spData)
                    self.callback(spData)
            except  ConnectionResetError:
                ExitCode();

            
    def __del__ (self) :
        # ���� ����
        self.client_socket.close()





