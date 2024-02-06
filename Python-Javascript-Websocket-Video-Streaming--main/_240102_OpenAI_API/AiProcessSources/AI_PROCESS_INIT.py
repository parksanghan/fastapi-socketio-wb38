# -*- coding: cp949 -*-

try : 

    import subprocess
    from time import sleep
    import psutil

    import ctypes
    import sys, os
    
    import Addon.CustomConsolePrinter

    def dirUp(dire , times) :
        return dirUp(os.path.dirname(dire), times-1) if times >0 else dire

    sys.path.append(f'{ dirUp(os.path.abspath(__file__), 3) }')
    import GlobalReference
    

    ctypes.windll.kernel32.SetConsoleTitleW("AiInitiateTerminal")

    def terminate_console_by_title(title):
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == 'cmd.exe':  # 콘솔 창의 이름에 따라 변경
                try:
                    # 프로세스 종료
                    process.terminate()
                    process.wait(timeout=5)  # 종료될 때까지 대기
                except Exception as e:
                    print(f"프로세스 종료 중 오류 발생: {e}")


    # 가상 환경 경로
    envPath = GlobalReference.envPath;
    print(envPath)
    # 진입점 코드 경로
    initPath = GlobalReference.initPath;
    print(initPath)

    cmdCommands = f"cd {envPath}"               # cd S:env
    cmdCommands += " && " + envPath[:2]         # S:
    cmdCommands += " && " + "Scripts\\activate" # 가상환경 활성화
    cmdCommands += " && " + f'''py "{initPath}"'''    # 시작 코드 활성화

    inputCommand = f'start cmd /k "{cmdCommands}"'


    user_documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
    saveDirectory = "WB38"
    filePath = f"{user_documents_path}\{saveDirectory}"
    with open(rf"{filePath}\communication_file.txt", "w") as file:
        file.write("")

    print("가상환경을 로드합니다...")
    process = subprocess.Popen(inputCommand, shell=True, creationflags=subprocess.CREATE_NO_WINDOW )
    
    while True:
        sleep(1)
        message = ""
    
        user_documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
        saveDirectory = "WB38"
        filePath = f"{user_documents_path}\{saveDirectory}"
    
        if os.path.exists(f"{user_documents_path}\{saveDirectory}"):
            pass
        else : os.makedirs();
    
        try :
            with open(rf"{filePath}\communication_file.txt", "r") as file:
                message = file.read()
            
                if(message == "EXIT_CODE") :
                    print("가상환경이 예기치 않은 오류로 인해 종료됐습니다. 프로세스를 마칩니다.")
                    terminate_console_by_title("AiEnviormentTerminal")
                    break;
        except FileNotFoundError:
            continue

    

except Exception as ex:
    print(ex)
    input("")