# -*- coding: cp949 
from ast import List
import os
from openai.types.chat import ChatCompletionMessageParam

import json

from Addon.CustomConsolePrinter import printError, printNor, printProcess


# 세션 객체
class Session ():
    # 세션을 불러옴. 불러오는 김에 강의 정보 초기화도 겸사 겸사
    def __init__(self, sid : str, lectureName : str) :
        
        user_documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
        saveDirectory = "WB38\\Sessions"
        rootPath = f"{user_documents_path}\\{saveDirectory}"
        
        if not os.path.exists(rootPath):
            os.makedirs(rootPath)
                
        # 초기화
        self.lectureName : str = lectureName
        self.hashValue : str = str(sid) + lectureName
        self.sessionFile : str = f"{rootPath}\\{str(self.hashValue)}.json"
        self.sessionData : ChatCompletionMessageParam  = []
        
        #로드
        if(os.path.exists(self.sessionFile)) : #이미 전에 만든적이 있는 세션
            self.Load()
        else :
            self.Init()
            
    # 새로운 세션을 생성
    def Init(self) :
        with open(self.sessionFile, 'w', encoding='utf-8') as file:
            json.dump([], file)
            
        self.Append("system", "너는 강의 내용에 대해 물어보는 사용자에게 답변을 제공하는 친절한 도우미야.")
        
        self.Save()
    
    # 현재 세션 정보를 저장함
    def Save(self) :
        with open(self.sessionFile, "w", encoding="utf-8") as file:
            json.dump(self.sessionData, file, ensure_ascii=False, indent=2)
          
    # 저장된 세션 정보를 불러옴
    def Load(self):
        session = []
        try:
            with open(self.sessionFile, "r", encoding="utf-8") as file:
                session : ChatCompletionMessageParam = json.load(file)
            
        except FileNotFoundError as e:
            printError(f"세션 파일을 불러오는데에 실패했습니다. : {e}{e.with_stacktrace().format_exc()}")
            return
            
        self.sessionData = session
    
        
    # 새로운 대화 정보를 저장
    def Append(self, role :str, content : str) :
        self.Load();
        self.sessionData.append({"role" : role, "content" : content })
        
        self.Save();
    
    # 삭제
    def Remove(self) :
        try :
            os.remove(self.sessionFile)
            del self
            return True
        
        except Exception as ex:
            printError(f"{ex}\n{ex.with_traceback.format_exc()}")
            return False

    # 세션 정보 로드
    def GetData(self) :
        return self.sessionData
    
    def GetLastRole(self) :
        return self.sessionData[len(self.sessionData) - 1]["role"] if len(self.sessionData) != 0 else ""

        
class SessionManagerV2 () :
    def __init__(self) :
        self.pm = None;
        
        user_documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
        saveDirectory = "WB38\\Sessions"
        rootPath = f"{user_documents_path}\\{saveDirectory}"

        self.sessionList : List = [f for f in os.listdir(rootPath) if os.path.isfile(os.path.join(rootPath, f))];
   
    def GetSession(self, sid : str, lectureName : str) :
        return Session(sid, lectureName)
    
