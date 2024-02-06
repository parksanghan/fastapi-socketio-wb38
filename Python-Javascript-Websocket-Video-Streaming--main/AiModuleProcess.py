 
import os, threading, time, subprocess
import socket
import asyncio
import aiofiles

import GlobalReference
from _240102_OpenAI_API.AiProcessSources.Addon.CustomConsolePrinter import printError, printNor, printProcess, printSucceed, printWarning
from _240102_OpenAI_API.AiProcessSources.Addon.ServerAndClient import Server 
import socketio
subsio= None
async def send_file(filepath, target_sid):
    if os.path.exists(filepath):  # 파일이 존재하는지 확인
        async with aiofiles.open(filepath, 'rb') as file:
            target_file = await file.read()
            await subsio.emit('GetAnswer_Add',
            data=target_file, to=target_sid)
            print("GetAnswer_Add 이벤트 파일 전송 완료")
    else:
        printError(f"파일이 존재하지 않습니다: {filepath}")
class AiModuleProcess():
    def __init__(self,sio : socketio.AsyncServer) :
    
        self.p1 = GlobalReference.PARSER[0]
        self.p2 = GlobalReference.PARSER[1]        
        self.subsio = sio
        global subsio 
        if subsio is None:
            subsio= self.subsio
        self.loadAiThread : threading.Thread = None
        self.initAiThread : threading.Thread = None
       
        self.server : Server;
        self.clientIsAvailable : bool = False;
       
        self.__ServerInit__()
    
    def __ServerInit__(self) :
        # 서버 생성
        self.server = Server('127.0.0.1', 4090, self.__ServerDel__)
        self.server.Deploy()
         
        #서버와 연결할 클라이언트를 가진 AI 프로세스를 불러온다.
        self.__LoadAiProcess__()
        
        while self.clientIsAvailable == False : time.sleep(1.)
        
    def __ServerDel__(self, client_socket : socket, packet) :
        p1 = self.p1
        p2 = self.p2
        
        sp = packet.split(p1)
        flag = sp[0]
        
        try : 
            match flag: 
                case "ProcessStart": 
                    self.clientIsAvailable = True;

                case "ProcessEnd ":
                    ssp = sp[1].split(p2)
                    isSucceed = True if ssp[0] == str(True) else False
                    if isSucceed :
                        printSucceed("성공적으로 AI 프로세스가 종료됐습니다.")
                    else:
                        printWarning("AI 프로세스 종료 중 알 수 없는 문제가 있었습니다. AI 프로세스를 확인해주세요.")
                    
                case "LectureCreate":
                    ssp = sp[1].split(p2)
                    isSucceed = True if ssp[0] == str(True) else False
                    lecture = ssp[1]
                    
                    if isSucceed :
                        printSucceed(f"성공적으로 '{lecture}' 과목을 생성했습니다.")
                    else:
                        printError(f"'{lecture}' 과목을 생성하는데 실패했습니다.")
                
                case "LectureDelete": 
                    ssp = sp[1].split(p2)
                    isSucceed = True if ssp[0] == str(True) else False
                    lecture = ssp[1]
                    
                    if isSucceed :
                        printSucceed(f"성공적으로 '{lecture}' 과목을 삭제했습니다.")
                    else:
                        printError(f"'{lecture}' 과목을 삭제하는데 실패했습니다.")
                
                case "LectureList":
                    ssp = sp[1].split(p2)
                    lecList = list(filter(None, ssp[0].split(p2)))
                    
                    ret = f"성공적으로 강좌 리스트를 불러오기 성공. ({len(lecList)}개)\n"
                    for lec in lecList : ret += f"{lecList}\n"

                    printSucceed(ret)
                
                case "SendDataPdf": 
                    ssp = sp[1].split(p2)
                    isSucceed = True if ssp[0] == str(True) else False
                    lecture = ssp[1]
                    path = ssp[2]
                    
                    if isSucceed :
                        printSucceed(f"성공적으로 '{path}' PDF파일을 '{lecture}'과목을 업로드했습니다.")
                    else:
                        printError(f"'{path}' PDF파일을 '{lecture}'과목에 업로드하는데 실패했습니다.")
                
                case "SendDataWav":
                    ssp = sp[1].split(p2)
                    isSucceed = True if ssp[0] == str(True) else False
                    lecture = ssp[1]
                    path = ssp[2]
                    
                    if isSucceed :
                        printSucceed(f"성공적으로 '{path}' 음성 파일을 '{lecture}'과목을 업로드했습니다.")
                    else:
                        printError(f"'{path}' 음성 파일을 '{lecture}'과목에 업로드하는데 실패했습니다.")
                
                case "SendDataTxt": 
                    ssp = sp[1].split(p2)
                    isSucceed = True if ssp[0] == str(True) else False
                    lecture = ssp[1]
                    path = ssp[2]
                    
                    if isSucceed :
                        printSucceed(f"성공적으로 '{path}' TXT파일을 '{lecture}'과목을 업로드했습니다.")
                    else:
                        printError(f"'{path}' TXT파일을 '{lecture}'과목에 업로드하는데 실패했습니다.")
                
                case "SendDataPpt": 
                    ssp = sp[1].split(p2)
                    isSucceed = True if ssp[0] == str(True) else False
                    lecture = ssp[1]
                    path = ssp[2]
                    
                    if isSucceed :
                        printSucceed(f"성공적으로 '{path}' PPT파일을 '{lecture}'과목을 업로드했습니다.")
                    else:
                        printError(f"'{path}' PPT파일을 '{lecture}'과목에 업로드하는데 실패했습니다.")
                
                case "FineTuneCreate":
                    ssp = sp[1].split(p2)
                    isSucceed = True if ssp[0] == str(True) else False
                    lecture = ssp[1]
                    
                    if isSucceed :
                        asyncio.run(subsio.emit("FineTuneStart",data=True,to=lecture))
                        printSucceed(f"'{lecture}'과목의 파인튜닝이 시작됐습니다.")
                        
                    else:
                        asyncio.run(subsio.emit("FineTuneStart",data=False,to=lecture))
                        printSucceed(f"'{lecture}'과목의 파인튜닝이 정상적으로 시작되지 않았습니다. AI 프로세스를 확인해주십시오.")
                
                case "FineTuneEnd" : 
                    ssp = sp[1].split(p2)
                    isSucceed = True if ssp[0] == str(True) else False
                    lecture = ssp[1]
                    
                    if isSucceed :
                        asyncio.run(subsio.emit("FineTuneEnd",data=True,to=lecture))
                        printSucceed(f"성공적으로 '{lecture}'과목의 파인튜닝이 끝났습니다.")
                    else:
                        asyncio.run(subsio.emit("FineTuneEnd",data=False,to=lecture))
                        printSucceed(f"'{lecture}'과목의 파인튜닝이 비정상적인 방법으로 종료됐습니다. AI 프로세스를 확인해주십시오.")
                
                case "GetModel":
                    ssp = sp[1].split(p2)
                    lecture = ssp[0]
                    modelName = ssp[1]
                    
                    printSucceed(f"'{lecture}'과목은 현재 '{modelName}' 모델을 사용 중입니다.")
                
                case "SessionDelete": 
                    ssp = sp[1].split(p2)
                    isSucceed = True if ssp[0] == str(True) else False
                    sid = ssp[1]
                    lecture = ssp[2]
                
                    if isSucceed :
                        printSucceed(f"성공적으로 '{sid}'사용자의 '{lecture}' 과목 세션이 삭제됐습니다.")
                    else:
                        printSucceed(f"'{sid}'사용자의 '{lecture}' 과목 세션을 삭제하는데에 실패했습니다.")
                
                case "GetAnswer": 
                    ssp = sp[1].split(p2)
                    sid = ssp[0]
                    lecture = ssp[1]
                    answer = ssp[2]
                    is_filepath_exist=ssp[3]
                    filepath =  None
                    if is_filepath_exist == "None":
                       
                        filepath = None  
                        # ppt 파일 슬라이드 경로가없다 # none
                    else:
                        filepath  = is_filepath_exist
                        # 외에는 해당 변수가 경로

                    if filepath is not None:
                        asyncio.run(send_file(filepath=filepath,target_sid=sid))

                    printSucceed(f"['{sid}' 사용자의 '{lecture}' 응답] : {answer}")
                    asyncio.run(subsio.emit('GetAnswer', data= answer,to= sid))
                    print("emit  성공")
                  
                case _:
                    if flag == "" : return;
            
                    printWarning(f"""'{flag}'는 유효한 패킷 타입이 아닙니다. reciecve : {packet}""")
            

        except Exception as ex:
            printError(f"소켓 통신 중 예외가 발생했습니다! {ex}\n{ex.with_stacktrace().format_exc()}")
            
   

    # 프로세스 로드 함수
    def __LoadAiProcess__(self) :
        
        server = self.server
        
        def LoadAiThread (server : Server) :
            printProcess("AI 프로세스를 로드 중입니다. 잠시만 기다려 주십시오...")
            
            # AI 프로세스를 새로운 창에서 실행.
            program_path = GlobalReference.cmdProcessPath
            subprocess.Popen(["python", program_path], creationflags=subprocess.CREATE_NEW_CONSOLE)

            # AI 프로세스가 기동할 때까지 대기
            while self.clientIsAvailable == False : pass
            printProcess("AI 프로세스가 로드되었습니다!")
        
        def InitAiThread (server : Server) :
            while True :
            
                if len(server.clients) != 0 or self.clientIsAvailable == False :
                    time.sleep(1.0);
                    continue
            
                self.clientIsAvailable = False
                server.clients = [];
            
                printError("AI 프로세스의 비정상적인 연결 종료가 발생했습니다.")
                printError("AI 프로세스를 다시 실행합니다. 프로그램을 종료하려면 서버를 먼저 종료하십시오.")
                self.loadAiThread = threading.Thread(target= LoadAiThread, args=[server])
                self.loadAiThread.start()
    
        self.loadAiThread = threading.Thread(target= LoadAiThread, args= [server])
        self.loadAiThread.start()
        self.initAiThread = threading.Thread(target= InitAiThread, args= [server])
        self.initAiThread.start()
    
        # AI 프로세스가 기동할 때까지 대기
        while self.clientIsAvailable == False : pass
    
    # 디버그용 기능 체크
    # def ExecuteDebugCode(self) : 
        
    #     printNor("테스트 코드로 기능을 확인을 시작합니다...")
        
    #     # 경로
    #     user_documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
    #     saveDirectory = "WB38\\Lectures"
    #     rootPath = f"{user_documents_path}\\{saveDirectory}"
        
    #     # 테스트용 빈 PDF
    #     from reportlab.pdfgen import canvas
    #     pdfPath = f"{rootPath}\\empty_pdf.pdf"
    #     c = canvas.Canvas(pdfPath)
    #     c.save()
        
    #     printProcess(f"빈 PDF 파일이 {pdfPath} 경로에 생성되었습니다.")

    #     # 테스트용 빈 TXT
    #     txtPath = f"{rootPath}\\empty_txt.txt"
    #     with open(txtPath, "w", encoding="utf-8") as file :
    #         file.write("asdadsa");
        
    #     printProcess(f"빈 TXT 파일이 {txtPath} 경로에 생성되었습니다.")

    #     # 기타 변수들을 짧게 처리
    #     p1 = self.p1
    #     p2 = self.p2
        
    #     server = self.server;
        
    #     # 실제 테스트 전송 시작

    #     self.DoLectureCreate("조현민의 나의 투쟁")
    #     time.sleep(1.0)
    #     self.DoLectureDelete("조현민의 나의 투쟁")
    #     time.sleep(1.0)
    #     self.DoLectureCreate("박상한의 케로로학")
    #     time.sleep(1.0)
    #     self.DoLectureList()
    #     time.sleep(1.0)
        
        
    #     self.DoGetModel("박상한의 케로로학")
    #     time.sleep(1.0)
    #     self.DoGetAnswer("1", "박상한의 케로로학", "C#에서 여러줄의 주석을 사용하는 방법에 대해 알려줘.")
    #     time.sleep(1.0)
    #     self.DoSessionDelete("1", "박상한의 케로로학")
    #     time.sleep(1.0)
    #     self.DoSendDataPdf("박상한의 케로로학", {pdfPath})
    #     time.sleep(1.0)
    #     self.DoSendDataTxt("박상한의 케로로학", {txtPath})
    #     time.sleep(1.0)
        
    #     #self.DoFineTuneCreate("박상한의 케로로학")
    #     time.sleep(1.0)
        
    #     printNor("테스트 코드로 기능을 확인을 마쳤습니다...")
        
    # 디버그용 Q and A
 
        
    def ExecuteTestQandA(self) :
        # 기타 변수들을 짧게 처리
        p1 = self.p1
        p2 = self.p2
        
        server = self.server;
        
        #간단한 질문과 응답
        sid = 0;
        lectureName = "박상한의 케로로학"
    
        while True :
            inputText = input(f"(sid : {sid})의 ({lectureName} 과목) 질문 : ")
            server.Send(f"GetAnswer{p1}{sid}{p2}{lectureName}{p2}{inputText}")
            sid+=1
        

    def DoLectureCreate(self, lecture : str) :
        # 기타 변수들을 짧게 처리
        p1 = self.p1
        p2 = self.p2
        server = self.server;
        
        server.Send(f"LectureCreate{p1}{lecture}")
        
    def DoLectureDelete(self, lecture : str) :
        # 기타 변수들을 짧게 처리
        p1 = self.p1
        p2 = self.p2
        server = self.server;
        
        server.Send(f"LectureDelete{p1}{lecture}")
        
    def DoLectureList(self) :
        # 기타 변수들을 짧게 처리
        p1 = self.p1
        p2 = self.p2
        server = self.server;
        
        server.Send(f"LectureList{p1}")

    def DoGetModel(self, lecture : str) :
        # 기타 변수들을 짧게 처리
        p1 = self.p1
        p2 = self.p2
        server = self.server;
        
        server.Send(f"GetModel{p1}{lecture}")
        
    def DoGetAnswer(self, sid : str, lecture : str, question : str) :
        # 기타 변수들을 짧게 처리
        p1 = self.p1
        p2 = self.p2
        server = self.server;
        
        server.Send(f"GetAnswer{p1}{sid}{p2}{lecture}{p2}{question}")
        
    def DoSessionDelete(self, sid : str, lecture : str) :
        # 기타 변수들을 짧게 처리
        p1 = self.p1
        p2 = self.p2
        server = self.server;
        
        server.Send(f"SessionDelete{p1}{sid}{p2}{lecture}")
        
    def DoSendDataPdf(self, lecture : str, path : str) :
        # 기타 변수들을 짧게 처리
        p1 = self.p1
        p2 = self.p2
        server = self.server;
        
        server.Send(f"SendDataPdf{p1}{lecture}{p2}{path}")
        
    def DoSendDataTxt(self, lecture : str, path : str) :
        # 기타 변수들을 짧게 처리
        p1 = self.p1
        p2 = self.p2
        server = self.server;
        
        server.Send(f"SendDataTxt{p1}{lecture}{p2}{path}")
        
    def DoSendDataWav(self, lecture : str, path : str) :
        # 기타 변수들을 짧게 처리
        p1 = self.p1
        p2 = self.p2
        server = self.server;
        
        server.Send(f"SendDataWav{p1}{lecture}{p2}{path}")
    
    def DoSendDataPpt(self, lecture : str, path : str) :
        # 기타 변수들을 짧게 처리
        p1 = self.p1
        p2 = self.p2
        server = self.server;
        
        server.Send(f"SendDataPpt{p1}{lecture}{p2}{path}")

    def DoFineTuneCreate(self, lecture : str) :
        # 기타 변수들을 짧게 처리
        p1 = self.p1
        p2 = self.p2
        server = self.server;
        
        server.Send(f"FineTuneCreate{p1}{lecture}")