#coding=utf-8
import os
import shutil
from os import path
from subprocess import Popen, PIPE, STDOUT
import os
import subprocess
import uiautomator2 as u2
import time
import difflib

def execShellCommand(cmd):
    print("================cmd=================")
    print(cmd)
    popen = subprocess.Popen(cmd, shell = True,
                     stdout = subprocess.PIPE,
                     stderr = subprocess.PIPE,
                     universal_newlines=True,
                     bufsize = 1)
    # 执行                                           
    out,err = popen.communicate()  
    print('std_out: ' + out)
    print('std_err: ' + err)
    print('returncode: ' + str(popen.returncode))

#给出path1和 path2下近似的文件对---> 返回key-value
def findSimilarFiles(files1, files2):
    fileMatch = {}
    for file1 in files1:
        maxSimilar = -1
        maxSimilarfile = ""
        for file2 in files2:
            simalarTemp = difflib.SequenceMatcher(None, file1, file2).quick_ratio()
            print(file1, file2)
            print(simalarTemp)
            if (simalarTemp > maxSimilar):
                fileMatch[file1] = file2
                maxSimilar = simalarTemp
                maxSimilarfile = file2
        if (maxSimilarfile != ""):
            files2.remove(maxSimilarfile)

    print(fileMatch)
    return fileMatch

def compareFile(path1, path2, filePairs):
    execShellCommand('adb devices')
    for key in filePairs.keys():
        BCompare_exePath = '"E:\Program Files\Beyond Compare 4\BCompare.exe"'
        compareConfig = "config_log\diff_Config_to_html.txt"
        compareFile1 = path1 + "\\" + key
        compareFile2 = path2 + "\\" + filePairs[key]
        outReport = "report\\" + key + "_vs_" + filePairs[key] +  ".html"
        cmd = '%s /silent @%s %s %s %s' % (BCompare_exePath, compareConfig, compareFile1, compareFile2, outReport)
        execShellCommand(cmd)

def traverseCompare(path1, path2, isPath2NeedsKeyWords):
    dirs1, files1 = traverseDir(path1, "")
    print(dirs1)
    print(files1)

    dirs2, files2 = traverseDir(path2, isPath2NeedsKeyWords)
    print(dirs2)
    print(files2)

    #从path1 + dirs1和 path2 + dirs1中找匹配文件 ---> 返回key-value
    filePairs = findSimilarFiles(files1, files2)

    #比对当前目录下
    compareFile(path1, path2, filePairs)

    #递归对比子目录下的
    for dir in dirs1:
        traverseCompare(path1 + "\\" + dir, path2 + "\\" + dir, isPath2NeedsKeyWords)

def hasKeyWord(fileFullPath, isPath2NeedsKeyWords):
    file_object = open(fileFullPath, 'rb')
    try:
        lineCount = 0
        while 1:
            if (lineCount >= 10): #key一般在前十行以内
                return False
            line = file_object.readline()
            if not line:
                continue
            line.decode('utf8')
            if isPath2NeedsKeyWords in str(line):
                return True
            lineCount += 1
    except Exception as e:
        print(e)
        return False
    finally:
        file_object.close()



#查找一个文件夹下 1、所有文件名  2、所有路径名 --->只管一层
def traverseDir(file_dir, isPath2NeedsKeyWords):
    # for root, dirs, files in os.walk(file_dir):
    #     print("root", root)  # 当前目录路径
    #     print("dirs", dirs)  # 当前路径下所有子目录（不包括孙目录）
    #     print("files", files)  # 当前路径下所有非目录子文件（包括孙目录文件）

    dirs = []
    files = []
    for file in os.listdir(file_dir):  # 不仅仅是文件，当前目录下的文件夹也会被认为遍历到
        fileFullPath = file_dir +"\\" +file # isfile判断必须用全路径！！！
        if os.path.isfile(fileFullPath):
            print("这个是文件，文件名称：", file)
            if (isPath2NeedsKeyWords != "" and not hasKeyWord(fileFullPath, isPath2NeedsKeyWords)):
                continue
            files.append(file)
        elif os.path.isdir(fileFullPath):
            print("这个是文件夹，文件夹名称：", file)
            dirs.append(file)
        else:
            print("这个情况没遇到", file)

    return dirs, files


if __name__ == "__main__":
    path1 = r"C:\Users\Administrator\Desktop\shell笔记\beyondCompareScript\comparePath1"
    path2 = r"C:\Users\Administrator\Desktop\shell笔记\beyondCompareScript\comparePath2"
    isPath2NeedsKeyWords = ""
    # isPath2NeedsKeyWords = "(24, 0, 3)" #用来过滤文件

    traverseCompare(path1, path2, isPath2NeedsKeyWords)