 

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
            if process.info['name'] == 'cmd.exe':  # �ܼ� â�� �̸��� ���� ����
                try:
                    # ���μ��� ����
                    process.terminate()
                    process.wait(timeout=5)  # ����� ������ ���
                except Exception as e:
                    print(f"���μ��� ���� �� ���� �߻�: {e}")


    # ���� ȯ�� ���
    envPath = GlobalReference.envPath;
    print(envPath)
    # ������ �ڵ� ���
    initPath = GlobalReference.initPath;
    print(initPath)

    cmdCommands = f"cd {envPath}"               # cd S:env
    cmdCommands += " && " + envPath[:2]         # S:
    cmdCommands += " && " + "Scripts\\activate" # ����ȯ�� Ȱ��ȭ
    cmdCommands += " && " + f'''py "{initPath}"'''    # ���� �ڵ� Ȱ��ȭ

    inputCommand = f'start cmd /k "{cmdCommands}"'


    user_documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
    saveDirectory = "WB38"
    filePath = f"{user_documents_path}\{saveDirectory}"
    with open(rf"{filePath}\communication_file.txt", "w") as file:
        file.write("")

    print("����ȯ���� �ε��մϴ�...")
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
                    print("����ȯ���� ����ġ ���� ������ ���� ����ƽ��ϴ�. ���μ����� ��Ĩ�ϴ�.")
                    terminate_console_by_title("AiEnviormentTerminal")
                    break;
        except FileNotFoundError:
            continue

    

except Exception as ex:
    print(ex)
    input("")