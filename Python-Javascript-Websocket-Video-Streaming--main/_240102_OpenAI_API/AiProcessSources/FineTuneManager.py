 
from distutils import extension
import json
import os, shutil, sys
import threading
from time import sleep
import time
from httpx import Headers
from openai import OpenAI
import openai
from openai.pagination import SyncCursorPage, SyncPage

from openai.types import FileObject, FineTune
from openai.types.fine_tuning import FineTuningJob

from Addon.PdfConverter import Pdf2TextConverter;
from Addon.SpeechToTextConverter import SpeechToTextConverter;

from datetime import datetime
import pytz


def dirUp(dire , times) :
    return dirUp(os.path.dirname(dire), times-1) if times >0 else dire

sys.path.append(f'{ dirUp(os.path.abspath(__file__), 3) }')
from Addon.CustomConsolePrinter import printProcess, printError, printNor, printSucceed, printWarning;


class FineTuneManager () :
    def __init__(self) :
        self.pm = None;

        # lecture : str => filePaths : list[str]
        self.trainingTree : dict[str,  list[str]] = {}
        
        # lecture : str => filePaths : list[str]
        self.trainedTree : dict[str,  list[str]] = {}
        
        # lecture : str => modelName : str
        self.modelLib : dict[str,  str] = {}
        
        user_documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
        saveDirectory = "WB38\\Lectures"
        self.rootPath = f"{user_documents_path}\\{saveDirectory}"
        
        
    # ���ο� ���¸� ����ϴ�.
    def LecturesCreate(self, lecture : str) : 
        
        lecPath = self.__lectureToPath__(lecture=lecture)
        
        # �̹� �����ϸ� ���� �Ұ�
        if os.path.exists(lecPath) :
            printError(f"{lecture} ������ �̹� �����ϱ� ������ ������ �� �����ϴ�.")
            return False
        
        # ���丮 ����
        os.makedirs(lecPath)
        os.makedirs(lecPath + r"\\RAW_DATA");
        os.makedirs(lecPath + r"\\TRAINING_DATA");
        os.makedirs(lecPath + r"\\MERGED_DATASET");
        
        
        # �ڷᱸ���� ����
        self.trainedTree[lecture] = list[str]();
        self.trainingTree[lecture] = list[str]();
        self.modelLib[lecture] = None;
        
        # lecture_info.json ����
        lectureData = {
            "modelName": None,
            "trainedList" : []
        }
        
        with open(rf"{lecPath}\lecture_info.json", "w") as json_file:
            json.dump(lectureData, json_file)
            
        printSucceed(f"���������� '{lecture}'�� �����ϴµ� �����߽��ϴ�.")
        return True;
    
    # ���� ���¸� �����մϴ�.
    def LecturesDelete(self, lecture : str) :
        
        lecPath = self.__lectureToPath__(lecture=lecture)
        if not os.path.exists(lecPath):
            printError(f"�������� �ʴ� ���� '{lecPath}'�� �����Ϸ��� �õ��ϰ� �ֽ��ϴ�.")
            return False
            
        # ���丮 ����(������ ���ϱ��� ��� ������)
        shutil.rmtree(lecPath)
        
        del self.trainingTree[lecture]
        del self.trainedTree[lecture]
        del self.modelLib[lecture]
        printSucceed(f"���������� '{lecture}'�� �����ϴµ� �����߽��ϴ�.")
        
        return True

    # ���ǵ� �ε�
    def LecturesLoad(self) : 
        try :
            # �����ڷ� �ʱ�ȭ
            self.trainingTree : dict[str,  list[str]] = {}
            self.trainedTree : dict[str,  list[str]] = {}
            self.modelLib : dict[str,  str] = {}
        
            # ��� ���� ���丮�� ����

            tPath = self.rootPath;
            directories = [item for item in os.listdir(tPath) if os.path.isdir(os.path.join(tPath, item))]

            for lecture in directories:
                full_path = os.path.join(self.rootPath, lecture)
                
                # lecture_info�� �о����
                with open(rf"{full_path}\lecture_info.json", "r") as json_file:
                    data = json.load(json_file)
                    
                    self.modelLib[lecture] = data["modelName"];
                    self.trainedTree[lecture] = data["trainedList"]
                    
                    self.trainingTree[lecture] = list[str]()

                ttPath = full_path + "\\TRAINING_DATA";
                files = [item for item in os.listdir(ttPath) if os.path.isfile(os.path.join(ttPath, item))]                

                # lecture TRAINING_DATA�� �о����
                for file_path in files:
                        
                    # MERGED_DATASET�� ����
                    if self.trainingTree[lecture].__contains__(file_path) : continue;
                        
                    # ã�� Ʈ���̴� ������ ��θ� ����
                    self.trainingTree[lecture].append(file_path)
                            
            printSucceed(f"���� ���� �ε忡 �����߽��ϴ�. \n�н� ���� �ڷ� : \n{self.trainingTree}\n�н� �Ϸ� �ڷ� : \n{self.trainedTree}\n�� : \n{self.modelLib}")
            return True;
    
        except Exception as ex :
            printError(f"���� �ε尡 �����߽��ϴ�. �� ���� : {ex}")
            input("�� �̻��� ������ �����ϹǷ�, ���μ����� �����մϴ�.")
            exit()
            
            return False;
    
    # ���ǵ� ����
    def LecturesSave(self) : 
        tPath = self.rootPath;
        directories = [item for item in os.listdir(tPath) if os.path.isdir(os.path.join(tPath, item))]

        for lecture in directories:
            full_path = os.path.join(self.rootPath, lecture)
                    
            lectureData = {
                "modelName": self.modelLib[lecture],
                "trainedList" : self.trainedTree[lecture]
            }
                    
            # lecture_info�� �о����
            with open(rf"{full_path}\lecture_info.json", "w") as json_file:
                json.dump(lectureData, json_file)
    
    # ���ǵ� ����Ʈ
    def LecturesList(self) : 
        return list(self.modelLib.keys())


    # �� ���� ��������
    def GetModel(self, lecture : str) : 
        try :
            modelName : str = self.modelLib[lecture]
        except KeyError as ex :
            printWarning(f"{lecture}������ �������� �ʽ��ϴ�.")
            return "(��ȿ���� ���� ����)"
        
        if modelName == None or modelName == "" :
            printWarning(f"{lecture}�� ����Ʃ�� ���� �������� �ʽ��ϴ�. �ٽ� �ѹ� Ȯ�����ֽʽÿ�.")
            return "gpt-3.5-turbo-1106"
        
        printSucceed(f"{lecture}�� ����Ʃ�� ��({modelName})�� ã�ҽ��ϴ�.")
        return modelName


    # ����Ʃ�� ���� ������ ����
    def StartFineTuneChecker(self) :
        thread_unit = threading.Thread(target=self.__threadFineTuneChecker__, args=[30.]);
        thread_unit.start()
    
    # ����Ʃ�� ���� ����Ʈ
    def __threadFineTuneChecker__(self, frequency : float) :
        try :
            while True :
                try :
                    api = self.pm.api;
                         
                    files :SyncPage[FileObject]

                    ftData, files =  api.GetFineTuneData()
                    ftJobs : list[FineTune] = ftData.data
                    ftFiles : list[FileObject] =  files.data
                
                    self.__fineTuneListPrint__(ftJobs, ftFiles)
                    
                    sleep(frequency)
                    
                except Exception as ex:   
                    printError(ex)
        except Exception as ex:   
            printError(ex)     
    def __fineTuneListPrint__(self, ftJobs : list[FineTune], ftFiles : list[FileObject]) :
        msg = f"<����Ʃ�� �� �۾� ��� : {len(ftJobs)}��>\n"
        for job in ftJobs :
            startTime = datetime.fromtimestamp(job.created_at)
                        
            timeFormat = "%Y-%m-%d %H:%M:%S" 
                        
            if (job.status in ["succeeded"]) :
                msg += f"[SUCCEED] [{startTime.strftime(timeFormat)}] [{job.id}] Name : {job.fine_tuned_model} \n"
                            
            elif (job.status in ["failed", "cancelled"]) :
                msg += f"[FAILURE] [{startTime.strftime(timeFormat)}] [{job.id}] Name : {job.fine_tuned_model} \n"
                            
            else :
                msg += f"[PROCESS] [{startTime.strftime(timeFormat)}] [{job.id}] Name : {job.fine_tuned_model} \n"
            
            for trFile in job.result_files :
                print()
                msg += f"\t<{trFile}>\n"
                
        msg += f"<�н� ���� ��� : {len(ftFiles)}��>\n"        
        for file in ftFiles :
            startTime = datetime.fromtimestamp(file.created_at)
                        
            timeFormat = "%Y-%m-%d %H:%M:%S" 
                        
            if (file.status in ["uploaded"]) :
                msg += f"[ UPLOAD] [{startTime.strftime(timeFormat)}] [{file.id}] FileName : {file.filename}({file.bytes}) \n"
                            
            elif (job.status in ["error"]) :
                msg += f"[FAILURE] [{startTime.strftime(timeFormat)}] [{file.id}] FileName : {file.filename}({file.bytes}) \n"
                            
            else :
                msg += f"[DEFAULT] [{startTime.strftime(timeFormat)}] [{file.id}] FileName : {file.filename}({file.bytes}) \n"
                            
        msg += "<��� ��>\n"
        print(msg)


    # ����Ʃ�� ����
    def StartFineTuneJob(self, lectureName : str) :
        try :
            printProcess(f"'{lectureName}' ������ �ڰ� �н��� �غ� ���Դϴ�...")
            
            if self.__CheckFineTuneAvailable__(lectureName) == False : 
                printError(f"'{lectureName}' ������ �̹� �������� ����Ʃ�� �۾��� �־� ����Ʃ���� �������� ���߽��ϴ�.")
                return
            
            # ��ó ������ ���� �����ͼ� �����۾��� ��ģ��.
            self.__MakeDataSetWhole__(lectureName);

            # ���������� ���� 
            self.__MergeDataSet__(lectureName)
        
            # ���������� ���ε�
            fo : FileObject = self.pm.api.UploadFile(lectureName)
                
            # ����Ʃ�� ����
            ftj : FineTuningJob = openai.fine_tuning.jobs.create(model = "gpt-3.5-turbo-1106", training_file = fo.id)
        
            # ����Ʃ�� �۾� ���� ������ ����
            thread_unit : threading.Thread = threading.Thread(target = self.__threadFineTuneJob__, args = (lectureName, ftj,  self.__FineTuneJobCallback__))
            thread_unit.start()
            printProcess(f"'{lectureName}' ������ �ڰ� �н��� �����մϴ�.")
        
            # ����Ʃ�� �۾� ���̺�����Ʈ ����
            self.__MakeFineTuneCheckPoint__(lecture=lectureName, ft= ftj)
            
            return True
        except :
            return False
        
    # ����Ʃ�� ������
    def __threadFineTuneJob__(self, lectureName : str, ftJobData : FineTuningJob,  callback) : 
        
        printProcess(f"'{lectureName}' ������ ����Ʃ�� �����尡 �����ƽ��ϴ�.")
        
        ft : FineTuningJob
        
        from _240102_OpenAI_API._240102_OpenAI_API.AiProcessSources.ProcessManager import p1, p2
        while True :
            try :
                
                # ����Ʃ�� ���� �� ������ �����´�.
                ft = openai.fine_tuning.jobs.retrieve(ftJobData.id)
            
                #���� �ð�, ����� �ʸ� ��´�.
                startTime = datetime.fromtimestamp(ft.created_at)
                pastTick = int(time.time()) - ft.created_at
                jobStatus = ft.status       

                printProcess(f"�ڰ��н� ������ - ���� �� : {lectureName}\t ���� �ð� : {startTime}\t ��� �ð� : {pastTick}��\t ���� ���� : {jobStatus}")
                
                #��ġ����?
                if(jobStatus in ["succeeded"]) :
                    printSucceed(f"���������� �ڰ��н��� �Ϸ�Ǿ����ϴ�. �ϼ��� AI�� �� Ű : {ft.fine_tuned_model}")
                    printSucceed(f"���� �� : {lectureName}\t ���� �ð� : {startTime}\t ��� �ð� : {ft.finished_at - ft.created_at}��\t ���� �ð� : {datetime.fromtimestamp(ft.finished_at)}")
                    callback(lectureName, ft.fine_tuned_model)
                    break
                
                #���߳�?
                elif (jobStatus in ["failed", "cancelled"]) :
                    printError(f"�ڰ��н��� �����߽��ϴ�! state : {jobStatus}")
                    printError(f"���� �� : {lectureName}\t ���� �ð� : {startTime}\t ��� �ð� : {pastTick}��\t ���� �ð� : {pastTick}")
                    
                    #ġ������ ������ ���� ó��
                    self.pm.client.Send(f"FineTuneEnd{p1}{str(False)}{p2}{lectureName}")
                    return
                
            except Exception as e: 
                printError(f"__threadFineTuneJob__ ���� : {e}\n{e.with_traceback.format_exc()}")
                
                #ġ������ ������ ���� ó��
                self.pm.client.Send(f"FineTuneEnd{p1}{str(False)}{p2}{lectureName}")
                return 
              
            #�ƴϾ�? �׷� �ݺ�  
            sleep(10.)
        
        # ��� ��ȯ
        callback(lectureName, ft.fine_tuned_model)
    
    # ����Ʃ�� ������ �ݹ�
    def __FineTuneJobCallback__ (self, lectureName, modelName) : 
        from _240102_OpenAI_API._240102_OpenAI_API.AiProcessSources.ProcessManager import p1, p2
        try :
            # �̹� ���� ���� ���� �� ��ŵ.
            if(self.modelLib[lectureName] == modelName) : return;
        
            # ���� ���� ����
            printProcess(f"{lectureName}�� ���� {modelName}�� ��ü�մϴ�.")
            if(self.modelLib[lectureName] != None) :
                printProcess(f"���� �� {self.modelLib[lectureName]}�� �����մϴ�...")
                self.pm.api.DeleteFineTuneModel(self.modelLib[lectureName])
                
            #���ο� �� ����
            printProcess(f"���ο� �� {modelName}�� ��ġ�մϴ�.")
            self.modelLib[lectureName] = modelName
            self.trainedTree[lectureName] = self.trainingTree[lectureName]
            
            self.LecturesSave()
        
            # �������� �������� ���� ���� ���̱�
            self.pm.client.Send(f"FineTuneEnd{p1}{str(True)}{p2}{lectureName}")
            
        except Exception as ex:
            # ���������� ���ῡ ���� ���� ���̱�
            printError(f"����Ʃ�� �ݹ鿡�� ���� �߻� : {ex}\n{ex.with_traceback.format_exc()}")
            self.pm.client.Send(f"FineTuneEnd{p1}{str(False)}{p2}{lectureName}")


    # �ο� �����͸� �о��� ���� ������ �ɴϴ�. txt > txt
    def AddRawData(self, lecture : str, txtFilePath : str) : 
        try:
            # �ؽ�Ʈ ������ ���� �о����
            with open(txtFilePath, "r", encoding ="utf-8") as source_file:
                file_content = source_file.read()

            # ���ο� ���丮�� �ؽ�Ʈ ���� �����ϰ� ���� ����
            file_name = os.path.basename(txtFilePath)
            destination_path = rf"{self.__lectureToPath__(lecture)}\RAW_DATA\{file_name}"

            with open(destination_path, "w", encoding ="utf-8") as destination_file:
                destination_file.write(file_content)
            
            if not self.trainingTree[lecture].__contains__(file_name) :
                self.trainingTree[lecture].append(file_name);
            self.LecturesSave();
            
            printSucceed(f"�ο� �����͸� �߰� �Ϸ�: {destination_path}")
            return True;
    
        except FileNotFoundError:
            printError(f"�ο� �����͸� �߰����� �������ϴ�. �ش� ������ ã�� �� �����ϴ�. {txtFilePath}")
            return False;
        
        except Exception as e:
            printError(f"�ο� ������ �߰� ��, ���� �߻�: <{txtFilePath}> {e}")
            return False;

    # pdf > txt
    def AddPdfData(self, lecture : str, pdfFilePath : str) : 
        try:
            
            # ���ο� ���丮�� �ؽ�Ʈ ���� �����ϰ� ���� ����
            file_name = os.path.basename(pdfFilePath).replace('.pdf','')
            destination_path = rf"{self.__lectureToPath__(lecture)}\RAW_DATA\{file_name}.txt"

            pdfCon = Pdf2TextConverter();
            pdfCon.convert(pdfFilePath, destination_path)
            
            if not self.trainingTree[lecture].__contains__(file_name) :
                self.trainingTree[lecture].append(file_name);
            self.LecturesSave();
            
            printSucceed(f"�ο� �����͸� �߰� �Ϸ�: {destination_path}")
            return True;
    
        except FileNotFoundError:
            printError(f"�ο� �����͸� �߰����� �������ϴ�. �ش� ������ ã�� �� �����ϴ�. {pdfFilePath}")
            return False;
        
        except Exception as e:
            printError(f"�ο� ������ �߰� ��, ���� �߻�: {pdfFilePath} - {e}")
            return False;
        
    # wav > txt
    def AddWavData(self, lecture : str, wavFilePath : str) : 
        try:
            # ���ο� ���丮�� �ؽ�Ʈ ���� �����ϰ� ���� ����
            extension = os.path.splitext(wavFilePath)[1]
            file_name = os.path.basename(wavFilePath).replace(extension,'')
            destination_path = rf"{self.__lectureToPath__(lecture)}\RAW_DATA\{file_name}.txt"

            sttc = SpeechToTextConverter();
            gsutil = sttc.upload_file(wavFilePath);
            transcript = sttc.transcribe_gcs(gsutil);      
            
            with open(destination_path, "w", encoding="utf-8") as file :
                file.write(transcript)

            if not self.trainingTree[lecture].__contains__(file_name) :
                self.trainingTree[lecture].append(file_name);
            self.LecturesSave();
            
            printSucceed(f"�ο� �����͸� �߰� �Ϸ�: {destination_path}")
            return True;
    
        except FileNotFoundError:
            printError(f"�ο� �����͸� �߰����� �������ϴ�. �ش� ������ ã�� �� �����ϴ�. {wavFilePath}")
            return False;
        
        except Exception as e:
            printError(f"�ο� ������ �߰� ��, ���� �߻�: {wavFilePath} - {e}")
            return False;
  
         
    # ������ �ο� �����ͷ� GPT �� ����� �н� �����ͷ� ����ϴ�. txt > json
    def __MakeDataSet__(self, lecture : str, txtFilePath : str) : 
        
        printProcess(f"�ο� �����Ϳ��� GPT�� �̿��� �н� �����͸� �����մϴ�...  ��� ���� : {txtFilePath}...")
        
        api = self.pm.api;
        #�н� ���� ����
        dataSet : list = api.InitDataSet(lecture, txtFilePath);
        
        # ������ �ؽ�Ʈ jsonl
        txtFileName = os.path.basename(txtFilePath).replace(".txt", "")
        dataSetPath : str = fr"{self.__lectureToPath__(lecture)}\TRAINING_DATA\{txtFileName}.jsonl"
        
        printSucceed(f"�ο� �����Ϳ��� GPT�� �̿��� �н� �����͸� �����ϴµ� �����߽��ϴ� ��� ���� : {dataSetPath}...")
        
        with open(dataSetPath, "w", encoding = "utf-8") as json_file:
            json_file.write(json.dumps(dataSet, ensure_ascii=False))
    
    # ���� ���� ��ó �Ϸ���� ���� ��� �ο� �����͸� �����Ѵ�.
    def __MakeDataSetWhole__(self, lecture : str) :
        printProcess("��ó �Ϸ���� ���� �ο쵥���͸� ã���ϴ�.")  
        
        resultList = []      
        
        try :
            lecPath = self.__lectureToPath__(lecture)
            rawPath = lecPath + r"\RAW_DATA"
            trainPath = lecPath + r"\TRAINING_DATA"
            
            rawList = []
            for filename in os.listdir(rawPath):
                if os.path.isfile(os.path.join(rawPath, filename)):
                    file_name_without_extension, _ = os.path.splitext(filename)
                    rawList.append(file_name_without_extension)
                    
            trainList = []
            for filename in os.listdir(trainPath):
                if os.path.isfile(os.path.join(trainPath, filename)):
                    file_name_without_extension, _ = os.path.splitext(filename)
                    trainList.append(file_name_without_extension)

            tempList = []
            for element in rawList:
                if element not in trainList:
                    tempList.append(element)
                    
            for fileName in tempList :
                resultList.append(f"{rawPath}\{fileName}.txt")
                
        except Exception as  ex:
            print(ex);
            

        try : 
            print("[result]" + str(resultList))
            
            for txtFile in resultList :
                self.__MakeDataSet__(lecture, txtFile)
                
        except Exception as ex :
            print(ex);

    # �ش� ������ ��� �����ͼ��� �ϳ��� ���� ���ε带 �غ��մϴ�. json, json... > jsonl
    def __MergeDataSet__(self, lecture : str) : 
        
        printProcess(f"'{lecture}'������ ���� ������ ������ �����մϴ�... ")
        
        lecPath = self.__lectureToPath__(lecture);        
        trainingFileDir = rf"{lecPath}\TRAINING_DATA"

        jsonl_contents = []

        # ���丮 ������ ���ϵ� ��������
        files = [f for f in os.listdir(trainingFileDir) if os.path.isfile(os.path.join(trainingFileDir, f))]

        # JSONL ���ϵ鿡 ���� �ݺ�
        for file_name in files: 
            if file_name.endswith('.jsonl'):
                jsonlPath = os.path.join(trainingFileDir, file_name)
                with open(jsonlPath, 'r', encoding='utf-8') as jsonl_file:
                    # ���� ���� �о����
                    file_content = jsonl_file.read()
                    dataList = json.loads(file_content)
                    jsonl_contents.extend([data for data in dataList])

        
        dataSetPath : str = fr"{self.__lectureToPath__(lecture)}\MERGED_DATASET\{lecture}_MERGED.jsonl"

        with open(dataSetPath, "w", encoding="utf-8") as json_file:
            
            for item in jsonl_contents:
                json_file.write(json.dumps(item, ensure_ascii=False) + '\n')
            
        printSucceed(f"'{lecture}'������ ���� �����͸� �����ϴµ��� �����߽��ϴ�. ��� : {dataSetPath}")
    
    # ���� �̸����� ���� ��� ã��
    def __lectureToPath__(self, lecture : str) :
        filePath : str = f"{self.rootPath}\\{lecture}"
        return filePath 
    
    
    # ����Ʃ�� �� ���̺�����Ʈ ����
    def __MakeFineTuneCheckPoint__(self, lecture : str, ft : FineTuningJob) : 
        user_documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
        saveDirectory = "WB38"
        cpPath = f"{user_documents_path}\\{saveDirectory}\\finetune_checkpoint.json"
        
        dataPre : list
        
        with open(cpPath, "r", encoding="utf-8") as jsonFile :
            dataPre = json.load(jsonFile)
            
        dataPre.append({"lecture" : lecture, "fineTuneJob" : ft.id})
        
        with open(cpPath, "w", encoding="utf-8") as jsonFile :
            json.dump(dataPre, jsonFile, ensure_ascii=False)
            
        printSucceed(f"'{lecture}' ������ �ڰ� �н� ���̺�����Ʈ�� ���������ϴ�!")
        
    # ����Ʃ�� �� ���̺� ����Ʈ �ε�. ������ ����Ʃ�� ���� ���� ��, ������ �����
    def __LoadFineTuneCheckPoint__(self) : 
        try : 
            user_documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            saveDirectory = "WB38"
            cpPath = f"{user_documents_path}\\{saveDirectory}\\finetune_checkpoint.json"
            
            # ���̺� ����Ʈ �ε�
            dataPre : list
            with open(cpPath, "r", encoding="utf-8") as jsonFile :
                dataPre = json.load(jsonFile)
        
            # API�� �������� ����� �ε�
            from ApiManager import OpenAiManagerV2 
            api : OpenAiManagerV2 = self.pm.api;
            ftData, files = api.GetFineTuneData()
            ftJobs : list[FineTuningJob] = ftData.data
    
            # ���̺� ����Ʈ���� ��ȸ�ϸ� �������� ����� Ȯ��

            for data in  dataPre : # ���̺�����Ʈ ��ȸ
            
                lecture : str = data["lecture"]
                ftId : str = data["fineTuneJob"] 
                
                for ftJob in ftJobs : # ����Ʃ�� �� ��ȸ
                    if(ftJob.id == ftId) :  # ���̺�����Ʈ�� ��ġ
                        if(ftJob.status in ["failed", "cancelled", "succeeded"]) : #��ȿ���� ���� ����Ʃ�� ��
                            break;
        
                        #����Ʃ�� �۾� ���� ������ ����
                        thread_unit : threading.Thread = threading.Thread(target = self.__threadFineTuneJob__, args = (lecture, ftJob, self.__FineTuneJobCallback__))
                        thread_unit.start()
                        printSucceed(f"'{lecture}' ������ �ڰ� �н� ���̺�����Ʈ�� �ҷ��Խ��ϴ�!")
                        
        except FileNotFoundError as ex :
            printWarning(f" finetune_checkpoint.json ������ �������� �ʽ��ϴ�. ���� �����մϴ�. ")
            with open(cpPath, "w", encoding="utf-8") as jsonFile :
                json.dump([], jsonFile, ensure_ascii=False)
            
        except Exception as ex : 
            printError(f"__LoadFineTuneCheckPoint__ ���� �� �����߻�. {ex}\n{ex.with_traceback.format_exc()}")
               
    # ����Ʃ�� �������� üũ
    def __CheckFineTuneAvailable__(self, lectureName : str) :
        try : 
            user_documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            saveDirectory = "WB38"
            cpPath = f"{user_documents_path}\\{saveDirectory}\\finetune_checkpoint.json"
            
            # ���̺� ����Ʈ �ε�
            cpList : list
            with open(cpPath, "r", encoding="utf-8") as jsonFile :
                cpList = json.load(jsonFile)
        
            # API�� �������� ����� �ε�
            from ApiManager import OpenAiManagerV2 
            api : OpenAiManagerV2 = self.pm.api;
            ftData, files = api.GetFineTuneData()
            ftJobs : list[FineTuningJob] = ftData.data
    
            # ���̺� ����Ʈ���� ��ȸ�ϸ� �������� ����� Ȯ��

            for cp in  cpList : # ���̺�����Ʈ ��ȸ
            
                cpLecture : str = cp["lecture"]
                cpId : str = cp["fineTuneJob"]
            
                for ftJob in ftJobs : # ����Ʃ�� �� ��ȸ
                    if(ftJob.id == cpId and lectureName == cpLecture) :  # ���̺�����Ʈ�� ����� ����� �� ������ ��ġ
                        if ftJob.status in ["validating_files", "queued", "running"] : #�������̶�� 
                            return False;
            
            return True
        
        except FileNotFoundError as ex :
            printWarning(f" finetune_checkpoint.json ������ �������� �ʽ��ϴ�. ���� �����մϴ�. ")
            with open(cpPath, "w", encoding="utf-8") as jsonFile :
                json.dump([], jsonFile, ensure_ascii=False)
            
        except Exception as ex : 
            printError(f"__CheckFineTuneAvailable__ ���� �� �����߻�. {ex}\n{ex.with_traceback.format_exc()}")
                
