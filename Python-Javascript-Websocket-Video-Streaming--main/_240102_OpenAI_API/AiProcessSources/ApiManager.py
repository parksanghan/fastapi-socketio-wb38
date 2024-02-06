# -*- coding: cp949 -*-
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

# OpenAI API를 다루는 작업을 하는 관리자 객체입니다.
# Q&A 작업이나 파인 튜닝, 모델 관리 같은 부분을 담당합니다.
class OpenAiManagerV2 :
    def __init__(self) :
        self.pm = None;
        self.client = OpenAI();
        
    # 질문 요청 스레드
    def __NormalRequestResponse__(self, sid : str, lectureName : str, requestQuestion : str, callback):
        
        waitedEnough = False;

        #API 요청
        try :
            #세션 매니저 가져오기
            sessionManager : SessionManagerV2 = self.pm.sm;
                
            #세션 가져오기
            sessionPrevious : Session = sessionManager.GetSession(sid, lectureName)
            
            # 세션 가장 마지막 단이 유효하지 않음 > 아직 질문 중? 오염된 데이터?
            if not sessionPrevious.GetLastRole() in ["assistant", "system"] :
                if waitedEnough == False :
                    waitedEnough = True
                    raise Exception("답변을 받기 전에 재차 질문을 시도하고 있습니다. 5초 뒤, 다시 시도합니다. ErrorCode : 697")
                else :
                    printError("대기를 헀음에도 세션이 여전히 답변을 대기 중입니다. 이는 세션 파일의 오염을 나타낼 수도 있습니다. 세션을 삭제해 문제를 해결할 수도 있습니다.")
                    callback(sid, lectureName, "요청 실패 : 세션이 여전히 답변을 대기 중입니다. 이는 세션 파일의 오염을 나타낼 수도 있습니다. 세션을 삭제해 문제를 해결할 수도 있습니다. ErrorCode : 697")
                    return
                    
            
            # 모델 이름 가져오기
            modelName = self.pm.ft.GetModel(lectureName)
                
            # 세션에 사용자 질문 추가
            sessionPrevious.Append("user", requestQuestion)
                
            # API 요청
            completion : ChatCompletion = self.client.chat.completions.create(
                        model= modelName,
                        temperature=0.4,
                        messages = sessionPrevious.GetData(),
                        # max_tokens= 4000,
                        # frequency_penalty= 0.3,
                        # presence_penalty= 0.3,
                    )
            
            responseAnswer = completion.choices[0].message.content
                
            # 세션에 AI 답변 추가
            sessionPrevious.Append("assistant", responseAnswer)
            sessionPrevious.Save()
            
        except openai.BadRequestError as ex:
            print(f"예외발생 BadRequestError : {ex}");
            responseAnswer = ex  
            print(ex.__traceback__.format_exc())
        except Exception as ex:
            print(f"예외발생 Exception : {ex}");
            
            # 너무 잦은 요청 시, 지연 후 다시 실행.
            if(str(ex).__contains__("429") or str(ex).__contains__("697")) :
                printWarning("짧은 시간 내에 너무 많은 요청을 시도하고 있습니다. 5초 후 다시 실행합니다...")
                sleep(5.)
                self.__NormalRequestResponse__(sid, lectureName, requestQuestion, callback)
                return
            
            # 모델을 찾을 수 없을 시, 기본 모델로 변경 
            elif(str(ex).__contains__("404")) :
                if(str(ex).__contains__("model_not_found")) :
                    printError("해당 과목의 모델이 더이상 존재하지 않거나 유효하지 않습니다! 해당 과목을 기초 모델로 초기화합니다...")
                    import FineTuneManager
                    ft : FineTuneManager.FineTuneManager = self.pm.ft;
                    ft.modelLib[lectureName] = None;
                    ft.LecturesSave()
                    self.__NormalRequestResponse__(sid, lectureName, requestQuestion, callback)
                    return
            
            responseAnswer = ex
            print(ex.__traceback__.format_exc())
            
        callback(sid, lectureName, responseAnswer)
    
    # 질문 요청
    def InitRequest(self, sid : str, lectureName : str, requestQuestion : str, callback) : # callback = Action<string sid, string msg>
        thread_instance = threading.Thread(
            target=self.__NormalRequestResponse__,
            args=(sid, lectureName, requestQuestion, callback)
        )
        thread_instance.start();
    

    # 데이터셋 요청 스레드
    def __DatasetRequestResponse__(self, lectureName : str, lectureData : str, callback):
        
        datasetRequest = f"이하는 '{lectureName}'라는 강의 주제의 강의 내용이다. \n\n{lectureData}" + """
        
해당 강의 내용을 요약해 질의응답 형식의 json 데이터로 변환하라. 데이터셋의 자료형식은 'json'이어야하고, 데이터셋의 양식은 다음과 같아.

# 데이터 샘플

```json
[
    {"messages": [{"role": "system", "content": "학생들의 강의 이해를 돕는 챗봇."}, {"role": "user", "content": "프랑스의 수도는 어디인가?"}, {"role": "assistant", "content": "'파리'라는 도시입니다."}]}
    {"messages": [{"role": "system", "content": "학생들의 강의 이해를 돕는 챗봇."}, {"role": "user", "content": "로미오와 줄리엣의 글쓴이는 누구인가?"}, {"role": "assistant", "content": "'윌리엄 셰익스피어'라는 소설가입니다."}]}
    {"messages": [{"role": "system", "content": "학생들의 강의 이해를 돕는 챗봇."}, {"role": "user", "content": "지구와 달은 얼마나 멀리 떨어져 있는가?"}, {"role": "assistant", "content": "384,400 킬로미터 가량 떨어져 있습니다."}]}
]
```
        
위와 같이 각각의 데이터는 아래와 같은 양식을 띄어야하며 "content"키의 값을 제외하고는 모두 일치해야 한다.

알았지? list[dict[str, list[dict[str, str]]]]의 형식을 지켜서 강의 내용을 질의응답 형식으로 정리한 데이터들을 생성해줘.

'messages' 리스트에 들어가는 요소는 단 세개이며 순서는 'role'에 따라 'system', 'user', 'assistant'여야만해.

[
    {
    "messages" :
        [
            {
                "role": "system",
                "content": "학생들의 강의 이해를 돕는 챗봇."
            },
            {
                "role": "user",
                "content": "프랑스의 수도는 어디인가?"
            },
            {
                "role": "assistant",
                "content": "'파리'라는 도시입니다."
            }
            
        ]
    }
]
        
답변으로 데이터를 5개 이상으로 반환하라. 답변은 최대한 많으면 많을수록 좋다.
        """
        
        datasetResponse  = ""
        datasetReturn  = []

        datasetSession = []
        datasetSession.append({
                                "role" : "system",
                                "content" : "너는 교수님의 강의 자료를 분석하고 AI가 학습 하기 위해 사용하는 데이터셋을 반환해야하는 도우미야."
                            })
        
        datasetSession.append({
                                "role" : "system",
                                "content" : """
사용자가 강의 주제와 강의 정보를 집어 넣으면 해당 강의 정보를 데이터셋으로 변환해서 출력해야줘.
출력되는 데이터의 수는 최소 10개 정도는 만들어줘야해. 또, 중요한 데이터가 생략될 만큼 적어서도 안되고, 너무 많은 데이터가 불필요하게 생성되어서도 안돼. 구체적인 데이터 수를 정하는 것은 네 판단에 맡길께. 

또한, 사용자가 입력한 정보 중 강의 주제와 연관이 없는 부분은 무시해줘.
예시를 들어 설명하자면, 'C# 객체 지향 프로그래밍'이라는 과목이라면, OOP 문법에 대한 설명과 상속 개념에 대한 이야기는 꼭 데이터로 만들어줘야해. 하지만 오늘의 점심 메뉴가 뭔지, 어디 회사의 노트북이 더 좋은지 등의 내용은 데이터로 만들 필요가 없어. 그것들은 강의 주제를 벗어난 얘기들이니까.

네가 이해하지 못한 몇가지 세부적인 사항도 무시해줘.
예시를 들어 설명하자면, '1.2.4 Main'나 '1.2.5 Console.WriteLine'등 전문적이지만 중요도가 낮은 사항에 대해 잘 모르겠다면 해당 부분에 대한 처리는 건너뛰어도 좋아.

데이터셋의 자료형식은 'json'이어야하고, 데이터셋의 양식은 다음과 같아.

# 데이터 샘플

```json
[
    {"messages": [{"role": "system", "content": "학생들의 강의 이해를 돕는 챗봇."}, {"role": "user", "content": "프랑스의 수도는 어디인가?"}, {"role": "assistant", "content": "'파리'라는 도시입니다."}]}
    {"messages": [{"role": "system", "content": "학생들의 강의 이해를 돕는 챗봇."}, {"role": "user", "content": "로미오와 줄리엣의 글쓴이는 누구인가?"}, {"role": "assistant", "content": "'윌리엄 셰익스피어'라는 소설가입니다."}]}
    {"messages": [{"role": "system", "content": "학생들의 강의 이해를 돕는 챗봇."}, {"role": "user", "content": "지구와 달은 얼마나 멀리 떨어져 있는가?"}, {"role": "assistant", "content": "384,400 킬로미터 가량 떨어져 있습니다."}]}
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
                # 복구를 위해 GPT에게 보내는 메세지
                restoreMessage : str = ""
                datasetString : str = ""
                
                # 무한 루프 탈출 코드
                count += 1
                printNor(f"반복 횟수 : {count}")
                if(count > 10) :
                    printError("비정상적인 반복 발생. 해당 요청 순회를 벗어납니다.")
                    break;
                
                #API로 답변을 요청
                completion : ChatCompletion = self.client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    temperature=0.7,
                    messages = datasetSession,
                    max_tokens= 4000,
                    frequency_penalty= 0.3,
                    presence_penalty= 0.3,
                )

                #반환할 문자열에 저장
                datasetResponse = completion.choices[0].message.content
                
                # json 파싱 검수
                sp = datasetResponse.split("```json")
                if(len(sp) == 2 ) :
                    datasetString = sp[1].split("```")[0];
                else : 
                    printError(f"```json가 존재하지 않아 파싱에 실패했습니다.")
                    restoreMessage = """
네가 출력한 문자열에는 유효한 json형식이 없다. 이하의 데이터 양식에 맞게 다시 출력하라. 이 메세지는 정상적인 데이터셋이 출력될 때까지 반복된다.
                                
# 데이터 샘플

```json
[
    {"messages": [{"role": "system", "content": "학생들의 강의 이해를 돕는 챗봇."}, {"role": "user", "content": "프랑스의 수도는 어디인가?"}, {"role": "assistant", "content": "'파리'라는 도시입니다."}]}
    {"messages": [{"role": "system", "content": "학생들의 강의 이해를 돕는 챗봇."}, {"role": "user", "content": "로미오와 줄리엣의 글쓴이는 누구인가?"}, {"role": "assistant", "content": "'윌리엄 셰익스피어'라는 소설가입니다."}]}
    {"messages": [{"role": "system", "content": "학생들의 강의 이해를 돕는 챗봇."}, {"role": "user", "content": "지구와 달은 얼마나 멀리 떨어져 있는가?"}, {"role": "assistant", "content": "384,400 킬로미터 가량 떨어져 있습니다."}]}
]```
                          """
                          
                # 자료구조 검수
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
                            if(len(dataSet["messages"]) > 3) : raise Exception("각 데이터의 길이는 3개여야 합니다. 현재 수령한 데이터는 3개보다 많으므로 json을 다시 구성해야합니다.")
                            
                            if(dataSet["messages"][1]["content"].__contains__("로미오와 줄리엣")) : raise Exception("이전에 주어진 강의 내용을 사용해서 새로운 json을 구성하세요. 당신은 예제로 준 내용을 그대로 사용헀기에 문제가 발생했습니다.")
                        
                        # 반환
                        datasetReturn = dataSets
                
                except Exception as ex:
                    printError(ex)
                    restoreMessage =  f"""
문제 발생 : {ex.args} {ex}
""" + """
네가 보낸 데이터를 json으로 파싱하는데에는 성공했지만, 자료구조가 일치하지 않아.
                                

각각의 데이터는 아래와 같은 양식을 띄어야하며 "content"키의 값을 제외하고는 모두 일치해야 해. 네가 보내준 데이터를 다시 확인하고 양식에 맞게 수정해서 강의 내용 요약을 다시 보내줘.
[      
    {
    "messages" :
        [
            {
                "role": "system",
                "content": "학생들의 강의 이해를 돕는 챗봇."
            },
            {
                "role": "user",
                "content": "프랑스의 수도는 어디인가?"
            },
            {
                "role": "assistant",
                "content": "'파리'라는 도시입니다."
            }
            
        ]
    }
]

알았지? list[dict[str, list[dict[str, str]]]]의 형식을 지켜서 강의 내용을 질의응답 형식으로 정리한 데이터들을 생성해줘.

'messages' 리스트에 들어가는 요소는 단 세개이며 순서는 'role'에 따라 'system', 'user', 'assistant'여야만해.

```json
[
    {"messages": [{"role": "system", "content": "학생들의 강의 이해를 돕는 챗봇."}, {"role": "user", "content": "프랑스의 수도는 어디인가?"}, {"role": "assistant", "content": "'파리'라는 도시입니다."}]}
    {"messages": [{"role": "system", "content": "학생들의 강의 이해를 돕는 챗봇."}, {"role": "user", "content": "로미오와 줄리엣의 글쓴이는 누구인가?"}, {"role": "assistant", "content": "'윌리엄 셰익스피어'라는 소설가입니다."}]}
    {"messages": [{"role": "system", "content": "학생들의 강의 이해를 돕는 챗봇."}, {"role": "user", "content": "지구와 달은 얼마나 멀리 떨어져 있는가?"}, {"role": "assistant", "content": "384,400 킬로미터 가량 떨어져 있습니다."}]}
]
```

"""

                # 재차 요청하는 내용을 세션에 추가해줌.
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
            print(f"예외발생 BadRequestError : {ex}");
            datasetResponse = ex  
        except Exception as ex:
            print(f"예외발생 Exception : {ex}");
            datasetResponse = ex
            
            if(str(ex).__contains__("429")) :
                sleep(5.)
                self.__DatasetRequestResponse__(lectureName, lectureData, callback)
                return
            
        callback(datasetReturn)
        
    # 데이터셋 요청
    def InitDataSet(self, lectureName : str, filePath : str) : # callback = Action<string msg>
        
        self.dataSetBuffer : list[str] = list[str]()

        #문자열 나누기
        rawDataSep = 1000;
        rawDataList = self.__readSplit__(filePath, rawDataSep)
        
        with open(filePath, "r", encoding = "utf-8") as file :
            printProcess(f"GPT를 이용해 로우 데이터에서 데이터셋을 추출합니다... 파일 크기 : {len(file.read())}자")
            printProcess(f"문맥 청크 단위 : {rawDataSep}자 / 청크 갯수 : {len(rawDataList)}")
            

        # 스레드로 동시에 여러개로 요청
        thrList : list[threading.Thread] = list[threading.Thread]()
        for rawData in rawDataList :
            thread_instance = threading.Thread(
                target=self.__DatasetRequestResponse__,
                args=(lectureName, rawData,
                            lambda msg : {
                                self.dataSetBuffer.append(msg),
                                printProcess(f"데이터셋 추출 중 {len(self.dataSetBuffer)}/{len(rawDataList)}\n{msg}")
                                }
                      )
            )
            thread_instance.start();
            thrList.append(thread_instance);
            sleep(5.);
        
        # 모든 요청이 끝날 때까지 기다리기
        for thr in thrList : 
            thr.join()
            
        
        # list[str] > dataSet
        retBuffer : list = []
        for dataSetList in self.dataSetBuffer :
            for dataSet in dataSetList :
                retBuffer.append(dataSet)
                 

        printSucceed(f"데이터셋 추출 완료! 추출한 데이터 수 : {len(retBuffer)}개")
        return retBuffer
        

    # PPT 라벨링 요청 스레드
    def __PptLabelingResponse__(self, lectureName : str, imageName : str, description : str, callback):
        try :
            labelingSession = []
            labelingSession.append({
                                    "role" : "system",
                                    "content" : "너는 강의 자료 ppt의 슬라이드 내의 텍스트를 요약해주는 도우미야."
                                })    
            
            labelingSession.append({
                                    "role" : "user",
                                    "content" : f"아래는 슬라이드 내에 있는 문자열 들이야.\n\n{description}\n\n 해당 문자열들을 정리해서 문장으로 요약해서 반환해줘."
                                })  
            #API로 답변을 요청
            completion : ChatCompletion = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                temperature=0.3,
                messages = labelingSession,
                max_tokens= 4000,
                frequency_penalty= 0.3,
                presence_penalty= 0.3,
            )

            #반환할 문자열에 저장
            datasetResponse = completion.choices[0].message.content
                
        except openai.BadRequestError as ex:
            print(f"예외발생 BadRequestError : {ex}");
            responseAnswer = ex  
            print(ex.__traceback__.format_exc())
        except Exception as ex:
            print(f"예외발생 Exception : {ex}");
            
            # 너무 잦은 요청 시, 지연 후 다시 실행.
            if(str(ex).__contains__("429") or str(ex).__contains__("697")) :
                printWarning("짧은 시간 내에 너무 많은 요청을 시도하고 있습니다. 5초 후 다시 실행합니다...")
                sleep(5.)
                self.__NormalRequestResponse__(sid, lectureName, requestQuestion, callback)
                return
            
            # 모델을 찾을 수 없을 시, 기본 모델로 변경 
            elif(str(ex).__contains__("404")) :
                if(str(ex).__contains__("model_not_found")) :
                    printError("해당 과목의 모델이 더이상 존재하지 않거나 유효하지 않습니다! 해당 과목을 기초 모델로 초기화합니다...")
                    import FineTuneManager
                    ft : FineTuneManager.FineTuneManager = self.pm.ft;
                    ft.modelLib[lectureName] = None;
                    ft.LecturesSave()
                    self.__NormalRequestResponse__(sid, lectureName, requestQuestion, callback)
                    return
            
            responseAnswer = ex
            print(ex.__traceback__.format_exc())
            
        callback(imageName, datasetResponse)
    
    # PPT 라벨링 요청
    def InitPptLabeling(self, lectureName : str, pairs : dict[str, str]) :
        
        dataSetDict : dict[str, str] = {}

        thrList : list[threading.Thread] = list[threading.Thread]()
        for key, value in pairs.items() : 
            thread_instance = threading.Thread(
                target=self.__PptLabelingResponse__,
                args=(lectureName, key, value,
                            lambda img, label : {
                                dataSetDict.update({img : label}),
                                printProcess(f"이미지 라벨링 중 {len(dataSetDict)}/{len(pairs)}\n{img} >> {label}")
                            }
                    )
                )        
            
            thread_instance.start();
            thrList.append(thread_instance);
            sleep(5.);
         
        # 모든 요청이 끝날 때까지 기다리기
        for thr in thrList :
            thr.join()
            sleep(1)
            
        printSucceed(f"이미지 라벨링 완료! 라벨링된 이미지 수 : {len(dataSetDict)}개")
        return dataSetDict




    # 파일에서 텍스트를 청크로 잘라 리스트로 가져옴
    def __readSplit__(self, file_path, chunkSize):
        result_list = []
        chunk = "-"

        with open(file_path, 'r', encoding='utf-8') as file:
            while chunk != "":
                chunk = file.read(chunkSize)
                result_list.append(chunk)
        return result_list
   
    # openai api에 파일 업로드
    def UploadFile(self, lecture) : 
        try :
            user_documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            saveDirectory = "WB38\\Lectures"
            path = rf"{user_documents_path}\{saveDirectory}\{lecture}\MERGED_DATASET\{lecture}_MERGED.jsonl"        
        
            printProcess(f"{lecture} 과목의 통합 데이터를 업로드합니다... Path : {path}")
            fo : FileObject = openai.files.create(
                file = open(path, "rb"),
                purpose = "fine-tune"
            )
            printProcess(f"{lecture} 과목의 통합 데이터를 업로드를 완료했습니다!")
            
            return fo
        
        except Exception as ex :
            print(ex);
            return None

    # 진행중인 파인 튜닝 잡과 업로드된 파일들을 조회
    def GetFineTuneData(self) : 
        ftJobs : SyncCursorPage =  openai.fine_tuning.jobs.list(limit=20)
        files : SyncPage[FileObject] = openai.files.list()
        return ftJobs, files
    
    # 파인튜닝 모델을 삭제함.
    def DeleteFineTuneModel(self, modelName) :
        printSucceed(f"모델(id : {modelName})를 삭제하는데 성공했습니다.")
        try : self.client.models.delete(modelName)
        except : pass
        # openai.models.delete(modelName)

    # openai api에서 사용 가능한 모든 모델을 조회
    def PrintAllModels(self) :
        for a in self.client.models.list().data : print(a.id)
            
