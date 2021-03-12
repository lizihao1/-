#网页后台扫描器，根据文件位置自行创建字典文件和网页target
import sys
import urllib.request
import time
import threading
rawurl = open(r"C:\Users\lizihao\Desktop\currenttopics\target.txt","r")
url="http://"+rawurl.read()
rawurl.close()
txt = open(r"C:\Users\lizihao\Desktop\currenttopics\websearch.txt","r")
open_url = []
all_url = []
threads = []
def search_url(url,txt):
    with open(r"C:\Users\lizihao\Desktop\currenttopics\websearch.txt") as f:
        for each in f:
            each = each.replace('\n','') #将文本中每行的字典条目读取，将换行符替换为空，并依次读取内容
            urllist= url+each    #拼接原始IP/域名和字典条目
            all_url.append(urllist)  #将新组成的IP/域名存入all_url变量
            print("ping:"+urllist+'\n')
        #    filter_url(urllist)
def filter_url(urllist):
    try:
        req=urllib.request.urlopen(urllist) #获取状态码作为过滤条件
        if req.getcode()==200:
            open_url.append(urllist)
        if req.getcode()==301:
            open_url.append(urllist)
    except:
        pass

def main():
    search_url(url,txt)

    for each in all_url:
        t = threading.Thread(target = filter_url,args=(each,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    if open_url:
        print("results:")
        for each in open_url:
            print("\n"+each)
    else:
        print("no results found")

if __name__ =="__main__":
    start = time.clock()
    main()
    end = time.clock()
    print("time cost: %.3f seconds" %(end-start))
