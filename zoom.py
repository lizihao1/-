import os
import requests
import json

access_token = ''
ip_list =[]

def login():
    user =input('username :')
    passwd=input('password :')
    data = {
        'username':user,
        'password':passwd
    }
    data_encrypted= json.dumps(data) #dumps将python字典对象转换为json字符串
    try:
        r=requests.post(url='https://api.zoomeye.org/user/login',data=data_encrypted) #post有风险，容易被封IP
        r_decrypted= json.loads(r.text) #loads将json字符串转换为python字典对象
        global access_token

        print(r_decrypted)
        access_token=r_decrypted['access_token'] #POST登录数据，由官方API返回临时token
    except Exception as e:
        print('error')
        exit()

def saveSTRtoFILE(file,str):
    with open(file,'w') as output:
        output.write(str)

def saveLISTtoFILE(file,list):
    s='\n'.join(list)
    with open(file,'w') as output:
        output.write(s)

def apitest():
    page =1
    global access_token
    with open('access_token.txt','r') as input:
        access_token = input.read()#将token格式化并添加到HTTP Header中
        headers={'Authorization': 'JWT'+access_token}

        while(True):
            try:
                r=requests.get(url='https://api.zoomeye.org/host/search?query="phpmyadmin"&facet=app,os&page=' + str(page),headers=headers)
                r_decypted=json.loads(r.text)
                print(r_decypted)#requests包里text将内容编码成字符串（ascII），content会出现b'标志
                for x in r_decypted['matches']:
                    print(x['ip'])
                    ip_list.append(x['ip'])
                print('pages:'+str(page*10))

            except Exception as e:
                if str(e.args)== 'matches':
                    print('API limit')
                    break
                else:
                    print('info：'+str(e.args))
            else:
                if page == 10:   #未捕捉到错误时，执行该块内容
                    break
                page +=1

def main():
    if not os.path.isfile('access_token.txt'):
        print('token not existed, please login')
        login()
        saveSTRtoFILE('access_token.txt',access_token)

    apitest()
    saveLISTtoFILE('ip_list.txt',ip_list)

if __name__ == '__main__':
    main()
