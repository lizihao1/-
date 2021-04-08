import requests
from lxml import etree
urls=['https://movie.douban.com/']
session = requests.session()
with session:
    for url in urls :
        response = session.get(url,headers={
          'User-agent':
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
        })
        content= response.text
        print(content)

        html = etree.HTML(content)
        titles= html.xpath("//div[@class='billboard-bd']//tr")
        for title in titles:
            txt=title.xpath('.//text()')
           # print(len(txt))
            print(''.join(map(lambda x: x.strip(), txt)))
            print('-'*30)



