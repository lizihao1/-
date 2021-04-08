from passlib.hash import sha256_crypt as sha256
def verifypass(crypt):
    #salt = crypt[0:2].encode('utf-8') #截取头两个字节
    dictFile = open('dictionary.txt','r')
    for word in dictFile.readlines():
        word= word.strip('\n')
        #cryptword=bcrypt.hashpw(word,salt)#通过字典生成的密码
        cryptword=sha256.hash(word)
        print(cryptword)
        if(sha256.verify(crypt,cryptword)):
            print("passwd found: "+word)
            return
    print("passwd not found")
    return
def main():
    PassFile =  open('passwords.txt',encoding='utf-8')
    for line in PassFile.readlines():
        if ":" in line:
            user=line.split(":")[0] ##用户名为冒号分隔内容的第一部分
            cryptpass=line.split(":")[1].strip(' ')
            print("cracking passwd for user: " + user)
            verifypass(cryptpass)


if __name__ == '__main__':
    main()

