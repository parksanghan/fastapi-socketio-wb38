 
import hashlib
import ctypes
import sys
import threading
from time import sleep

from ApiManager import OpenAiManagerV2
from SessionManager import SessionManagerV2
from FineTuneManager import FineTuneManager
from Addon.ServerAndClient import Server, Client

import GlobalReference as GlobalReference
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
        
        # Ŭ���̾�Ʈ ����
        self.client : Client = Client("127.0.0.1", 4090, self.__ClientDel__)
    
        # Ŭ���̾�Ʈ ����
        self.client.Connect()
    
        # Ŭ���̾�Ʈ�� �Է� ���� �غ� �Ǿ��ٰ� ����
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
                        printSucceed(f"������ ���� �亯 ���� ({sid}/{lecture}) \n[Quesetion] : {question} \n[Answer] : {answer}")
                        self.client.Send(f"GetAnswer{p1}{sid}{p2}{lecture}{p2}{answer}")
                    
                    self.api.InitRequest(sid, lecture, question, callback=__callbackFun__)
            
                case _:
                    if flag == "" : return;
            
                    printWarning(f"""'{flag}'�� ��ȿ�� ��Ŷ Ÿ���� �ƴմϴ�. reciecve : {packet}""")
            

        except Exception as ex:
            printError(f"���� ��� �� ���ܰ� �߻��߽��ϴ�! {ex}\n{ex.with_stacktrace().format_exc()}")
      
    def __DebugFunction__(self) : 
        self.api.PrintAllModels();
        self.ft.StartFineTuneChecker();
        
        # self.ft.LecturesLoad();
        # self.ft.LecturesCreate("B# ���α׷���");
        # self.ft.LecturesLoad();
        # self.ft.LecturesDelete("B# ���α׷���");
        # self.ft.LecturesCreate("�ڻ��ѿ� ���ؼ�");
        # self.ft.AddRawData("�ڻ��ѿ� ���ؼ�", "S:\\test.txt");
        # self.ft.__MakeDataSet__("�ڻ��ѿ� ���ؼ�", r"C:\Users\skyma\Documents\WB38\Lectures\C# ���α׷���\RAW_DATA\test.txt")
        # self.ft.LecturesSave();

        # self.ft.LecturesCreate("C# ���α׷���");
        # # self.ft.AddPdfData("C# ���α׷���", "S:\\test_pdf.pdf");
        # self.ft.__MakeDataSet__("C# ���α׷���", r"C:\Users\skyma\Documents\WB38\Lectures\C# ���α׷���\RAW_DATA\test_pdf_mm2.txt")
        # self.ft.LecturesSave();
        # self.ft.__MergeDataSet__("C# ���α׷���")
        # self.api.UploadFile("C# ���α׷���")
        
        # self.ft.StartFineTuneJob("C# ���α׷���")
        
        # self.api.DeleteFineTuneModel(self.ft.modelLib["C# ���α׷���"]);

        # self.api.DeleteFineTuneModel("ft:gpt-3.5-turbo-1106:personal::8fN4DBXe");
        
        # self.api.InitRequest(1, "C# ���α׷���", "C#�� �ּ� ��ɿ� ���� ��������.",
        #                      lambda sid, lecture, response : print(f"[{str(sid)}�� ������� '{lecture}' ���� ���� ������ ���� ����] : {response}"))
        
        # self.api.InitRequest(2, "C# ���α׷���", "�̾�, ���� ����� �ߴ��� �����ߴµ� �ٽ� �����ٷ�?",
        #                      lambda sid, lecture, response : print(f"[{str(sid)}�� ������� '{lecture}' ���� ���� ������ ���� ����] : {response}"))
        
        # self.api.InitRequest(3, "C# ���α׷���", "�̾�, ���� ����� �ߴ��� �����ߴµ� �ٽ� �����ٷ�?",
        #                      lambda sid, lecture, response : print(f"[{str(sid)}�� ������� '{lecture}' ���� ���� ������ ���� ����] : {response}"))
        
        # self.api.InitRequest(4, "C# ���α׷���", "C#�� �ּ� ��ɿ� ���� ��������.",
        #                      lambda sid, lecture, response : print(f"[{str(sid)}�� ������� '{lecture}' ���� ���� ������ ���� ����] : {response}"))

if __name__ == "__main__":
    pm : ProcessManager = ProcessManager(SessionManagerV2(), OpenAiManagerV2(), FineTuneManager())
    # pm.ft.StartFineTuneJob("C# ���α׷���")
    # print(pm.ft.__CheckFineTuneAvailable__("C# ���α׷���"))
    # print(pm.ft.__CheckFineTuneAvailable__("�ڻ����� �ɷη���"))
    while True : sleep(1.)



