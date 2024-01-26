 
from email.mime import nonmultipart
import json,os, threading
from time import sleep

import openai
from openai import OpenAI
from openai.pagination import SyncCursorPage, SyncPage
from openai.types import FileObject
from openai.types.chat import ChatCompletion

from SessionManager import Session, SessionManagerV2

from Addon.CustomConsolePrinter import printError, printNor, printProcess, printSucceed, printWarning

# OpenAI API�� �ٷ�� �۾��� �ϴ� ������ ��ü�Դϴ�.
# Q&A �۾��̳� ���� Ʃ��, �� ���� ���� �κ��� ����մϴ�.
class OpenAiManagerV2 :
    def __init__(self) :
        self.pm = None;
        self.client = OpenAI();
        
    # ���� ��û ������
    def __NormalRequestResponse__(self, sid : str, lectureName : str, requestQuestion : str, callback):
        
        waitedEnough = False;

        #API ��û
        try :
            #���� �Ŵ��� ��������
            sessionManager : SessionManagerV2 = self.pm.sm;
                
            #���� ��������
            sessionPrevious : Session = sessionManager.GetSession(sid, lectureName)
            
            # ���� ���� ������ ���� ��ȿ���� ���� > ���� ���� ��? ������ ������?
            if not sessionPrevious.GetLastRole() in ["assistant", "system"] :
                if waitedEnough == False :
                    waitedEnough = True
                    raise Exception("�亯�� �ޱ� ���� ���� ������ �õ��ϰ� �ֽ��ϴ�. 5�� ��, �ٽ� �õ��մϴ�. ErrorCode : 697")
                else :
                    printError("��⸦ �������� ������ ������ �亯�� ��� ���Դϴ�. �̴� ���� ������ ������ ��Ÿ�� ���� �ֽ��ϴ�. ������ ������ ������ �ذ��� ���� �ֽ��ϴ�.")
                    callback(sid, lectureName, "��û ���� : ������ ������ �亯�� ��� ���Դϴ�. �̴� ���� ������ ������ ��Ÿ�� ���� �ֽ��ϴ�. ������ ������ ������ �ذ��� ���� �ֽ��ϴ�. ErrorCode : 697")
                    return
                    
            
            # �� �̸� ��������
            modelName = self.pm.ft.GetModel(lectureName)
                
            # ���ǿ� ����� ���� �߰�
            sessionPrevious.Append("user", requestQuestion)
                
            # API ��û
            completion : ChatCompletion = self.client.chat.completions.create(
                        model= modelName,
                        temperature=0.4,
                        messages = sessionPrevious.GetData(),
                        # max_tokens= 4000,
                        # frequency_penalty= 0.3,
                        # presence_penalty= 0.3,
                    )
            
            responseAnswer = completion.choices[0].message.content
                
            # ���ǿ� AI �亯 �߰�
            sessionPrevious.Append("assistant", responseAnswer)
            sessionPrevious.Save()
            
        except openai.BadRequestError as ex:
            print(f"���ܹ߻� BadRequestError : {ex}");
            responseAnswer = ex  
            print(ex.__traceback__.format_exc())
        except Exception as ex:
            print(f"���ܹ߻� Exception : {ex}");
            
            # �ʹ� ���� ��û ��, ���� �� �ٽ� ����.
            if(str(ex).__contains__("429") or str(ex).__contains__("697")) :
                printWarning("ª�� �ð� ���� �ʹ� ���� ��û�� �õ��ϰ� �ֽ��ϴ�. 5�� �� �ٽ� �����մϴ�...")
                sleep(5.)
                self.__NormalRequestResponse__(sid, lectureName, requestQuestion, callback)
                return
            
            # ���� ã�� �� ���� ��, �⺻ �𵨷� ���� 
            elif(str(ex).__contains__("404")) :
                if(str(ex).__contains__("model_not_found")) :
                    printError("�ش� ������ ���� ���̻� �������� �ʰų� ��ȿ���� �ʽ��ϴ�! �ش� ������ ���� �𵨷� �ʱ�ȭ�մϴ�...")
                    import FineTuneManager
                    ft : FineTuneManager.FineTuneManager = self.pm.ft;
                    ft.modelLib[lectureName] = None;
                    ft.LecturesSave()
                    self.__NormalRequestResponse__(sid, lectureName, requestQuestion, callback)
                    return
            
            responseAnswer = ex
            print(ex.__traceback__.format_exc())
            
        callback(sid, lectureName, responseAnswer)
    
    # ���� ��û
    def InitRequest(self, sid : str, lectureName : str, requestQuestion : str, callback) : # callback = Action<string sid, string msg>
        thread_instance = threading.Thread(
            target=self.__NormalRequestResponse__,
            args=(sid, lectureName, requestQuestion, callback)
        )
        thread_instance.start();
    

    # �����ͼ� ��û ������
    def __DatasetRequestResponse__(self, lectureName : str, lectureData : str, callback):
        
        datasetRequest = f"���ϴ� '{lectureName}'��� ���� ������ ���� �����̴�. \n\n{lectureData}" + """
        
�ش� ���� ������ ����� �������� ������ json �����ͷ� ��ȯ�϶�. �����ͼ��� �ڷ������� 'json'�̾���ϰ�, �����ͼ��� ����� ������ ����.

# ������ ����

```json
[
    {"messages": [{"role": "system", "content": "�л����� ���� ���ظ� ���� ê��."}, {"role": "user", "content": "�������� ������ ����ΰ�?"}, {"role": "assistant", "content": "'�ĸ�'��� �����Դϴ�."}]}
    {"messages": [{"role": "system", "content": "�л����� ���� ���ظ� ���� ê��."}, {"role": "user", "content": "�ι̿��� �ٸ����� �۾��̴� �����ΰ�?"}, {"role": "assistant", "content": "'������ ���ͽ��Ǿ�'��� �Ҽ����Դϴ�."}]}
    {"messages": [{"role": "system", "content": "�л����� ���� ���ظ� ���� ê��."}, {"role": "user", "content": "������ ���� �󸶳� �ָ� ������ �ִ°�?"}, {"role": "assistant", "content": "384,400 ų�ι��� ���� ������ �ֽ��ϴ�."}]}
]
```
        
���� ���� ������ �����ʹ� �Ʒ��� ���� ����� �����ϸ� "content"Ű�� ���� �����ϰ��� ��� ��ġ�ؾ� �Ѵ�.

�˾���? list[dict[str, list[dict[str, str]]]]�� ������ ���Ѽ� ���� ������ �������� �������� ������ �����͵��� ��������.

'messages' ����Ʈ�� ���� ��Ҵ� �� �����̸� ������ 'role'�� ���� 'system', 'user', 'assistant'���߸���.

[
    {
    "messages" :
        [
            {
                "role": "system",
                "content": "�л����� ���� ���ظ� ���� ê��."
            },
            {
                "role": "user",
                "content": "�������� ������ ����ΰ�?"
            },
            {
                "role": "assistant",
                "content": "'�ĸ�'��� �����Դϴ�."
            }
            
        ]
    }
]
        
�亯���� �����͸� 5�� �̻����� ��ȯ�϶�. �亯�� �ִ��� ������ �������� ����.
        """
        
        datasetResponse  = ""
        datasetReturn  = []

        datasetSession = []
        datasetSession.append({
                                "role" : "system",
                                "content" : "�ʴ� �������� ���� �ڷḦ �м��ϰ� AI�� �н� �ϱ� ���� ����ϴ� �����ͼ��� ��ȯ�ؾ��ϴ� ����̾�."
                            })
        
        datasetSession.append({
                                "role" : "system",
                                "content" : """
����ڰ� ���� ������ ���� ������ ���� ������ �ش� ���� ������ �����ͼ����� ��ȯ�ؼ� ����ؾ���.
��µǴ� �������� ���� �ּ� 10�� ������ ����������. ��, �߿��� �����Ͱ� ������ ��ŭ ����� �ȵǰ�, �ʹ� ���� �����Ͱ� ���ʿ��ϰ� �����Ǿ�� �ȵ�. ��ü���� ������ ���� ���ϴ� ���� �� �Ǵܿ� �ñ沲. 

����, ����ڰ� �Է��� ���� �� ���� ������ ������ ���� �κ��� ��������.
���ø� ��� �������ڸ�, 'C# ��ü ���� ���α׷���'�̶�� �����̶��, OOP ������ ���� ������ ��� ���信 ���� �̾߱�� �� �����ͷ� ����������. ������ ������ ���� �޴��� ����, ��� ȸ���� ��Ʈ���� �� ������ ���� ������ �����ͷ� ���� �ʿ䰡 ����. �װ͵��� ���� ������ ��� �����̴ϱ�.

�װ� �������� ���� ��� �������� ���׵� ��������.
���ø� ��� �������ڸ�, '1.2.4 Main'�� '1.2.5 Console.WriteLine'�� ������������ �߿䵵�� ���� ���׿� ���� �� �𸣰ڴٸ� �ش� �κп� ���� ó���� �ǳʶپ ����.

�����ͼ��� �ڷ������� 'json'�̾���ϰ�, �����ͼ��� ����� ������ ����.

# ������ ����

```json
[
    {"messages": [{"role": "system", "content": "�л����� ���� ���ظ� ���� ê��."}, {"role": "user", "content": "�������� ������ ����ΰ�?"}, {"role": "assistant", "content": "'�ĸ�'��� �����Դϴ�."}]}
    {"messages": [{"role": "system", "content": "�л����� ���� ���ظ� ���� ê��."}, {"role": "user", "content": "�ι̿��� �ٸ����� �۾��̴� �����ΰ�?"}, {"role": "assistant", "content": "'������ ���ͽ��Ǿ�'��� �Ҽ����Դϴ�."}]}
    {"messages": [{"role": "system", "content": "�л����� ���� ���ظ� ���� ê��."}, {"role": "user", "content": "������ ���� �󸶳� �ָ� ������ �ִ°�?"}, {"role": "assistant", "content": "384,400 ų�ι��� ���� ������ �ֽ��ϴ�."}]}
]
```

"""
                            })

        datasetSession.append({
                                "role" : "user",
                                "content" : str(datasetRequest)
                            })

        count = 0;
        
        #API
        try :
            while True :
                # ������ ���� GPT���� ������ �޼���
                restoreMessage : str = ""
                datasetString : str = ""
                
                # ���� ���� Ż�� �ڵ�
                count += 1
                printNor(f"�ݺ� Ƚ�� : {count}")
                if(count > 10) :
                    printError("���������� �ݺ� �߻�. �ش� ��û ��ȸ�� ����ϴ�.")
                    break;
                
                #API�� �亯�� ��û
                completion : ChatCompletion = self.client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    temperature=0.7,
                    messages = datasetSession,
                    max_tokens= 4000,
                    frequency_penalty= 0.3,
                    presence_penalty= 0.3,
                )

                #��ȯ�� ���ڿ��� ����
                datasetResponse = completion.choices[0].message.content
                
                # json �Ľ� �˼�
                sp = datasetResponse.split("```json")
                if(len(sp) == 2 ) :
                    datasetString = sp[1].split("```")[0];
                else : 
                    printError(f"```json�� �������� �ʾ� �Ľ̿� �����߽��ϴ�.")
                    restoreMessage = """
�װ� ����� ���ڿ����� ��ȿ�� json������ ����. ������ ������ ��Ŀ� �°� �ٽ� ����϶�. �� �޼����� �������� �����ͼ��� ��µ� ������ �ݺ��ȴ�.
                                
# ������ ����

```json
[
    {"messages": [{"role": "system", "content": "�л����� ���� ���ظ� ���� ê��."}, {"role": "user", "content": "�������� ������ ����ΰ�?"}, {"role": "assistant", "content": "'�ĸ�'��� �����Դϴ�."}]}
    {"messages": [{"role": "system", "content": "�л����� ���� ���ظ� ���� ê��."}, {"role": "user", "content": "�ι̿��� �ٸ����� �۾��̴� �����ΰ�?"}, {"role": "assistant", "content": "'������ ���ͽ��Ǿ�'��� �Ҽ����Դϴ�."}]}
    {"messages": [{"role": "system", "content": "�л����� ���� ���ظ� ���� ê��."}, {"role": "user", "content": "������ ���� �󸶳� �ָ� ������ �ִ°�?"}, {"role": "assistant", "content": "384,400 ų�ι��� ���� ������ �ֽ��ϴ�."}]}
]```
                          """
                          
                # �ڷᱸ�� �˼�
                try :
                    if(datasetString != "") :
                        dataSets : list = json.loads(datasetString.strip().replace('\n', ''))
                        
                        for dataSet in dataSets :
                            dataSet["messages"][0]["role"] 
                            dataSet["messages"][0]["content"] 
                            dataSet["messages"][1]["role"] 
                            dataSet["messages"][1]["content"] 
                            dataSet["messages"][2]["role"] 
                            dataSet["messages"][2]["content"] 
                            len(dataSet["messages"])
                            if(len(dataSet["messages"]) > 3) : raise Exception("�� �������� ���̴� 3������ �մϴ�. ���� ������ �����ʹ� 3������ �����Ƿ� json�� �ٽ� �����ؾ��մϴ�.")
                            
                            if(dataSet["messages"][1]["content"].__contains__("�ι̿��� �ٸ���")) : raise Exception("������ �־��� ���� ������ ����ؼ� ���ο� json�� �����ϼ���. ����� ������ �� ������ �״�� ������⿡ ������ �߻��߽��ϴ�.")
                        
                        # ��ȯ
                        datasetReturn = dataSets
                
                except Exception as ex:
                    printError(ex)
                    restoreMessage =  f"""
���� �߻� : {ex.args} {ex}
""" + """
�װ� ���� �����͸� json���� �Ľ��ϴµ����� ����������, �ڷᱸ���� ��ġ���� �ʾ�.
                                

������ �����ʹ� �Ʒ��� ���� ����� �����ϸ� "content"Ű�� ���� �����ϰ��� ��� ��ġ�ؾ� ��. �װ� ������ �����͸� �ٽ� Ȯ���ϰ� ��Ŀ� �°� �����ؼ� ���� ���� ����� �ٽ� ������.
[      
    {
    "messages" :
        [
            {
                "role": "system",
                "content": "�л����� ���� ���ظ� ���� ê��."
            },
            {
                "role": "user",
                "content": "�������� ������ ����ΰ�?"
            },
            {
                "role": "assistant",
                "content": "'�ĸ�'��� �����Դϴ�."
            }
            
        ]
    }
]

�˾���? list[dict[str, list[dict[str, str]]]]�� ������ ���Ѽ� ���� ������ �������� �������� ������ �����͵��� ��������.

'messages' ����Ʈ�� ���� ��Ҵ� �� �����̸� ������ 'role'�� ���� 'system', 'user', 'assistant'���߸���.

```json
[
    {"messages": [{"role": "system", "content": "�л����� ���� ���ظ� ���� ê��."}, {"role": "user", "content": "�������� ������ ����ΰ�?"}, {"role": "assistant", "content": "'�ĸ�'��� �����Դϴ�."}]}
    {"messages": [{"role": "system", "content": "�л����� ���� ���ظ� ���� ê��."}, {"role": "user", "content": "�ι̿��� �ٸ����� �۾��̴� �����ΰ�?"}, {"role": "assistant", "content": "'������ ���ͽ��Ǿ�'��� �Ҽ����Դϴ�."}]}
    {"messages": [{"role": "system", "content": "�л����� ���� ���ظ� ���� ê��."}, {"role": "user", "content": "������ ���� �󸶳� �ָ� ������ �ִ°�?"}, {"role": "assistant", "content": "384,400 ų�ι��� ���� ������ �ֽ��ϴ�."}]}
]
```

"""

                # ���� ��û�ϴ� ������ ���ǿ� �߰�����.
                if(restoreMessage != "" or datasetReturn == None) :
                    datasetSession.append({
                                "role" : "assistant",
                                "content" : datasetResponse
                            })
                    datasetSession.append({
                                "role" : "user",
                                "content" : restoreMessage
                            })
                else : break;
        
        except openai.BadRequestError as ex:
            print(f"���ܹ߻� BadRequestError : {ex}");
            datasetResponse = ex  
        except Exception as ex:
            print(f"���ܹ߻� Exception : {ex}");
            datasetResponse = ex
            
            if(str(ex).__contains__("429")) :
                sleep(5.)
                self.__DatasetRequestResponse__(lectureName, lectureData, callback)
                return
            
        callback(datasetReturn)
        
    # �����ͼ� ��û
    def InitDataSet(self, lectureName : str, filePath : str) : # callback = Action<string msg>
        
        self.dataSetBuffer : list[str] = list[str]()

        #���ڿ� ������
        rawDataSep = 1000;
        rawDataList = self.__readSplit__(filePath, rawDataSep)
        
        with open(filePath, "r", encoding = "utf-8") as file :
            printProcess(f"GPT�� �̿��� �ο� �����Ϳ��� �����ͼ��� �����մϴ�... ���� ũ�� : {len(file.read())}��")
            printProcess(f"���� ûũ ���� : {rawDataSep}�� / ûũ ���� : {len(rawDataList)}")
            

        # ������� ���ÿ� �������� ��û
        thrList : list[threading.Thread] = list[threading.Thread]()
        for rawData in rawDataList :
            thread_instance = threading.Thread(
                target=self.__DatasetRequestResponse__,
                args=(lectureName, rawData,
                            lambda msg : {
                                self.dataSetBuffer.append(msg),
                                printProcess(f"�����ͼ� ���� �� {len(self.dataSetBuffer)}/{len(rawDataList)}\n{msg}")
                                }
                      )
            )
            thread_instance.start();
            thrList.append(thread_instance);
            sleep(5.);
        
        # ��� ��û�� ���� ������ ��ٸ���
        for thr in thrList : 
            thr.join()
            
        
        # list[str] > dataSet
        retBuffer : list = []
        for dataSetList in self.dataSetBuffer :
            for dataSet in dataSetList :
                retBuffer.append(dataSet)
                 

        printSucceed(f"�����ͼ� ���� �Ϸ�! ������ ������ �� : {len(retBuffer)}��")
        return retBuffer
        

    # ���Ͽ��� �ؽ�Ʈ�� ûũ�� �߶� ����Ʈ�� ������
    def __readSplit__(self, file_path, chunkSize):
        result_list = []
        chunk = "-"

        with open(file_path, 'r', encoding='utf-8') as file:
            while chunk != "":
                chunk = file.read(chunkSize)
                result_list.append(chunk)
        return result_list
   
    # openai api�� ���� ���ε�
    def UploadFile(self, lecture) : 
        try :
            user_documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            saveDirectory = "WB38\\Lectures"
            path = rf"{user_documents_path}\{saveDirectory}\{lecture}\MERGED_DATASET\{lecture}_MERGED.jsonl"        
        
            printProcess(f"{lecture} ������ ���� �����͸� ���ε��մϴ�... Path : {path}")
            fo : FileObject = openai.files.create(
                file = open(path, "rb"),
                purpose = "fine-tune"
            )
            printProcess(f"{lecture} ������ ���� �����͸� ���ε带 �Ϸ��߽��ϴ�!")
            
            return fo
        
        except Exception as ex :
            print(ex);
            return None

    # �������� ���� Ʃ�� ��� ���ε�� ���ϵ��� ��ȸ
    def GetFineTuneData(self) : 
        ftJobs : SyncCursorPage =  openai.fine_tuning.jobs.list(limit=20)
        files : SyncPage[FileObject] = openai.files.list()
        return ftJobs, files
    
    # ����Ʃ�� ���� ������.
    def DeleteFineTuneModel(self, modelName) :
        printSucceed(f"��(id : {modelName})�� �����ϴµ� �����߽��ϴ�.")
        try : self.client.models.delete(modelName)
        except : pass
        # openai.models.delete(modelName)

    # openai api���� ��� ������ ��� ���� ��ȸ
    def PrintAllModels(self) :
        for a in self.client.models.list().data : print(a.id)
            
