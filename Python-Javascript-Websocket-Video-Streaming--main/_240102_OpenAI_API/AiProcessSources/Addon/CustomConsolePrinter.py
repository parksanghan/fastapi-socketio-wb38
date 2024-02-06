# -*- coding: cp949 -*-

def printSucceed(msg : str) :
    print(f"[\033[92mSUCCEED\033[0m] {msg}")
def printError(msg : str) :
    print(f"[\033[91mERROR\033[0m] {msg}")
def printWarning(msg : str) :
    print(f"[\033[93mWARNING\033[0m] {msg}")
def printProcess(msg : str) :
    print(f"[\033[96mPROCESS\033[0m] {msg}")
def printNor(msgType :str,  msg : str) :
    print(f"[{msgType}] {msg}")
def printNor(msg : str) :
    print(f"[DEBUG] {msg}")