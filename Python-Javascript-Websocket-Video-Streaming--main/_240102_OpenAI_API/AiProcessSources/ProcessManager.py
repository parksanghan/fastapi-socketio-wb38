# -*- coding: cp949 -*-
import hashlib
import ctypes
import sys
import threading
from time import sleep

from ApiManager import OpenAiManagerV2
from SessionManager import SessionManagerV2
from FineTuneManager import FineTuneManager
from Addon.ServerAndClient import Server, Client

import GlobalReference 
from _240102_OpenAI_API.AiProcessSources.ApiManager import printError, printSucceed, printWarning

p1 = GlobalReference.PARSER[0]
p2 = GlobalReference.PARSER[1]



class ProcessManager() :
    def __init__ (self, sm : SessionManagerV2, api : OpenAiManagerV2, ft : FineTuneManager) : 
        
        self.sm  = sm;
        self.sm.pm = self;
        self.api = api
        self.api.pm = self;
        self.ft = ft
        self.ft.pm = self;
       
        self.ft.LecturesLoad();
        self.ft.__LoadFineTuneCheckPoint__();
        
        self.__InitClient__();
        
    def __del__(self) : 
        self.client.Send(f"ProcessEnd{p1}{str(True)}")
        self.ft.LecturesSave();
        sys.exit()
        
    def __InitClient__(self) : 
        
        ctypes.windll.kernel32.SetConsoleTitleW("AiEnviormentTerminal")
        
        # 클라이언트 생성
        self.client : Client = Client("127.0.0.1", 4090, self.__ClientDel__)
    
        # 클라이언트 연결
        self.client.Connect()
    
        # 클라이언트가 입력 받을 준비가 되었다고 전송
        self.client.Send(f"ProcessStart{p1}")
        
    def __ClientDel__(self, packet) :
        
        sp = packet.split(p1)
        flag = sp[0]
        try : 
            match flag: 
                case "ProcessStart": pass
            
                case "ProcessEnd ":
                    try :
                        del self
                    except :
                        self.client.Send(f"ProcessEnd{p1}{str(False)}")
                    
                case "LectureCreate":
                    ssp = sp[1].split(p2)
                    lecture = ssp[0]
                    ret = self.ft.LecturesCreate(lecture)
                
                    self.client.Send(f"LectureCreate{p1}{str(ret)}{p2}{lecture}")
            
                case "LectureDelete": 
                    ssp = sp[1].split(p2)
                    lecture = ssp[0]
                    ret = self.ft.LecturesDelete(lecture)
                
                    self.client.Send(f"LectureDelete{p1}{str(ret)}{p2}{lecture}")
                
                case "LectureList":
                    ssp = sp[1].split(p2)
                    lecList = self.ft.LecturesList()
                
                    sendPac = f"LectureList{p1}"
                    for lec in lecList : sendPac += f"{lec}{p2}"

                    self.client.Send(sendPac)
                
                case "SendDataPdf": 
                    ssp = sp[1].split(p2)
                    lecture = ssp[0]
                    path = ssp[1]
                    ret = self.ft.AddPdfData(lecture, path)
                
                    self.client.Send(f"SendDataPdf{p1}{str(ret)}{p2}{lecture}{p2}{path}")
                
                case "SendDataWav":
                    ssp = sp[1].split(p2)
                    lecture = ssp[0]
                    path = ssp[1]
                    
                    def thr () :
                        ret = self.ft.AddWavData(lecture, path)
                        self.client.Send(f"SendDataWav{p1}{str(ret)}{p2}{lecture}{p2}{path}")
                        

                    tu = threading.Thread(target=thr);
                    tu.start();
                
                case "SendDataPpt":
                    ssp = sp[1].split(p2)
                    lecture = ssp[0]
                    path = ssp[1]
                    
                    def thr () :
                        ret = self.ft.AddPptData(lecture, path)
                        self.client.Send(f"SendDataPpt{p1}{str(ret)}{p2}{lecture}{p2}{path}")
                        
                    tu = threading.Thread(target=thr);
                    tu.start();
                
                case "SendDataTxt": 
                    ssp = sp[1].split(p2)
                    lecture = ssp[0]
                    path = ssp[1]
                    ret = self.ft.AddRawData(lecture, path)
                
                    self.client.Send(f"SendDataTxt{p1}{str(ret)}{p2}{lecture}{p2}{path}")
                
                case "FineTuneCreate":
                    ssp = sp[1].split(p2)
                    lecture = ssp[0]
                    
                    ret = self.ft.StartFineTuneJob(lecture)
                
                    self.client.Send(f"FineTuneCreate{p1}{str(ret)}{p2}{lecture}")
                
                case "FineTuneEnd" : 
                    pass
                
                case "GetModel":
                    ssp = sp[1].split(p2)
                    lecture = ssp[0]
                    ret = self.ft.GetModel(lecture)
                
                    self.client.Send(f"GetModel{p1}{lecture}{p2}{ret}")
                
                case "SessionDelete": 
                    ssp = sp[1].split(p2)
                    sid = ssp[0]
                    lecture = ssp[1]
                    
                    ses = self.sm.GetSession(sid, lecture)
                    ret = ses.Remove()
                
                    self.client.Send(f"SessionDelete{p1}{str(ret)}{p2}{sid}{p2}{lecture}")
                
                case "GetAnswer": 
                    ssp = sp[1].split(p2)
                    sid = ssp[0]
                    lecture = ssp[1]
                    question = ssp[2]
                
                    def __callbackFun__(sid, lecture, answer) :
                        printSucceed(f"질문에 대한 답변 생성 ({sid}/{lecture}) \n[Quesetion] : {question} \n[Answer] : {answer}")
                        imgRoot : str = self.ft.FindSimilarity(lecture, question)                         

                        printSucceed(f"유사도 높은 이미지 ({sid}/{lecture}) \n[image] : {imgRoot}")
                        self.client.Send(f"GetAnswer{p1}{sid}{p2}{lecture}{p2}{answer}{p2}{'None' if imgRoot == None else imgRoot}")
                    
                    self.api.InitRequest(sid, lecture, question, callback=__callbackFun__)
            
                case _:
                    if flag == "" : return;
            
                    printWarning(f"""'{flag}'는 유효한 패킷 타입이 아닙니다. reciecve : {packet}""")
            

        except Exception as ex:
            printError(f"소켓 통신 중 예외가 발생했습니다! {ex}\n{ex.with_stacktrace().format_exc()}")
      
    def __DebugFunction__(self) : 
        self.api.PrintAllModels();
        self.ft.StartFineTuneChecker();
        
        # self.ft.LecturesLoad();
        # self.ft.LecturesCreate("B# 프로그래밍");
        # self.ft.LecturesLoad();
        # self.ft.LecturesDelete("B# 프로그래밍");
        # self.ft.LecturesCreate("박상한에 대해서");
        # self.ft.AddRawData("박상한에 대해서", "S:\\test.txt");
        # self.ft.__MakeDataSet__("박상한에 대해서", r"C:\Users\skyma\Documents\WB38\Lectures\C# 프로그래밍\RAW_DATA\test.txt")
        # self.ft.LecturesSave();

        # self.ft.LecturesCreate("C# 프로그래밍");
        # # self.ft.AddPdfData("C# 프로그래밍", "S:\\test_pdf.pdf");
        # self.ft.__MakeDataSet__("C# 프로그래밍", r"C:\Users\skyma\Documents\WB38\Lectures\C# 프로그래밍\RAW_DATA\test_pdf_mm2.txt")
        # self.ft.LecturesSave();
        # self.ft.__MergeDataSet__("C# 프로그래밍")
        # self.api.UploadFile("C# 프로그래밍")
        
        # self.ft.StartFineTuneJob("C# 프로그래밍")
        
        # self.api.DeleteFineTuneModel(self.ft.modelLib["C# 프로그래밍"]);

        # self.api.DeleteFineTuneModel("ft:gpt-3.5-turbo-1106:personal::8fN4DBXe");
        
        # self.api.InitRequest(1, "C# 프로그래밍", "C#의 주석 기능에 대해 설명해줘.",
        #                      lambda sid, lecture, response : print(f"[{str(sid)}번 사용자의 '{lecture}' 과목에 대한 질문에 대한 응답] : {response}"))
        
        # self.api.InitRequest(2, "C# 프로그래밍", "미안, 내가 뭐라고 했는지 깜빡했는데 다시 보내줄래?",
        #                      lambda sid, lecture, response : print(f"[{str(sid)}번 사용자의 '{lecture}' 과목에 대한 질문에 대한 응답] : {response}"))
        
        # self.api.InitRequest(3, "C# 프로그래밍", "미안, 내가 뭐라고 했는지 깜빡했는데 다시 보내줄래?",
        #                      lambda sid, lecture, response : print(f"[{str(sid)}번 사용자의 '{lecture}' 과목에 대한 질문에 대한 응답] : {response}"))
        
        # self.api.InitRequest(4, "C# 프로그래밍", "C#의 주석 기능에 대해 설명해줘.",
        #                      lambda sid, lecture, response : print(f"[{str(sid)}번 사용자의 '{lecture}' 과목에 대한 질문에 대한 응답] : {response}"))

if __name__ == "__main__":
    pm : ProcessManager = ProcessManager(SessionManagerV2(), OpenAiManagerV2(), FineTuneManager())
    # pm.ft.StartFineTuneJob("C# 프로그래밍")
    # print(pm.ft.__CheckFineTuneAvailable__("C# 프로그래밍"))
    # print(pm.ft.__CheckFineTuneAvailable__("박상한의 케로로학"))
    while True : sleep(1.)



