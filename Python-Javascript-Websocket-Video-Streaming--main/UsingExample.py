 
import sys
import time
from AiModuleProcess import AiModuleProcess


# AI �� ��뿹.
try :
    ai = AiModuleProcess();
    
    # ai.ExecuteDebugCode();
    # ai.ExecuteTestQandA

    # ai.DoLectureCreate("�ڻ����� �ɷη���")
    # ai.DoSendDataTxt("�ڻ����� �ɷη���", r"S:\[GitHub]\240102_OpenAI_API\�� �ؽ�Ʈ ����.txt")
    # time.sleep(1.)
    # ai.DoFineTuneCreate("�ڻ����� �ɷη���")
    sys.exit()

except Exception as ex : 
    print(ex + ex.with_stacktrace().format_exc())
